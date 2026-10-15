"""Request body size limit middleware.

Rejects requests whose declared ``Content-Length`` exceeds the configured
maximum with a contract-shaped 413 response, before the body is read.
"""

from __future__ import annotations

import json

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core import request_context
from app.core.constants import REQUEST_ID_HEADER


class ContentLengthLimitMiddleware:
    """ASGI middleware enforcing a maximum request body size."""

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max(0, max_bytes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or self.max_bytes <= 0:
            await self.app(scope, receive, send)
            return

        declared = _content_length(scope)
        if declared is not None and declared > self.max_bytes:
            await self._reject(send)
            return

        await self.app(scope, receive, send)

    async def _reject(self, send: Send) -> None:
        request_id = request_context.get_request_id()
        body: dict[str, object] = {
            "error": "payload_too_large",
            "message": "The uploaded payload exceeds the allowed size.",
        }
        if request_id:
            body["request_id"] = request_id
        payload = json.dumps(body).encode("utf-8")
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(payload)).encode("latin-1")),
        ]
        if request_id:
            headers.append(
                (REQUEST_ID_HEADER.lower().encode("latin-1"), request_id.encode("latin-1"))
            )
        await send({"type": "http.response.start", "status": 413, "headers": headers})
        await send({"type": "http.response.body", "body": payload})


def _content_length(scope: Scope) -> int | None:
    for name, value in scope.get("headers") or []:
        if name.lower() == b"content-length":
            try:
                return int(value.decode("latin-1"))
            except (ValueError, UnicodeDecodeError):
                return None
    return None
