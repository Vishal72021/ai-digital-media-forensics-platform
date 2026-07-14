"""User service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.user import UserRepository


class UserService:
    """Service responsible for user-related business operations."""

    def __init__(
        self,
        session: Session,
        repository: UserRepository | None = None,
    ) -> None:
        """Initialize the user service.

        Args:
            session: SQLAlchemy database session.
            repository: Optional repository implementation.
        """
        self._session = session
        self._repository = repository or UserRepository(session)
