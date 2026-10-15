"""Access logging middleware.

Emits one structured log line per HTTP request with method, route, status
and duration. Request bodies, query strings and headers are never logged to
avoid capturing sensitive data.
"""

from __future__ import annotations

import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging_config import get_logger

logger = get_logger("app.access")

# Paths excluded from access logs to reduce noise.
_SILENT_PATHS = frozenset({"/health", "/healthz", "/ready", "/metrics"})


class RequestLoggingMiddleware:
    """ASGI middleware that logs request completion."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()
        status_code: int = 500

        async def capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        finally:
            path = scope.get("path", "")
            if path not in _SILENT_PATHS:
                duration_ms = round((time.perf_counter() - started) * 1000.0, 2)
                logger.info(
                    "request_completed",
                    extra={
                        "http_method": scope.get("method"),
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client": _client_host(scope),
                    },
                )


def _client_host(scope: Scope) -> str | None:
    client = scope.get("client")
    if client:
        return client[0]
    return None
