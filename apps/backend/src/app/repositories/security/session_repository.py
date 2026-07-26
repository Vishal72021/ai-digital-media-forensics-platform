"""Authentication session persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.authentication_session import AuthenticationSession
from app.models.refresh_credential import RefreshCredential


class SessionRepository:
    """Provides persistence operations for authentication session state."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_session(
        self,
        authentication_session: AuthenticationSession,
    ) -> AuthenticationSession:
        """Add an authentication session to the current transaction."""
        self._session.add(authentication_session)
        return authentication_session

    def add_refresh_credential(
        self,
        credential: RefreshCredential,
    ) -> RefreshCredential:
        """Add a refresh credential to the current transaction."""
        self._session.add(credential)
        return credential

    def get_session_by_id(
        self,
        session_id: UUID,
    ) -> AuthenticationSession | None:
        """Return an authentication session by identifier."""
        return self._session.get(AuthenticationSession, session_id)

    def get_refresh_by_selector(
        self,
        selector: str,
    ) -> RefreshCredential | None:
        """Return a refresh credential by its public selector."""
        statement = select(RefreshCredential).where(RefreshCredential.selector == selector)
        return self._session.scalar(statement)
