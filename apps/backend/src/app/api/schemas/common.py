"""Shared API schema definitions."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base class for all API schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True,
    )


class IdentifierSchema(BaseSchema):
    """Schema containing an immutable identifier."""

    id: UUID


class TimestampSchema(BaseSchema):
    """Schema containing creation and update timestamps."""

    created_at: datetime
    updated_at: datetime
