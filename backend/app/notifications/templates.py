"""Plain-text templates for notification bodies."""

from __future__ import annotations

from typing import Optional

from app.notifications.events import PredictionCompleteEvent, ReportReadyEvent

__all__ = ["render_prediction_complete", "render_report_ready"]


def _line_prefix() -> str:
    return "[EyeDx Screening] "


def render_prediction_complete(event: PredictionCompleteEvent) -> str:
    lines = [_line_prefix() + "Prediction completed"]
    if event.prediction_id:
        lines.append(f"Prediction ID: {event.prediction_id}")
    if event.patient_id:
        lines.append(f"Patient: {event.patient_id}")
    if event.status:
        lines.append(f"Status: {event.status}")
    if event.model_version:
        lines.append(f"Model version: {event.model_version}")
    return "\n".join(lines)


def render_report_ready(event: ReportReadyEvent) -> str:
    lines = [_line_prefix() + "Report ready"]
    if event.report_id:
        lines.append(f"Report ID: {event.report_id}")
    if event.prediction_id:
        lines.append(f"Prediction ID: {event.prediction_id}")
    if event.patient_id:
        lines.append(f"Patient: {event.patient_id}")
    if event.file_url:
        lines.append(f"Link: {event.file_url}")
    return "\n".join(lines)
