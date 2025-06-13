from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    service_name: str = Field(..., description="The name of the service")
    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="The health status of the service"
    )
    timestamp: float = Field(..., description="The timestamp of the health check")
    dependencies: dict[str, Any] = Field(
        ..., description="The health status of the dependencies"
    )
