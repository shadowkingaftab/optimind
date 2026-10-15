"""Consent model.

Consent governs whether a patient's images may be processed and stored.
Absence of an active consent must be handled explicitly by callers; this
model never assumes consent exists.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    enum_values,
)

if TYPE_CHECKING:
    from app.models.patient import Patient


class ConsentStatus(StrEnum):
    PENDING = "pending"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsentType(StrEnum):
    SCREENING = "screening"
    STORAGE = "storage"
    RESEARCH = "research"


class Consent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A record of a patient's consent decision."""

    __tablename__ = "consents"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type: Mapped[ConsentType] = mapped_column(
        Enum(
            ConsentType,
            name="consent_type",
            native_enum=False,
            length=32,
            values_callable=enum_values,
        ),
        nullable=False,
        default=ConsentType.SCREENING,
    )
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(
            ConsentStatus,
            name="consent_status",
            native_enum=False,
            length=32,
            values_callable=enum_values,
        ),
        nullable=False,
        default=ConsentStatus.PENDING,
        index=True,
    )
    granted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    document_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    recorded_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(back_populates="consents")

    @property
    def is_active(self) -> bool:
        """Return True when consent is granted and not expired/withdrawn."""
        if self.status is not ConsentStatus.GRANTED:
            return False
        if self.withdrawn_at is not None:
            return False
        if self.expires_at is not None:
            from datetime import timezone

            return self.expires_at > datetime.now(timezone.utc)
        return True

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Consent id={self.id!r} status={self.status}>"
