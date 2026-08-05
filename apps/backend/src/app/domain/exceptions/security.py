"""Security domain exceptions."""

from __future__ import annotations

from app.domain.exceptions.base import (
    BusinessRuleException,
    ValidationException,
)


class AuthenticationException(BusinessRuleException):
    """Base class for authentication domain failures."""


class InvalidCredentialsException(AuthenticationException):
    """Raised when supplied authentication credentials are invalid."""

    def __init__(self) -> None:
        super().__init__("The supplied credentials are invalid.")


class PasswordPolicyViolation(ValidationException):
    """Raised when a candidate password violates the canonical password policy."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
