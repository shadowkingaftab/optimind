"""Rate limiting middleware (in-process fixed window).

This provides a *baseline* rate limit suitable for a single process. For
multi-worker or horizontally-scaled deployments a shared backing store
(e.g. Redis) is required; that dependency is recorded as a deployment input
rather than assumed here.

When the limit is exceeded a contract-shaped 429 response is returned with a
``Retry-After`` header.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core import request_context
from app.core.constants import REQUEST_ID_HEADER

_EXEMPT_PATHS = frozenset({"/health", "/healthz", "/ready", "/metrics"})


@dataclass
class _Window:
    count: int
    reset_at: float


class InMemoryRateLimiter:
    """Thread-safe-enough fixed-window counter (single event loop)."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = max(1, limit)
        self.window_seconds = max(1, window_seconds)
        self._windows: dict[str, _Window] = {}

    def check(self, key: str) -> tuple[bool, int]:
        """Return ``(allowed, retry_after_seconds)`` for ``key``."""
        now = time.monotonic()
        window = self._windows.get(key)
        if window is None or now >= window.reset_at:
            self._windows[key] = _Window(count=1, reset_at=now + self.window_seconds)
            return True, 0

        if window.count >= self.limit:
            retry_after = max(1, math.ceil(window.reset_at - now))
            return False, retry_after

        window.count += 1
        return True, 0

    def prune(self, now: float | None = None) -> None:
        """Drop expired windows to bound memory usage."""
        current = now if now is not None else time.monotonic()
        for key in [k for k, w in self._windows.items() if current >= w.reset_at]:
            self._windows.pop(key, None)


class RateLimitMiddleware:
    """ASGI middleware enforcing a per-client request rate limit."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        limit_per_minute: int,
        enabled: bool = True,
    ) -> None:
        self.app = app
        self.enabled = enabled
        self.limiter = InMemoryRateLimiter(limit_per_minute, window_seconds=60)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in _EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        key = _client_key(scope)
        allowed, retry_after = self.limiter.check(key)
        if not allowed:
            await self._reject(send, retry_after)
            return

        await self.app(scope, receive, send)

    async def _reject(self, send: Send, retry_after: int) -> None:
        request_id = request_context.get_request_id()
        body: dict[str, object] = {
            "error": "rate_limited",
            "message": "Too many requests. Please retry later.",
        }
        if request_id:
            body["request_id"] = request_id
        payload = json.dumps(body).encode("utf-8")
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(payload)).encode("latin-1")),
            (b"retry-after", str(retry_after).encode("latin-1")),
        ]
        if request_id:
            headers.append(
                (REQUEST_ID_HEADER.lower().encode("latin-1"), request_id.encode("latin-1"))
            )
        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": payload})


def _client_key(scope: Scope) -> str:
    client = scope.get("client")
    if client:
        return client[0]
    return "unknown"
