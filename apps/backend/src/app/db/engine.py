"""Database engine configuration."""

from sqlalchemy import Engine, create_engine

from app.core.config import get_settings


def create_database_engine() -> Engine:
    """Create the SQLAlchemy database engine.

    Returns:
        Configured SQLAlchemy engine.
    """
    settings = get_settings()

    return create_engine(
        settings.database_url,
        future=True,
    )
