"""Image quality schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImageQualitySummary(BaseModel):
    """Structural quality assessment of an image.

    Values are heuristic quality signals, not clinical measurements.
    """

    model_config = ConfigDict(extra="forbid")

    acceptable: bool
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
