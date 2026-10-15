"""HTTP middleware stack.

``register_middleware`` wires the stack in a deliberate order (outermost
first): error handling -> request id -> access logging -> rate limiting ->
body size -> security headers -> CORS.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.core.settings import Settings
from app.middleware.content_length import ContentLengthLimitMiddleware
from app.middleware.cors import configure_cors
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

__all__ = [
    "ContentLengthLimitMiddleware",
    "ErrorHandlerMiddleware",
    "RateLimitMiddleware",
    "RequestIDMiddleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "configure_cors",
    "register_middleware",
]


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Attach the full middleware stack to ``app``.

    Starlette treats the most recently added middleware as the outermost, so
    these are added inner-to-outer.
    """
    # CORS (inner) -- runs closest to the routes.
    configure_cors(app, settings)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        ContentLengthLimitMiddleware,
        max_bytes=settings.max_upload_mb * 1024 * 1024,
    )
    app.add_middleware(
        RateLimitMiddleware,
        limit_per_minute=settings.rate_limit_per_minute,
        enabled=not settings.debug,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    # Error handler (outer) -- final backstop.
    app.add_middleware(ErrorHandlerMiddleware)
