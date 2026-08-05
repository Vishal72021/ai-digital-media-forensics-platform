"""Authentication API schemas."""

from __future__ import annotations

from pydantic import EmailStr, Field

from app.api.schemas.common import BaseSchema


class RegisterUserRequest(BaseSchema):
    """Request schema for user registration."""

    email: EmailStr = Field(
        ...,
        description="User email address.",
        max_length=320,
    )

    password: str = Field(
        ...,
        description="Plaintext password.",
    )
