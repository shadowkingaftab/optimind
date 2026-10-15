"""Application lifespan (startup / shutdown).

Startup:
    * configure logging,
    * validate required settings (fail fast),
    * measure database connectivity (non-fatal, logged),
    * record a startup system event in the log stream.

Shutdown:
    * release the database engine and session factory.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.constants import API_VERSION, APP_VERSION
from app.core.logging_config import configure_logging, get_logger
from app.core.settings import get_settings
from app.database.health_check import check_database

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    settings = get_settings()

    configure_logging(level=settings.log_level, json_output=settings.log_json)

    # Fail fast on missing required configuration.
    settings.validate_for_startup()

    logger.info(
        "application_startup",
        extra={
            "app_env": settings.app_env,
            "api_version": API_VERSION,
            "app_version": APP_VERSION,
        },
    )

    database_health = await check_database()
    if database_health.healthy:
        logger.info(
            "database_ready", extra={"latency_ms": database_health.latency_ms}
        )
    else:
        # Not fatal: the service can still report unreadiness via health.
        logger.warning("database_not_ready", extra={"detail": database_health.detail})

    try:
        yield
    finally:
        from app.database.engine import dispose_engine
        from app.database.session import dispose_session_factory

        await dispose_session_factory()
        await dispose_engine()
        logger.info("application_shutdown")
