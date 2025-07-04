from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.general_assistant.api.routes import chat, health
from src.general_assistant.config.logger import create_logger, loguru_logger
from src.general_assistant.config.settings import settings
from src.general_assistant.core.workflows import GeneralAssistantWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events using FastAPI's lifespan protocol.
    """

    logger = create_logger("application", settings.api.log_level)

    general_assistant_workflow = GeneralAssistantWorkflow(
        settings=settings.workflows,
    )
    app.state.general_assistant_workflow = general_assistant_workflow

    logger.info(f"Starting up {settings.api.api_name} {settings.api.api_version}...")

    yield

    # --- Shutdown Logic ---

    logger.info(f"Shutting down {settings.api.api_name}...")

    # remove all loguru handlers
    loguru_logger.remove()


def create_app() -> FastAPI:
    """
    Application factory to create and configure the FastAPI application.
    """

    app = FastAPI(
        title=settings.api.api_name,
        description=settings.api.api_description,
        version=settings.api.api_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(health.router)

    return app


app = create_app()
