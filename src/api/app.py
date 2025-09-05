from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, health
from src.core.workflows import GeneralAgent
from src.settings.services import api_settings
from src.utils.functions import get_agents_configuration
from src.utils.logger import create_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events using FastAPI's lifespan protocol.
    """

    logger = create_logger(
        "api",
        api_settings.console_log_level,
        api_settings.file_log_level,
    )
    app.state.logger = logger

    app.state.agents_configuration = get_agents_configuration()
    app.state.general_agent = GeneralAgent()

    logger.info(f"Starting up {api_settings.api_name} {api_settings.api_version}...")

    yield

    # --- Shutdown Logic ---

    logger.info(f"Shutting down {api_settings.api_name}...")


def create_app() -> FastAPI:
    """
    Application factory to create and configure the FastAPI application.
    """

    app = FastAPI(
        title=api_settings.api_name,
        description=api_settings.api_description,
        version=api_settings.api_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(health.router)

    return app


load_dotenv()
app = create_app()
