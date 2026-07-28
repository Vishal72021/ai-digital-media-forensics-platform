"""add wave 4 security foundation

Revision ID: e5fa1d2044ee
Revises: 819c29544e40
Create Date: 2026-07-26 18:49:12

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5fa1d2044ee"
down_revision: str | Sequence[str] | None = "819c29544e40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Introduce the Wave 4 security persistence foundation."""
    op.add_column(
        "users",
        sa.Column("account_status", sa.String(length=32), nullable=True),
    )

    op.execute(sa.text("UPDATE users SET account_status = 'active' WHERE account_status IS NULL"))

    op.alter_column(
        "users",
        "account_status",
        existing_type=sa.String(length=32),
        nullable=False,
    )

    op.add_column(
        "users",
        sa.Column(
            "email_verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_table(
        "password_credentials",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_password_credentials_user_id",
        "password_credentials",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("permission_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "authentication_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "absolute_expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "revocation_reason",
            sa.String(length=128),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_authentication_sessions_user_id",
        "authentication_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "refresh_credentials",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("selector", sa.String(length=128), nullable=False),
        sa.Column("verifier_digest", sa.Text(), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("replaced_by_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["replaced_by_id"],
            ["refresh_credentials.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["authentication_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_refresh_credentials_selector",
        "refresh_credentials",
        ["selector"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_credentials_session_id",
        "refresh_credentials",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "password_recovery_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_digest", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_digest"),
    )
    op.create_index(
        "ix_password_recovery_tokens_user_id",
        "password_recovery_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_digest", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_digest"),
    )
    op.create_index(
        "ix_email_verification_tokens_user_id",
        "email_verification_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the Wave 4 security persistence foundation."""
    op.drop_index(
        "ix_email_verification_tokens_user_id",
        table_name="email_verification_tokens",
    )
    op.drop_table("email_verification_tokens")

    op.drop_index(
        "ix_password_recovery_tokens_user_id",
        table_name="password_recovery_tokens",
    )
    op.drop_table("password_recovery_tokens")

    op.drop_index(
        "ix_refresh_credentials_session_id",
        table_name="refresh_credentials",
    )
    op.drop_index(
        "ix_refresh_credentials_selector",
        table_name="refresh_credentials",
    )
    op.drop_table("refresh_credentials")

    op.drop_index(
        "ix_authentication_sessions_user_id",
        table_name="authentication_sessions",
    )
    op.drop_table("authentication_sessions")

    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")

    op.drop_index(
        "ix_password_credentials_user_id",
        table_name="password_credentials",
    )
    op.drop_table("password_credentials")

    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "account_status")
