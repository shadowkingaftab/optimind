"""Async session management.

Provides the FastAPI request-scoped session dependency and an explicit
``session_scope`` context manager for background jobs and scripts.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.database.engine import get_engine

_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory, creating it on first use."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Transactional session scope for scripts and background jobs.

    Commits on clean exit, rolls back and re-raises on error.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped session.

    The session is closed after the response. Commits are the responsibility
    of the service/repository layer so that units of work stay explicit.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_session_factory() -> None:
    """Reset the cached session factory (used on shutdown)."""
    global _session_factory
    _session_factory = None
