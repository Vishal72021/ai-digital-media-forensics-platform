"""Verification for service dependency providers."""

from app.api.dependencies.services import get_password_hasher
from app.core.config import get_settings


def test_get_password_hasher_uses_application_settings(monkeypatch) -> None:
    """Password hasher composition honors application configuration."""

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
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


def test_get_password_hasher_preserves_verification_behavior(monkeypatch) -> None:
    """Configured dependency produces a functional password hasher."""

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
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


def test_get_password_hasher_returns_cached_instance(monkeypatch) -> None:
    """Password hasher composition reuses the configured singleton instance."""

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        first_hasher = get_password_hasher()
        second_hasher = get_password_hasher()

        assert first_hasher is second_hasher
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()


def test_get_password_hasher_supports_configured_dummy_verification(monkeypatch) -> None:
    """Configured dependency keeps anti-enumeration verification operational."""

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    monkeypatch.setenv("PASSWORD_HASH_TIME_COST", "4")
    monkeypatch.setenv("PASSWORD_HASH_MEMORY_COST", "32768")
    monkeypatch.setenv("PASSWORD_HASH_PARALLELISM", "2")
    monkeypatch.setenv("PASSWORD_HASH_HASH_LEN", "24")
    monkeypatch.setenv("PASSWORD_HASH_SALT_LEN", "12")

    get_settings.cache_clear()
    get_password_hasher.cache_clear()

    try:
        hasher = get_password_hasher()

        result = hasher.verify_dummy("supplied password material")

        assert result is None
    finally:
        get_password_hasher.cache_clear()
        get_settings.cache_clear()
