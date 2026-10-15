"""Report model.

A report is a rendered document (for example PDF) generated from a
prediction. It stores a reference to the stored object, not the document
bytes. Reports restate screening output and carry the non-diagnostic
limitation notice.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    enum_values,
)

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.prediction import Prediction


class ReportStatus(StrEnum):
    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A generated screening report document."""

    __tablename__ = "reports"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("predictions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus,
            name="report_status",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=False,
        default=ReportStatus.PENDING,
        index=True,
    )

    storage_key: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    media_type: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    byte_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    generated_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    patient: Mapped["Patient"] = relationship(back_populates="reports")
    prediction: Mapped[Optional["Prediction"]] = relationship(
        back_populates="reports"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Report id={self.id!r} status={self.status}>"
