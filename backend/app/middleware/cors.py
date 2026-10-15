"""CORS configuration.

Wraps Starlette's ``CORSMiddleware`` and derives its parameters from
settings. Wildcard origins are never combined with credentials.
"""

from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.settings import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Attach CORS middleware when origins are configured."""
    origins = list(settings.cors_allow_origins)
    if not origins:
        return

    allow_credentials = settings.cors_allow_credentials
    # Browsers reject credentialed requests with a wildcard origin.
    if "*" in origins and allow_credentials:
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=list(settings.cors_allow_methods) or ["*"],
        allow_headers=list(settings.cors_allow_headers) or ["*"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )
