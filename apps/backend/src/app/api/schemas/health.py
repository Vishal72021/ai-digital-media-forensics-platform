"""Health API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.api.schemas.common import BaseSchema
from app.api.schemas.enums import Environment, HealthStatus


class HealthResponse(BaseSchema):
    """Application health response."""

    status: HealthStatus = Field(
        description="Overall application health status.",
    )

    version: str = Field(
        description="Application version.",
        examples=["0.3.0"],
    )

    environment: Environment = Field(
        description="Current runtime environment.",
    )

    timestamp: datetime = Field(
        description="Time when the health check was generated.",
    )


class LivenessResponse(BaseSchema):
    """Liveness probe response."""

    status: HealthStatus = Field(
        description="Liveness status.",
    )


class ReadinessResponse(BaseSchema):
    """Readiness probe response."""

    status: HealthStatus = Field(
        description="Readiness status.",
    )
