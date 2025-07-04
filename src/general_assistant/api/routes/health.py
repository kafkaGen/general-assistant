import time

from fastapi import APIRouter, HTTPException, status

from src.general_assistant.api.schemas.health_schemas import HealthCheckResponse
from src.general_assistant.config.logger import create_logger
from src.general_assistant.config.settings import settings
from src.general_assistant.core.workflows import GeneralAssistantWorkflow

logger = create_logger("health_api", settings.api.log_level)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",  # Endpoint will be accessible at /health
    response_model=HealthCheckResponse,
    summary=f"{settings.api.api_name} Health Check",
    description=(
        "Checks if the API and its core dependencies are healthy "
        "and ready to process requests."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_api_health() -> HealthCheckResponse:
    """
    Provides the health status of the API.

    It checks if critical components like the GeneralAssistantWorkflow can
    be initialized, which implies that its own dependencies (e.g., LLM provider)
    were also set up correctly at application startup.
    """
    component_checks = {}
    overall_healthy = True

    # Check 1: GeneralAssistantWorkflow instantiation
    try:
        # Attempt to create an instance of the workflow.
        # This tests if:
        # 1. The GeneralAssistantWorkflow class and its module were imported
        #    successfully (meaning class-level dependencies like the LLM
        #    provider were initialized without error).
        # 2. An instance can be created (its __init__ logic is sound).
        _ = GeneralAssistantWorkflow(settings=settings.workflows)
        component_checks["workflow_initialization"] = {"status": "healthy"}
    except Exception as e:
        error_message = f"Workflow initialization failed: {type(e).__name__} - {str(e)}"
        logger.error(f"Health Check Error: {error_message}", exc_info=True)
        component_checks["workflow_initialization"] = {
            "status": "unhealthy",
            "error": error_message,
        }
        overall_healthy = False

    # Future: Add more checks here for other critical dependencies
    # (e.g., database connectivity, other external services) if they become
    #   part of your application.
    # For each new check, update `component_checks` and set `overall_healthy = False`
    #   on failure.

    response_payload = HealthCheckResponse(
        service_name=settings.api.api_name,
        status="healthy" if overall_healthy else "unhealthy",
        timestamp=time.time(),
        dependencies=component_checks,
    )

    if not overall_healthy:
        logger.warning(
            "API health check determined service is unhealthy. "
            f"Details: {component_checks}"
        )
        # Return HTTP 503 if not healthy, including the detailed status in
        #   the response body.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_payload,
        )

    logger.debug(
        "API health check successful."
    )  # Use debug for successful checks to reduce log noise
    return response_payload
