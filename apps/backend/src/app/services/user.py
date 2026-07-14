"""User service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
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

    def create_user(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to persist.

        Returns:
            The persisted user entity.
        """
        created_user = self._repository.create(user)
        self._session.commit()

        return created_user

    def get_user(self, user_id: UUID) -> User | None:
        """Retrieve a user by identifier."""
        return self._repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        return self._repository.get_by_email(email)

    def list_users(self) -> list[User]:
        """Return all users."""
        return self._repository.list()

    def delete_user(self, user: User) -> None:
        """Delete a user."""
        self._repository.delete(user)
        self._session.commit()
