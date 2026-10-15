"""Eye image model.

Stores *references* to stored image objects together with structural
metadata. Raw image bytes are never stored in the database.
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
    Integer,
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


class EyeSide(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    UNKNOWN = "unknown"


class QualityStatus(StrEnum):
    UNKNOWN = "unknown"
    ACCEPTABLE = "acceptable"
    INSUFFICIENT = "insufficient"


class EyeImage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A stored retinal/fundus image associated with a patient."""

    __tablename__ = "eye_images"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eye_side: Mapped[EyeSide] = mapped_column(
        Enum(
            EyeSide,
            name="eye_side",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=False,
        default=EyeSide.UNKNOWN,
    )
    quality_status: Mapped[QualityStatus] = mapped_column(
        Enum(
            QualityStatus,
            name="quality_status",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=False,
        default=QualityStatus.UNKNOWN,
        index=True,
    )

    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False)
    byte_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    captured_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    uploaded_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(back_populates="eye_images")
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="eye_image"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<EyeImage id={self.id!r} side={self.eye_side}>"
