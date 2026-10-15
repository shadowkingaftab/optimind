"""FastAPI application factory and ASGI entrypoint.

Run locally with::

    uvicorn app.main:app --reload

The factory keeps construction explicit so tests can build isolated apps.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.constants import (
    API_DESCRIPTION,
    API_TITLE,
    APP_VERSION,
)
from app.core.exception_handlers import register_exception_handlers
from app.core.settings import get_settings
from app.lifespan import lifespan
from app.middleware import register_middleware


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=settings.api_title or API_TITLE,
        version=APP_VERSION,
        description=API_DESCRIPTION,
        lifespan=lifespan,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        # Never include examples that could be mistaken for clinical output.
        swagger_ui_parameters={"persistAuthorization": True},
    )

    # Order matters: middleware then exception handlers then routes.
    register_middleware(application, settings)
    register_exception_handlers(application)
    application.include_router(api_router)

    return application


app = create_app()
