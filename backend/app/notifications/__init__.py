"""Notifications package exports."""

from __future__ import annotations

from .email_sender import ConsoleEmailSender, EmailMessage, EmailSender
from .events import PredictionCompleteEvent, ReportReadyEvent
from .notification_service import NotificationService
from .templates import render_prediction_complete, render_report_ready

__all__ = [
    "ConsoleEmailSender",
    "EmailMessage",
    "EmailSender",
    "NotificationService",
    "PredictionCompleteEvent",
    "ReportReadyEvent",
    "render_prediction_complete",
    "render_report_ready",
]
