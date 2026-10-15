"""Email delivery abstraction.

The default implementation logs messages to the application logger rather
than sending real email. This is safe for development and prevents accidental
secrets or external calls in test contexts.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("notifications.email")

__all__ = ["EmailMessage", "EmailSender", "ConsoleEmailSender"]


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None


class EmailSender(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None:  # pragma: no cover
        ...


class ConsoleEmailSender(EmailSender):
    """Log-only sender: no external network calls are made."""

    async def send(self, message: EmailMessage) -> None:
        logger.info("email.send", extra={"to": message.to, "subject": message.subject})
