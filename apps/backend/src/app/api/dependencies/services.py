"""Service dependency providers."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.repositories import get_user_repository
from app.core.config import get_settings
from app.repositories.user import UserRepository
from app.security.password_hasher import PasswordHasher
from app.services.user import UserService


@lru_cache
def get_password_hasher() -> PasswordHasher:
    """Provide the configured password hashing primitive.

    Returns:
        Cached password hasher configured from application settings.
    """
    settings = get_settings()

    return PasswordHasher(
        time_cost=settings.password_hash_time_cost,
        memory_cost=settings.password_hash_memory_cost,
        parallelism=settings.password_hash_parallelism,
        hash_len=settings.password_hash_hash_len,
        salt_len=settings.password_hash_salt_len,
    )


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


PasswordHasherDependency = Annotated[
    PasswordHasher,
    Depends(get_password_hasher),
]

UserServiceDependency = Annotated[
    UserService,
    Depends(get_user_service),
]
