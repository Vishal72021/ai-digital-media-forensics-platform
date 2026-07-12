"""Health endpoint response schemas."""

from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    """Supported application health states."""

    HEALTHY = "healthy"


class HealthStatusResponse(BaseModel):
    """Response returned by platform health endpoints."""

    status: HealthStatus
