"""User domain exceptions."""

from __future__ import annotations

from uuid import UUID

from app.domain.exceptions.base import (
    ConflictException,
    ResourceNotFoundException,
)


class UserNotFoundException(ResourceNotFoundException):
    """Raised when a user cannot be found."""

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User '{user_id}' was not found.")


class DuplicateEmailException(ConflictException):
    """Raised when an email address is already in use."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Email '{email}' is already registered.")
