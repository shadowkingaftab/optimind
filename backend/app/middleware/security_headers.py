"""Security response headers middleware.

Adds conservative, widely-compatible security headers. HSTS is only emitted
for HTTPS requests so that local HTTP development is not locked out.
"""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

_HSTS_VALUE = "max-age=31536000; includeSubDomains"


class SecurityHeadersMiddleware:
    """ASGI middleware adding security headers to responses."""

    def __init__(self, app: ASGIApp, *, enable_hsts: bool = True) -> None:
        self.app = app
        self.enable_hsts = enable_hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        is_secure = scope.get("scheme") == "https"

        async def add_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for key, value in _BASE_HEADERS.items():
                    if key not in headers:
                        headers[key] = value
                if self.enable_hsts and is_secure and "Strict-Transport-Security" not in headers:
                    headers["Strict-Transport-Security"] = _HSTS_VALUE
            await send(message)

        await self.app(scope, receive, add_headers)
