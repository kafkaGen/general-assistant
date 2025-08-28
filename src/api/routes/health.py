import time

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependency import get_logger
from src.api.schemas.health import HealthCheckResponse
from src.core.workflows import WorkflowFactory
from src.settings.services import api_settings
from src.utils.logger import Logger

router = APIRouter(
    prefix=f"/{api_settings.api_version}/health",
    tags=["Health"],
    responses={
        400: {"description": "Bad Request - Invalid input"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)


@router.get(
    "",  # Endpoint will be accessible at /health
    response_model=HealthCheckResponse,
    summary=f"{api_settings.api_name} Health Check",
    description=(
        "Checks if the API and its core dependencies are healthy "
        "and ready to process requests."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_api_health(
    logger: Logger = Depends(get_logger),
) -> HealthCheckResponse:
    """
    Provides the health status of the API.

    It checks if critical components like the GeneralAssistant can
    be initialized, which implies that its own dependencies
    were also set up correctly at application startup.
    """
    component_checks = {}
    overall_healthy = True

    # Check 1: GeneralAssistant instantiation
    try:
        # Attempt to create an instance of the workflow.
        _ = WorkflowFactory.create_general_assistant()
        component_checks["workflow_initialization"] = {"status": "healthy"}
    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        component_checks["workflow_initialization"] = {
            "status": "unhealthy",
            "error": error_details,
        }
        overall_healthy = False

        logger.error(
            f"Health Check Error: {error_details}",
            error_type=error_type,
            exc_info=True,
        )

    # Future: Add more checks here for other critical dependencies
    # (e.g., database connectivity, other external services) if they become
    #   part of your application.
    # For each new check, update `component_checks` and set `overall_healthy = False`
    #   on failure.

    response_payload = HealthCheckResponse(
        service_name=api_settings.api_name,
        status="healthy" if overall_healthy else "unhealthy",
        timestamp=time.time(),
        dependencies=component_checks,
    )

    if not overall_healthy:
        logger.warning(
            "API health check determined service is unhealthy. "
            f"Details: {component_checks}"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_payload.model_dump(),
        )

    return response_payload
