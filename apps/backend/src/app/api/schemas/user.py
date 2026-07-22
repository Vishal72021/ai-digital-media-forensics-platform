"""User API schemas."""

from __future__ import annotations

from pydantic import EmailStr, Field

from app.api.schemas.common import (
    BaseSchema,
    IdentifierSchema,
    TimestampSchema,
)


class CreateUserRequest(BaseSchema):
    """Request schema for creating a user."""

    email: EmailStr = Field(
        ...,
        description="User email address.",
        max_length=320,
    )


class UpdateUserRequest(BaseSchema):
    """Request schema for updating a user."""

    email: EmailStr | None = Field(
        default=None,
        description="Updated user email address.",
        max_length=320,
    )


class UserSummary(IdentifierSchema):
    """Compact user representation."""

    email: EmailStr


class UserResponse(
    IdentifierSchema,
    TimestampSchema,
):
    """Full user representation returned by the API."""

    email: EmailStr
