"""Per-condition prediction item.

A prediction may report several condition scores (multi-label screening).
Each item is optional/detached: absence of an item means "not assessed",
not "negative".
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    enum_values,
)
from app.models.prediction import RiskLevel

if TYPE_CHECKING:
    from app.models.prediction import Prediction


class PredictionItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single scored condition within a prediction."""

    __tablename__ = "prediction_items"

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    condition_code: Mapped[str] = mapped_column(String(64), nullable=False)
    condition_label: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    prediction: Mapped["Prediction"] = relationship(back_populates="items")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<PredictionItem id={self.id!r} code={self.condition_code!r}>"
