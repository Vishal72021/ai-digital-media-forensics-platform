"""Base domain exception hierarchy."""

from __future__ import annotations


class DomainException(Exception):
    """Base class for all Sentinel AI domain exceptions."""


class BusinessRuleException(DomainException):
    """Raised when a business rule is violated."""


class ValidationException(DomainException):
    """Raised when domain validation fails."""


class ResourceNotFoundException(DomainException):
    """Raised when a requested domain resource does not exist."""


class ConflictException(DomainException):
    """Raised when a resource conflicts with existing state."""


class InfrastructureException(DomainException):
    """Raised when an infrastructure dependency fails."""
