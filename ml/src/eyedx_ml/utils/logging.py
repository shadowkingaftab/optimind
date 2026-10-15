"""Privacy-safe logging.

Provides a logger that never emits patient identifiers or file contents. Callers
should pass only non-identifying, aggregated values as ``extra`` fields.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Optional

__all__ = ["get_logger", "redact_identifier", "SENSITIVE_KEYS"]

# Keys that must never be logged verbatim.
SENSITIVE_KEYS = frozenset(
    {
        "patient_id",
        "patient_code",
        "mrn",
        "image_path",
        "path",
        "file",
        "token",
        "password",
        "secret",
        "email",
    }
)


def redact_identifier(value: Optional[str]) -> Optional[str]:
    """Return a short, non-reversible tag for correlating logs safely."""
    if not value:
        return value
    suffix = str(value)[-4:]
    return f"***{suffix}"


def _scrub(extra: dict) -> dict:
    cleaned: dict = {}
    for key, value in extra.items():
        if key.lower() in SENSITIVE_KEYS:
            if isinstance(value, str):
                cleaned[key] = redact_identifier(value)
            else:
                cleaned[key] = "***"
        else:
            cleaned[key] = value
    return cleaned


class _ScrubFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for key in list(record.__dict__.keys()):
            if key.lower() in SENSITIVE_KEYS:
                value = record.__dict__[key]
                if isinstance(value, str):
                    record.__dict__[key] = redact_identifier(value)
                else:
                    record.__dict__[key] = "***"
        return True


def get_logger(name: str = "eyedx_ml", level: int = logging.INFO) -> logging.Logger:
    """Return a namespaced logger with privacy scrubbing attached once."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        handler.addFilter(_ScrubFilter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


def log_event(logger: logging.Logger, message: str, **fields: Any) -> None:
    """Log a message with scrubbed structured fields."""
    logger.info(message, extra=_scrub(fields))
