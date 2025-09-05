from fastapi import Request

from src.core.workflows import GeneralAgent
from src.utils.logger import Logger


def get_logger(request: Request) -> Logger:
    """
    Dependency to retrieve the logger instance from the app state.
    """
    return request.app.state.logger


def get_agents_configuration(request: Request) -> dict:
    """
    Dependency to retrieve the agents configuration instance from the app state.
    """
    return request.app.state.agents_configuration


def get_general_agent(request: Request) -> GeneralAgent:
    """
    Dependency to retrieve the singleton GeneralAgent instance from
    the app state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The shared GeneralAgent instance.
    """
    return request.app.state.general_agent
