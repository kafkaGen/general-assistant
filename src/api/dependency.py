from fastapi import Request

from src.core.workflows import GeneralAssistant
from src.utils.logger import Logger


def get_general_assistant(request: Request) -> GeneralAssistant:
    """
    Dependency to retrieve the singleton GeneralAssistant instance from
    the app state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The shared GeneralAssistant instance.
    """
    return request.app.state.general_assistant


def get_logger(request: Request) -> Logger:
    """
    Dependency to retrieve the logger instance from the app state.
    """
    return request.app.state.logger
