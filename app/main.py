from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .seed_data import seed_models

from app.dependencies.database import db
from app.routes import execution, experiment, health, uploads, bedrock_config, config
from app.dependencies.database import (
    get_execution_model_invocations_db
)

def create_app() -> FastAPI:

    app = FastAPI(title="FloTorch Experiment API")

    # Initialize databases at startup
    @app.on_event("startup")
    async def startup_event():
        db.initialize()
        seed_models(get_execution_model_invocations_db())

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

    return app


app = create_app()
