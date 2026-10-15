"""Refresh token model.

Refresh tokens are persisted only as irreversible hashes. The plaintext
token is returned to the client once and never stored server-side.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A persisted refresh-token hash and its lifecycle metadata."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RefreshToken id={self.id!r} user_id={self.user_id!r}>"
