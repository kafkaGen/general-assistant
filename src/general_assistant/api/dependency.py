from fastapi import Request

from src.general_assistant.core.workflows import GeneralAssistantWorkflow


def get_workflow(request: Request) -> GeneralAssistantWorkflow:
    """
    Dependency to retrieve the singleton GeneralAssistantWorkflow instance from
    the app state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The shared GeneralAssistantWorkflow instance.
    """
    return request.app.state.general_assistant_workflow
