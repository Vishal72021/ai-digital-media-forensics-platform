"""Shared API enumerations."""

from __future__ import annotations

from enum import StrEnum


class HealthStatus(StrEnum):
    """Application health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SortOrder(StrEnum):
    """Sorting direction."""

    ASC = "asc"
    DESC = "desc"


class Environment(StrEnum):
    """Application runtime environment."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
