from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .seed_data import seed_models

from app.routes import execution, experiment, health, uploads, bedrock_config, config, expert_eval
from app.dependencies.database import (
    get_execution_model_invocations_db
)

def create_app() -> FastAPI:

    app = FastAPI(title="FloTorch Experiment API")

    # Initialize databases at startup
    @app.on_event("startup")
    async def startup_event():
        try:
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

    # Register routers
    app.include_router(uploads.router)
    app.include_router(execution.router)
    app.include_router(experiment.router)
    app.include_router(health.router)
    app.include_router(bedrock_config.router)
    app.include_router(config.router)
    app.include_router(expert_eval.router)

    return app


app = create_app()
