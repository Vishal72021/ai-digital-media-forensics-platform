"""Database session factory."""

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import create_database_engine

engine = create_database_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
