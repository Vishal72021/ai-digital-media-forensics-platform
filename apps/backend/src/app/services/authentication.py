"""Authentication service."""

from __future__ import annotations

from app.models.user import User
from app.repositories.user import UserRepository
from app.security.credential_service import CredentialService
from app.services.user import UserService


class AuthenticationService:
    """Coordinate authentication business workflows."""

    def __init__(
        self,
        *,
        user_service: UserService,
        credential_service: CredentialService,
        transaction_manager: UserRepository,
    ) -> None:
        """Initialize the authentication service.

        Args:
            user_service:
                User business service.

            credential_service:
                Password credential service.

            transaction_manager:
                Transaction owner responsible only for commit/rollback.
        """
        self._user_service = user_service
        self._credential_service = credential_service
        self._transaction_manager = transaction_manager

    def register(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        """Register a new user.

        Args:
            email:
                User email.

            password:
                Plaintext password.

        Returns:
            Newly created user.

        Raises:
            Any exception raised by the composed services.
        """
        user = User(email=email)

        try:
            created_user = self._user_service.create_user(user)

            self._credential_service.create(
                created_user.id,
                password,
            )

            self._transaction_manager.commit()

            return created_user

        except Exception:
            self._transaction_manager.rollback()
            raise
