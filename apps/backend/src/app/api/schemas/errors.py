"""API error schemas."""

from __future__ import annotations

from pydantic import Field, HttpUrl

from app.api.schemas.common import BaseSchema


class ProblemDetails(BaseSchema):
    """RFC 9457 Problem Details."""

    type: HttpUrl = Field(
        description="URI identifying the problem type.",
    )

    title: str = Field(
        description="Short human-readable summary.",
    )

    status: int = Field(
        ge=100,
        le=599,
        description="HTTP status code.",
    )

    detail: str = Field(
        description="Detailed explanation of the problem.",
    )

    instance: str | None = Field(
        default=None,
        description="URI identifying this specific occurrence.",
    )


class ValidationErrorDetail(BaseSchema):
    """Validation error for a single field."""

    field: str

    message: str


class ValidationProblemDetails(ProblemDetails):
    """Problem details for validation failures."""

    errors: list[ValidationErrorDetail]
