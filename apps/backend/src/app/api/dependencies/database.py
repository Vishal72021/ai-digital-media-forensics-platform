"""Database dependency providers."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db_session() -> Generator[Session]:
    """Provide a request-scoped SQLAlchemy session.

    Yields:
        An active SQLAlchemy session.

    Ensures:
        The session is closed after the request completes.
    """
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
