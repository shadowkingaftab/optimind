"""Patient model.

Patient records are kept deliberately minimal and pseudonymous by default.
No clinical values, diagnoses or fabricated identifiers are stored here.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.consent import Consent
    from app.models.eye_image import EyeImage
    from app.models.prediction import Prediction
    from app.models.report import Report


class Patient(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A person undergoing screening.

    ``patient_code`` is the pseudonymous identifier used throughout the
    system. Free-text identity fields are optional and may be omitted
    entirely in a deployment that operates on de-identified data.
    """

    __tablename__ = "patients"

    patient_code: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    consents: Mapped[list["Consent"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    eye_images: Mapped[list["EyeImage"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Patient id={self.id!r} code={self.patient_code!r}>"
