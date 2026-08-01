"""Verification for service dependency providers."""

from unittest.mock import Mock

from app.api.dependencies.services import (
    get_authentication_service,
    get_password_hasher,
    get_password_policy,
)
from app.core.config import get_settings
from app.domain.security.password_policy import PasswordPolicy
from app.services.authentication import AuthenticationService


def test_get_authentication_service_returns_authentication_service() -> None:
    """Dependency provider constructs the authentication service."""

    user_service = Mock()
    credential_service = Mock()
    transaction_manager = Mock()

    service = get_authentication_service(
        user_service=user_service,
        credential_service=credential_service,
        user_repository=transaction_manager,
    )

    assert isinstance(service, AuthenticationService)


def test_get_authentication_service_wires_dependencies() -> None:
    """Dependency provider injects the expected collaborators."""

    user_service = Mock()
    credential_service = Mock()
    transaction_manager = Mock()

    service = get_authentication_service(
        user_service=user_service,
        credential_service=credential_service,
        user_repository=transaction_manager,
    )

    assert service._user_service is user_service
    assert service._credential_service is credential_service
    assert service._transaction_manager is transaction_manager


def test_get_password_policy_returns_password_policy() -> None:
    """Password policy provider returns a policy instance."""

    policy = get_password_policy()

    assert isinstance(policy, PasswordPolicy)


def test_get_password_policy_is_not_cached() -> None:
    """Password policy provider returns a new instance."""

    assert get_password_policy() is not get_password_policy()


def test_get_password_hasher_uses_application_settings(monkeypatch) -> None:
    """Password hasher composition honors application configuration."""

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost/test",
    )
    monkeypatch.setenv("PASSWORD_HASH_TIME_COST", "4")
    monkeypatch.setenv("PASSWORD_HASH_MEMORY_COST", "32768")
    monkeypatch.setenv("PASSWORD_HASH_PARALLELISM", "2")
    monkeypatch.setenv("PASSWORD_HASH_HASH_LEN", "24")
    monkeypatch.setenv("PASSWORD_HASH_SALT_LEN", "12")

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        hasher = get_password_hasher()
        encoded_hash = hasher.hash("correct horse battery staple")

        assert encoded_hash.startswith("$argon2id$v=19$m=32768,t=4,p=2$")
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()


def test_get_password_hasher_preserves_verification_behavior(
    monkeypatch,
) -> None:
    """Configured dependency produces a functional password hasher."""

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost/test",
    )
    monkeypatch.setenv("PASSWORD_HASH_TIME_COST", "4")
    monkeypatch.setenv("PASSWORD_HASH_MEMORY_COST", "32768")
    monkeypatch.setenv("PASSWORD_HASH_PARALLELISM", "2")
    monkeypatch.setenv("PASSWORD_HASH_HASH_LEN", "24")
    monkeypatch.setenv("PASSWORD_HASH_SALT_LEN", "12")

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        hasher = get_password_hasher()
        password = "correct horse battery staple"

        encoded_hash = hasher.hash(password)

        assert hasher.verify(password, encoded_hash) is True
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()


def test_get_password_hasher_returns_cached_instance(
    monkeypatch,
) -> None:
    """Password hasher composition reuses the configured singleton instance."""

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost/test",
    )

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        first = get_password_hasher()
        second = get_password_hasher()

        assert first is second
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()


def test_get_password_hasher_supports_configured_dummy_verification(
    monkeypatch,
) -> None:
    """Configured dependency keeps dummy verification operational."""

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost/test",
    )

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        hasher = get_password_hasher()

        assert hasher.verify_dummy("supplied password") is None
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()
