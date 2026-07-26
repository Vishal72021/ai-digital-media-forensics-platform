"""Persistence metadata verification for the Wave 4 security foundation."""

from __future__ import annotations

from sqlalchemy import Table

import app.models  # noqa: F401
from app.db.base import Base

EXPECTED_SECURITY_TABLES = {
    "authentication_sessions",
    "email_verification_tokens",
    "password_credentials",
    "password_recovery_tokens",
    "permissions",
    "refresh_credentials",
    "role_permissions",
    "roles",
    "user_roles",
    "users",
}

FORBIDDEN_SECRET_COLUMNS = {
    "raw_credential",
    "raw_token",
    "recovery_token",
    "refresh_token",
    "secret",
    "token",
    "verification_token",
}


def _table(name: str) -> Table:
    """Return a table registered in the application metadata."""
    return Base.metadata.tables[name]


def test_security_tables_are_registered() -> None:
    """All Wave 4 security foundation tables are registered."""
    assert set(Base.metadata.tables) >= EXPECTED_SECURITY_TABLES


def test_user_security_state_is_modeled() -> None:
    """User persistence exposes the required account security state."""
    users = _table("users")

    assert "account_status" in users.c
    assert users.c.account_status.nullable is False
    assert users.c.account_status.default is not None
    assert users.c.account_status.default.arg == "active"

    assert "email_verified_at" in users.c
    assert users.c.email_verified_at.nullable is True


def test_password_credential_is_separate_from_user() -> None:
    """Password credentials remain independent from the user entity."""
    users = _table("users")
    credentials = _table("password_credentials")

    assert "password_hash" not in users.c

    assert set(credentials.c.keys()) == {
        "id",
        "user_id",
        "password_hash",
        "created_at",
        "updated_at",
    }

    assert credentials.c.user_id.nullable is False
    assert credentials.c.user_id.unique is True
    assert credentials.c.password_hash.nullable is False

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in credentials.foreign_keys
    }

    assert foreign_keys == {
        ("user_id", "users.id", "CASCADE"),
    }


def test_authorization_catalog_constraints() -> None:
    """Role and permission catalogs preserve unique server-owned names."""
    roles = _table("roles")
    permissions = _table("permissions")

    assert roles.c.name.nullable is False
    assert roles.c.name.unique is True

    assert permissions.c.name.nullable is False
    assert permissions.c.name.unique is True


def test_user_role_relationship_constraints() -> None:
    """User-role assignments use an authoritative composite identity."""
    user_roles = _table("user_roles")

    assert [column.name for column in user_roles.primary_key.columns] == [
        "user_id",
        "role_id",
    ]

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in user_roles.foreign_keys
    }

    assert foreign_keys == {
        ("user_id", "users.id", "CASCADE"),
        ("role_id", "roles.id", "CASCADE"),
    }


def test_role_permission_relationship_constraints() -> None:
    """Role-permission assignments use an authoritative composite identity."""
    role_permissions = _table("role_permissions")

    assert [column.name for column in role_permissions.primary_key.columns] == [
        "role_id",
        "permission_id",
    ]

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in role_permissions.foreign_keys
    }

    assert foreign_keys == {
        ("role_id", "roles.id", "CASCADE"),
        ("permission_id", "permissions.id", "CASCADE"),
    }


def test_authentication_session_constraints() -> None:
    """Authentication sessions preserve durable subject and lifecycle state."""
    sessions = _table("authentication_sessions")

    assert sessions.c.user_id.nullable is False
    assert sessions.c.absolute_expires_at.nullable is False
    assert sessions.c.revoked_at.nullable is True
    assert sessions.c.revocation_reason.nullable is True

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in sessions.foreign_keys
    }

    assert foreign_keys == {
        ("user_id", "users.id", "CASCADE"),
    }


def test_refresh_credential_constraints() -> None:
    """Refresh credentials preserve selector/verifier and rotation state."""
    credentials = _table("refresh_credentials")

    assert credentials.c.session_id.nullable is False
    assert credentials.c.selector.nullable is False
    assert credentials.c.selector.unique is True
    assert credentials.c.verifier_digest.nullable is False
    assert credentials.c.expires_at.nullable is False
    assert credentials.c.consumed_at.nullable is True
    assert credentials.c.replaced_by_id.nullable is True

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in credentials.foreign_keys
    }

    assert foreign_keys == {
        ("session_id", "authentication_sessions.id", "CASCADE"),
        ("replaced_by_id", "refresh_credentials.id", "SET NULL"),
    }


def test_recovery_capability_constraints() -> None:
    """Password recovery capabilities preserve single-use durable state."""
    recovery = _table("password_recovery_tokens")

    assert recovery.c.user_id.nullable is False
    assert recovery.c.token_digest.nullable is False
    assert recovery.c.token_digest.unique is True
    assert recovery.c.expires_at.nullable is False
    assert recovery.c.consumed_at.nullable is True
    assert recovery.c.revoked_at.nullable is True

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in recovery.foreign_keys
    }

    assert foreign_keys == {
        ("user_id", "users.id", "CASCADE"),
    }


def test_email_verification_capability_constraints() -> None:
    """Email verification capabilities preserve single-use durable state."""
    verification = _table("email_verification_tokens")

    assert verification.c.user_id.nullable is False
    assert verification.c.token_digest.nullable is False
    assert verification.c.token_digest.unique is True
    assert verification.c.expires_at.nullable is False
    assert verification.c.consumed_at.nullable is True
    assert verification.c.revoked_at.nullable is True

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname, foreign_key.ondelete)
        for foreign_key in verification.foreign_keys
    }

    assert foreign_keys == {
        ("user_id", "users.id", "CASCADE"),
    }


def test_raw_security_secrets_are_not_persisted() -> None:
    """Security persistence must not contain raw credential material."""
    security_tables = EXPECTED_SECURITY_TABLES - {"users"}

    for table_name in security_tables:
        columns = set(_table(table_name).c.keys())

        assert not columns & FORBIDDEN_SECRET_COLUMNS, (
            f"{table_name} contains forbidden raw-secret columns: "
            f"{sorted(columns & FORBIDDEN_SECRET_COLUMNS)}"
        )
