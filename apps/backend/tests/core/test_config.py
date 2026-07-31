"""Verification for application configuration contracts."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_password_hash_settings_use_approved_defaults() -> None:
    """Password hashing settings expose the approved Argon2id defaults."""

    settings = Settings(
        database_url="postgresql+psycopg://user:password@localhost:5432/test",
    )

    assert settings.password_hash_time_cost == 3
    assert settings.password_hash_memory_cost == 65536
    assert settings.password_hash_parallelism == 4
    assert settings.password_hash_hash_len == 32
    assert settings.password_hash_salt_len == 16


def test_password_hash_settings_accept_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Password hashing parameters can be overridden through the environment."""

    monkeypatch.setenv("PASSWORD_HASH_TIME_COST", "4")
    monkeypatch.setenv("PASSWORD_HASH_MEMORY_COST", "131072")
    monkeypatch.setenv("PASSWORD_HASH_PARALLELISM", "2")
    monkeypatch.setenv("PASSWORD_HASH_HASH_LEN", "48")
    monkeypatch.setenv("PASSWORD_HASH_SALT_LEN", "24")

    settings = Settings(
        database_url="postgresql+psycopg://user:password@localhost:5432/test",
    )

    assert settings.password_hash_time_cost == 4
    assert settings.password_hash_memory_cost == 131072
    assert settings.password_hash_parallelism == 2
    assert settings.password_hash_hash_len == 48
    assert settings.password_hash_salt_len == 24


@pytest.mark.parametrize(
    "environment_variable",
    [
        "PASSWORD_HASH_TIME_COST",
        "PASSWORD_HASH_MEMORY_COST",
        "PASSWORD_HASH_PARALLELISM",
        "PASSWORD_HASH_HASH_LEN",
        "PASSWORD_HASH_SALT_LEN",
    ],
)
@pytest.mark.parametrize("invalid_value", ["0", "-1"])
def test_password_hash_settings_reject_non_positive_values(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable: str,
    invalid_value: str,
) -> None:
    """Password hashing parameters reject zero and negative values."""

    monkeypatch.setenv(environment_variable, invalid_value)

    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql+psycopg://user:password@localhost:5432/test",
        )


@pytest.mark.parametrize(
    "environment_variable",
    [
        "PASSWORD_HASH_TIME_COST",
        "PASSWORD_HASH_MEMORY_COST",
        "PASSWORD_HASH_PARALLELISM",
        "PASSWORD_HASH_HASH_LEN",
        "PASSWORD_HASH_SALT_LEN",
    ],
)
def test_password_hash_settings_reject_non_integer_values(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable: str,
) -> None:
    """Password hashing parameters reject non-integer values."""

    monkeypatch.setenv(environment_variable, "invalid")

    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql+psycopg://user:password@localhost:5432/test",
        )
