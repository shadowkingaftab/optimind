"""Notification service.

Dispatches domain events to configured channels. By default, dispatch does not
fail the requesting operation (errors are logged and swallowed). Recipients are
not hard-coded; call sites must pass explicit targets when required.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.notifications.email_sender import EmailMessage, EmailSender
from app.notifications.events import PredictionCompleteEvent, ReportReadyEvent
from app.notifications.templates import (
    render_prediction_complete,
    render_report_ready,
)

logger = logging.getLogger("notifications.service")

__all__ = ["NotificationService"]


class NotificationService:
    def __init__(self, email_sender: EmailSender) -> None:
        self._email = email_sender

    async def notify_prediction_complete(
        self,
        event: PredictionCompleteEvent,
        *,
        email_to: Optional[str] = None,
    ) -> None:
        text = render_prediction_complete(event)
        logger.info("notifications.prediction_complete", extra={"event": event})
        if email_to:
            try:
                await self._email.send(
                    EmailMessage(
                        to=email_to,
                        subject="Prediction completed",
                        body_text=text,
                    )
                )
            except Exception:  # pragma: no cover - defensive
                logger.exception("notifications.email.failed")

    async def notify_report_ready(
        self,
        event: ReportReadyEvent,
        *,
        email_to: Optional[str] = None,
    ) -> None:
        text = render_report_ready(event)
        logger.info("notifications.report_ready", extra={"event": event})
        if email_to:
            try:
                await self._email.send(
                    EmailMessage(to=email_to, subject="Report ready", body_text=text)
                )
            except Exception:  # pragma: no cover - defensive
                logger.exception("notifications.email.failed")
