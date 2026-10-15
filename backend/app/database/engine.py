"""Async SQLAlchemy engine construction.

The engine is created lazily from settings and cached for the process. The
DSN is normalised to the asyncpg driver so callers may supply a standard
``postgresql://`` URL.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.settings import Settings, get_settings
from app.exceptions.base import ConfigurationError

_engine: Optional[AsyncEngine] = None

_ASYNC_DRIVER = "postgresql+asyncpg"


def _normalise_async_dsn(dsn: str) -> str:
    """Ensure the DSN uses the asyncpg driver."""
    if dsn.startswith("postgresql+asyncpg://"):
        return dsn
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", f"{_ASYNC_DRIVER}://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", f"{_ASYNC_DRIVER}://", 1)
    return dsn


def to_async_dsn(dsn: str) -> str:
    """Public alias for :func:`_normalise_async_dsn`."""
    return _normalise_async_dsn(dsn)


def create_engine(settings: Optional[Settings] = None) -> AsyncEngine:
    """Construct a new async engine from settings."""
    settings = settings or get_settings()
    dsn = settings.sqlalchemy_database_uri
    if not dsn:
        raise ConfigurationError(
            "DATABASE_URL is required to create the database engine."
        )

    return create_async_engine(
        _normalise_async_dsn(dsn),
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
        future=True,
    )


def get_engine() -> AsyncEngine:
    """Return the process-wide engine, creating it on first use."""
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


async def dispose_engine() -> None:
    """Dispose the cached engine and release pooled connections."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
