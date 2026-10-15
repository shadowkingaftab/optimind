"""Request id / correlation id middleware.

Ensures every request carries an ``X-Request-ID`` (generated when absent) and
an optional ``X-Correlation-ID``, binding both to the request context so log
records and error responses can be correlated.
"""

from __future__ import annotations

import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core import request_context
from app.core.constants import CORRELATION_ID_HEADER, REQUEST_ID_HEADER


class RequestIDMiddleware:
    """ASGI middleware that establishes request/correlation identifiers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        incoming_request_id = _header(headers, REQUEST_ID_HEADER)
        incoming_correlation_id = _header(headers, CORRELATION_ID_HEADER)

        request_id = incoming_request_id or str(uuid.uuid4())
        correlation_id = incoming_correlation_id or request_id

        request_token = request_context.set_request_id(request_id)
        correlation_token = request_context.set_correlation_id(correlation_id)

        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id
        scope["state"]["correlation_id"] = correlation_id

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                mutable = MutableHeaders(scope=message)
                mutable[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        finally:
            request_context.reset_request_id(request_token)
            request_context.reset_correlation_id(correlation_token)


def _header(headers: dict[bytes, bytes], name: str) -> str | None:
    raw = headers.get(name.lower().encode("latin-1"))
    if raw is None:
        return None
    try:
        return raw.decode("latin-1").strip() or None
    except (UnicodeDecodeError, AttributeError):
        return None
