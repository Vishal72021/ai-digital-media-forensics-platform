"""Repository dependency providers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db_session
from app.repositories.user import UserRepository


def get_user_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> UserRepository:
    """Provide a user repository.

    Args:
        session: Request-scoped database session.

    Returns:
        User repository bound to the current database session.
    """
    return UserRepository(session)


UserRepositoryDependency = Annotated[
    UserRepository,
    Depends(get_user_repository),
]
