"""Security domain exceptions."""

from app.domain.exceptions.base import ValidationException


class PasswordPolicyViolation(ValidationException):
    """Raised when a candidate password violates the canonical password policy."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
