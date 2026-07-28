"""Refresh credential persistence model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RefreshCredential(Base):
    """Represents one persisted refresh-credential generation."""

    __tablename__ = "refresh_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authentication_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    selector: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    verifier_digest: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    generation: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("refresh_credentials.id", ondelete="SET NULL"),
        nullable=True,
    )
