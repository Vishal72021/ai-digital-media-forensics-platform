"""Password recovery capability persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_recovery_token import PasswordRecoveryToken


class PasswordRecoveryRepository:
    """Provides persistence operations for password recovery capabilities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        token: PasswordRecoveryToken,
    ) -> PasswordRecoveryToken:
        """Add a password recovery capability to the current transaction."""
        self._session.add(token)
        return token

    def get_by_digest(
        self,
        token_digest: str,
    ) -> PasswordRecoveryToken | None:
        """Return a password recovery capability by its stored digest."""
        statement = select(PasswordRecoveryToken).where(
            PasswordRecoveryToken.token_digest == token_digest
        )
        return self._session.scalar(statement)

    def list_outstanding_for_user(
        self,
        user_id: UUID,
    ) -> list[PasswordRecoveryToken]:
        """Return unconsumed and unrevoked recovery capabilities for a user."""
        statement = select(PasswordRecoveryToken).where(
            PasswordRecoveryToken.user_id == user_id,
            PasswordRecoveryToken.consumed_at.is_(None),
            PasswordRecoveryToken.revoked_at.is_(None),
        )
        return list(self._session.scalars(statement).all())
