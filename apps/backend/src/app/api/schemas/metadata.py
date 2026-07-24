"""Shared metadata schemas."""

from __future__ import annotations

from pydantic import Field

from app.api.schemas.common import BaseSchema
from app.api.schemas.enums import Environment


class ApplicationMetadata(BaseSchema):
    """Application metadata shared across API responses."""

    version: str = Field(
        description="Application version.",
        examples=["0.3.0"],
    )

    environment: Environment = Field(
        description="Current runtime environment.",
    )
