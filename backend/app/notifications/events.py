"""Notification types and payloads.

Domain events that may result in outbound notifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

__all__ = ["PredictionCompleteEvent", "ReportReadyEvent"]


@dataclass(frozen=True)
class PredictionCompleteEvent:
    prediction_id: str
    patient_id: Optional[str] = None
    status: str = ""
    model_version: Optional[str] = None


@dataclass(frozen=True)
class ReportReadyEvent:
    report_id: str
    patient_id: Optional[str] = None
    prediction_id: Optional[str] = None
    file_url: Optional[str] = None
