"""Model version registry.

Tracks which inference artifact is approved and active. Performance metrics
are intentionally NOT stored on this model: they are deployment inputs and
must be supplied from real evaluation, never fabricated. The ``metadata``
JSON column exists to hold externally-provided, verified metadata verbatim.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    enum_values,
)


class ModelStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class ModelVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A versioned inference artifact."""

    __tablename__ = "model_versions"

    version: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    status: Mapped[ModelStatus] = mapped_column(
        Enum(
            ModelStatus,
            name="model_status",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        nullable=False,
        default=ModelStatus.CANDIDATE,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false", index=True
    )
    artifact_uri: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True
    )
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    input_contract_version: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True
    )
    output_contract_version: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retired_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    extra_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ModelVersion version={self.version!r} status={self.status}>"
