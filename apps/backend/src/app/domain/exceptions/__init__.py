"""Domain exceptions."""

from app.domain.exceptions.base import (
    BusinessRuleException,
    ConflictException,
    DomainException,
    InfrastructureException,
    ResourceNotFoundException,
    ValidationException,
)
from app.domain.exceptions.database import (
    DatabaseConnectionException,
    DatabaseTransactionException,
)
from app.domain.exceptions.security import (
    AuthenticationException,
    InvalidCredentialsException,
    PasswordPolicyViolation,
)
from app.domain.exceptions.users import (
    DuplicateEmailException,
    UserNotFoundException,
)

__all__ = [
    "BusinessRuleException",
    "ConflictException",
    "DomainException",
    "DuplicateEmailException",
    "InfrastructureException",
    "ResourceNotFoundException",
    "UserNotFoundException",
    "ValidationException",
    "DatabaseConnectionException",
    "DatabaseTransactionException",
    "AuthenticationException",
    "InvalidCredentialsException",
    "PasswordPolicyViolation",
]
