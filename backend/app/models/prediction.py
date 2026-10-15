"""Prediction model.

A prediction records the outcome of a screening run against a single image.
All result fields are nullable so that honest "no result" states (low
quality, uncertain, abstained, failed) can be represented without inventing
values. This record is a screening output only, never a diagnosis.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
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
    from app.models.eye_image import EyeImage
    from app.models.model_version import ModelVersion
    from app.models.patient import Patient
    from app.models.prediction_item import PredictionItem
    from app.models.report import Report


class PredictionStatus(StrEnum):
    SUCCESS = "success"
    LOW_QUALITY = "low_quality"
    UNCERTAIN = "uncertain"
    ABSTAINED = "abstained"
    FAILED = "failed"


class RiskLevel(StrEnum):
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Prediction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single screening inference result."""

    __tablename__ = "predictions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eye_image_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("eye_images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    consent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("consents.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[PredictionStatus] = mapped_column(
        Enum(
            PredictionStatus,
            name="prediction_status",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    outcome_label: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(
        Enum(
            RiskLevel,
            name="risk_level",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=True,
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uncertainty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    model_version_label: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    patient: Mapped["Patient"] = relationship(back_populates="predictions")
    eye_image: Mapped[Optional["EyeImage"]] = relationship(
        back_populates="predictions"
    )
    model_version: Mapped[Optional["ModelVersion"]] = relationship()
    items: Mapped[list["PredictionItem"]] = relationship(
        back_populates="prediction", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(back_populates="prediction")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Prediction id={self.id!r} status={self.status}>"
