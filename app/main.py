from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from .seed_data import seed_models
from .validation import log_core_version, validate_base_config, log_validation_warnings

from app.routes import execution, experiment, health, uploads, bedrock_config, config, expert_eval, migration, cutover, cleanup, opensearch_admin
from app.dependencies.database import (
    get_execution_model_invocations_db
)
from app.database import init_database

def create_app() -> FastAPI:

    app = FastAPI(title="FloTorch Experiment API")

    # Initialize databases at startup
    @app.on_event("startup")
    async def startup_event():
        try:
            # Observability-only: core version + config validation (warnings only)
            log_core_version()
            warnings = validate_base_config()
            # In LOCAL_DEV, always just warn. In other envs, still warn only to avoid behavior changes.
            log_validation_warnings(warnings)
            
            # Initialize PostgreSQL database if enabled
            if os.getenv("DB_TYPE", "DYNAMODB").upper() == "POSTGRESDB":
                try:
                    init_database()
                    print("PostgreSQL database initialized successfully")
                except Exception as e:
                    print(f"PostgreSQL initialization failed: {e}")
                    # Continue startup even if PostgreSQL init fails

            if os.getenv("SKIP_SEEDING", "false").lower() != "true":
                db_client_generator = get_execution_model_invocations_db()
                db_client = None
                try:
                    db_client = next(db_client_generator)
                    seeded_count = seed_models(db_client)
                except StopIteration:
                    print("Generator did not yield a DB client during startup.")
                except Exception as e:
                    print(f"Error during seeding process: {e}")
                finally:
                    if db_client_generator:
                        try:
                            db_client_generator.close()
                        except Exception as e:
                            print(f"Error closing DB client generator during startup: {e}")

            print("Application startup tasks finished.")

        except Exception as e:
            print(f"FATAL: Error during application startup event: {e}")
            

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers with /api prefix
    app.include_router(uploads.router, prefix="/api")
    app.include_router(execution.router, prefix="/api")
    app.include_router(experiment.router, prefix="/api")
    app.include_router(health.router, prefix="/api")
    app.include_router(bedrock_config.router, prefix="/api")
    app.include_router(config.router, prefix="/api")
    app.include_router(expert_eval.router, prefix="/api")
    app.include_router(migration.router, prefix="/api")
    app.include_router(cutover.router, prefix="/api")
    app.include_router(cleanup.router, prefix="/api")
    app.include_router(opensearch_admin.router, prefix="/api")

    return app


app = create_app()
