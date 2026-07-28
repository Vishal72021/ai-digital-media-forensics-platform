"""Password credential persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_credential import PasswordCredential


class CredentialRepository:
    """Provides persistence operations for password credentials."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, credential: PasswordCredential) -> PasswordCredential:
        """Add a password credential to the current transaction."""
        self._session.add(credential)
        return credential

    def get_by_user_id(self, user_id: UUID) -> PasswordCredential | None:
        """Return the password credential belonging to a user."""
        statement = select(PasswordCredential).where(PasswordCredential.user_id == user_id)
        return self._session.scalar(statement)
