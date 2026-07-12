"""Platform health endpoints."""

from fastapi import APIRouter

from app.schemas.health import HealthStatus, HealthStatusResponse

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    response_model=HealthStatusResponse,
)
def get_health() -> HealthStatusResponse:
    """Return the overall application health."""

    return HealthStatusResponse(
        status=HealthStatus.HEALTHY,
    )


@health_router.get(
    "/live",
    response_model=HealthStatusResponse,
)
def get_liveness() -> HealthStatusResponse:
    """Return the application liveness state."""

    return HealthStatusResponse(
        status=HealthStatus.HEALTHY,
    )


@health_router.get(
    "/ready",
    response_model=HealthStatusResponse,
)
def get_readiness() -> HealthStatusResponse:
    """Return the application readiness state."""

    return HealthStatusResponse(
        status=HealthStatus.HEALTHY,
    )
