"""Service dependency providers."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db_session
from app.api.dependencies.repositories import get_user_repository
from app.core.config import get_settings
from app.domain.security.password_policy import PasswordPolicy
from app.repositories.security.credential_repository import CredentialRepository
from app.repositories.user import UserRepository
from app.security.credential_service import CredentialService
from app.security.password_hasher import PasswordHasher
from app.services.authentication import AuthenticationService
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


def get_password_policy() -> PasswordPolicy:
    """Provide the password policy."""

    return PasswordPolicy()


def get_credential_repository(
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> CredentialRepository:
    """Provide a credential repository.

    Args:
        session: Request-scoped database session.

    Returns:
        Credential repository configured with its database session.
    """
    return CredentialRepository(session)


def get_user_service(
    repository: Annotated[
        UserRepository,
        Depends(get_user_repository),
    ],
) -> UserService:
    """Provide a user service."""

    return UserService(repository)


def get_credential_service(
    repository: Annotated[
        CredentialRepository,
        Depends(get_credential_repository),
    ],
    password_policy: Annotated[
        PasswordPolicy,
        Depends(get_password_policy),
    ],
    password_hasher: Annotated[
        PasswordHasher,
        Depends(get_password_hasher),
    ],
) -> CredentialService:
    """Provide a credential service."""

    return CredentialService(
        repository=repository,
        password_policy=password_policy,
        password_hasher=password_hasher,
    )


def get_authentication_service(
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
    credential_service: Annotated[
        CredentialService,
        Depends(get_credential_service),
    ],
    user_repository: Annotated[
        UserRepository,
        Depends(get_user_repository),
    ],
) -> AuthenticationService:
    """Provide the authentication service."""

    return AuthenticationService(
        user_service=user_service,
        credential_service=credential_service,
        transaction_manager=user_repository,
    )


PasswordHasherDependency = Annotated[
    PasswordHasher,
    Depends(get_password_hasher),
]

PasswordPolicyDependency = Annotated[
    PasswordPolicy,
    Depends(get_password_policy),
]

CredentialServiceDependency = Annotated[
    CredentialService,
    Depends(get_credential_service),
]

UserServiceDependency = Annotated[
    UserService,
    Depends(get_user_service),
]

AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]
