"""User service."""

from __future__ import annotations

from uuid import UUID

from app.domain.exceptions import (
    DuplicateEmailException,
    UserNotFoundException,
)
from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    """Service responsible for user-related business operations."""

    def __init__(self, repository: UserRepository) -> None:
        """Initialize the user service.

        Args:
            repository: Repository used for user persistence operations.
        """
        self._repository = repository

    def create_user(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to persist.

        Returns:
            The persisted user entity.

        Raises:
            DuplicateEmailException:
                If a user with the same email already exists.
        """
        existing_user = self._repository.get_by_email(user.email)

        if existing_user is not None:
            raise DuplicateEmailException(user.email)

        created_user = self._repository.create(user)
        self._repository.commit()

        return created_user

    def get_user(self, user_id: UUID) -> User:
        """Retrieve a user by identifier.

        Args:
            user_id: Unique identifier of the user.

        Returns:
            The requested user.

        Raises:
            UserNotFoundException:
                If the user does not exist.
        """
        user = self._repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundException(user_id)

        return user

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email.

        Args:
            email: User email address.

        Returns:
            The matching user if found; otherwise ``None``.
        """
        return self._repository.get_by_email(email)

    def list_users(
        self,
        *,
        page: int,
        page_size: int,
    ) -> list[User]:
        """Return a paginated list of users.

        Args:
            offset: Number of users to skip.
            limit: Maximum number of users to return.

        Returns:
            Paginated list of users.
        """
        offset = (page - 1) * page_size

        return self._repository.list(
            offset=offset,
            limit=page_size,
        )

    def delete_user(self, user_id: UUID) -> None:
        """Delete a user.

        Args:
            user_id: Unique identifier of the user.

        Raises:
            UserNotFoundException:
                If the user does not exist.
        """
        user = self.get_user(user_id)

        self._repository.delete(user)
        self._repository.commit()
