"""Database and infrastructure domain exceptions."""

from __future__ import annotations

from app.domain.exceptions.base import InfrastructureException


class DatabaseConnectionException(InfrastructureException):
    """Raised when a database connection cannot be established."""

    def __init__(self) -> None:
        super().__init__("Unable to connect to the database.")


class DatabaseTransactionException(InfrastructureException):
    """Raised when a database transaction fails."""

    def __init__(self) -> None:
        super().__init__("The database transaction failed.")
