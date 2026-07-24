"""User repository."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository responsible for user persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy database session.
        """
        self._session = session

    def create(self, user: User) -> User:
        """Persist a new user.

        Args:
            user: User entity to persist.

        Returns:
            The persisted user entity.
        """
        self._session.add(user)
        self._session.flush()
        self._session.refresh(user)

        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by its identifier.

        Args:
            user_id: User UUID.

        Returns:
            The matching user if found, otherwise ``None``.
        """
        statement = select(User).where(User.id == user_id)

        return cast(User | None, self._session.scalar(statement))

    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email address.

        Args:
            email: User email.

        Returns:
            The matching user if found, otherwise ``None``.
        """
        statement = select(User).where(User.email == email)

        return cast(User | None, self._session.scalar(statement))

    def list(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[User]:
        """Return a paginated list of users.

        Args:
            offset: Number of users to skip.
            limit: Maximum number of users to return.

        Returns:
            Paginated list of users ordered by creation time.
        """
        statement = select(User).order_by(User.created_at).offset(offset).limit(limit)

        return cast(list[User], list(self._session.scalars(statement)))

    def count(self) -> int:
        """Return the total number of users.

        Returns:
            Total number of persisted users.
        """
        statement = select(func.count()).select_from(User)

        result = self._session.scalar(statement)

        return 0 if result is None else result

    def delete(self, user: User) -> None:
        """Mark a user for deletion.

        Args:
            user: User entity to delete.
        """
        self._session.delete(user)
        self._session.flush()

    def commit(self) -> None:
        """Commit the current transaction."""
        self._session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self._session.rollback()

    def flush(self) -> None:
        """Flush pending changes to the database."""
        self._session.flush()
