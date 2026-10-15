"""Outermost error-handling middleware (safety net).

FastAPI's exception handlers cover route-level errors. This middleware is the
final backstop for exceptions raised by other middleware or during response
streaming. It guarantees a contract-shaped JSON body and never exposes a
stack trace to the client.
"""

from __future__ import annotations

import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core import request_context
from app.core.constants import REQUEST_ID_HEADER
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware:
    """ASGI middleware converting unhandled exceptions to JSON errors."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_tracking(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, send_tracking)
        except Exception:  # noqa: BLE001 - final safety net
            logger.exception("unhandled_middleware_exception")
            if response_started:
                # Response already partially sent; cannot replace it safely.
                raise
            await self._send_internal_error(send)

    async def _send_internal_error(self, send: Send) -> None:
        request_id = request_context.get_request_id()
        body: dict[str, object] = {
            "error": "internal_error",
            "message": "An unexpected error occurred.",
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
        await send({"type": "http.response.start", "status": 500, "headers": headers})
        await send({"type": "http.response.body", "body": payload})
