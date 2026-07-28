"""Email verification capability persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken


class EmailVerificationRepository:
    """Provides persistence operations for email verification capabilities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:
        """Add an email verification capability to the current transaction."""
        self._session.add(token)
        return token

    def get_by_digest(
        self,
        token_digest: str,
    ) -> EmailVerificationToken | None:
        """Return an email verification capability by its stored digest."""
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.token_digest == token_digest
        )
        return self._session.scalar(statement)

    def list_outstanding_for_user(
        self,
        user_id: UUID,
    ) -> list[EmailVerificationToken]:
        """Return unconsumed and unrevoked verification capabilities for a user."""
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.consumed_at.is_(None),
            EmailVerificationToken.revoked_at.is_(None),
        )
        return list(self._session.scalars(statement).all())
