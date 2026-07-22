"""Service dependency providers."""

from typing import Annotated

from fastapi import Depends

from app.api.dependencies.repositories import get_user_repository
from app.repositories.user import UserRepository
from app.services.user import UserService


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Provide a user service.

    Args:
        repository: Request-scoped user repository.

    Returns:
        User service configured with its repository dependency.
    """
    return UserService(repository)
