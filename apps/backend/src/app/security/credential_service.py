"""Password credential lifecycle orchestration."""

from __future__ import annotations

from uuid import UUID

from app.domain.security.password_policy import PasswordPolicy
from app.models.password_credential import PasswordCredential
from app.repositories.security.credential_repository import CredentialRepository
from app.security.password_hasher import PasswordHasher


class CredentialService:
    """Coordinate password credential creation and verification."""

    def __init__(
        self,
        repository: CredentialRepository,
        password_policy: PasswordPolicy,
        password_hasher: PasswordHasher,
    ) -> None:
        """Initialize the credential service."""
        self._repository = repository
        self._password_policy = password_policy
        self._password_hasher = password_hasher

    def create(self, user_id: UUID, password: str) -> PasswordCredential:
        """Create a password credential within the current transaction.

        Args:
            user_id: Identifier of the user receiving the credential.
            password: Candidate plaintext password.

        Returns:
            The password credential added to the current transaction.
        """
        self._password_policy.validate(password)
        password_hash = self._password_hasher.hash(password)

        credential = PasswordCredential(
            user_id=user_id,
            password_hash=password_hash,
        )

        return self._repository.add(credential)

    def verify(self, user_id: UUID, password: str) -> bool:
        """Verify password material against a user's stored credential.

        Args:
            user_id: Identifier of the user whose credential is verified.
            password: Supplied plaintext password.

        Returns:
            True when a stored credential exists and the password matches.
        """
        credential = self._repository.get_by_user_id(user_id)

        if credential is None:
            return False

        return self._password_hasher.verify(
            password,
            credential.password_hash,
        )
