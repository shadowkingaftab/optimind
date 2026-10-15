"""Logging configuration.

Provides structured (optionally JSON) logging that automatically includes the
active request/correlation identifiers from :mod:`app.core.request_context`.

A redaction filter scrubs a small set of sensitive keys (tokens, passwords,
authorization headers) that must never appear in logs.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Iterable

from app.core import request_context

# Keys whose values must never be logged verbatim.
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "secret_key",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "jwt_secret_key",
        "database_url",
        "s3_secret_access_key",
        "s3_access_key_id",
        "api_key",
    }
)

_REDACTED = "***REDACTED***"

# Standard LogRecord attributes we never treat as structured extras.
_RESERVED_ATTRS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
        "asctime",
    }
)


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``data`` with sensitive values redacted."""
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            redacted[key] = _REDACTED
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted


class ContextFilter(logging.Filter):
    """Inject request context identifiers onto every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_context.get_request_id()
        record.correlation_id = request_context.get_correlation_id()
        record.user_id = request_context.get_user_id()
        return True


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON with context."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "user_id": getattr(record, "user_id", None),
        }

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_ATTRS
            and key not in {"request_id", "correlation_id", "user_id"}
            and not key.startswith("_")
        }
        if extras:
            payload["extra"] = redact_mapping(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Human-readable formatter including request identifiers."""

    def __init__(self) -> None:
        super().__init__(
            fmt=(
                "%(asctime)s %(levelname)-8s %(name)s "
                "[req=%(request_id)s corr=%(correlation_id)s] %(message)s"
            ),
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )


def configure_logging(
    *,
    level: str = "INFO",
    json_output: bool = False,
    stream: Any = None,
) -> None:
    """Configure the root logger.

    Args:
        level: Log level name (e.g. ``"INFO"``).
        json_output: Emit JSON lines when True, otherwise plain text.
        stream: Destination stream; defaults to ``sys.stdout``.
    """
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Replace handlers to avoid duplicate output on repeated configuration.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter() if json_output else TextFormatter())
    handler.addFilter(ContextFilter())
    root.addHandler(handler)

    # Quieten noisy third-party loggers unless debugging.
    if level.upper() != "DEBUG":
        for noisy in ("uvicorn.access", "sqlalchemy.engine"):
            logging.getLogger(noisy).setLevel("WARNING")


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)


def redact_keys(keys: Iterable[str]) -> None:
    """Extend the global redaction key set at runtime (best-effort)."""
    global _SENSITIVE_KEYS
    _SENSITIVE_KEYS = _SENSITIVE_KEYS | frozenset(k.lower() for k in keys)
