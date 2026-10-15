"""Database health probe.

Performs a lightweight ``SELECT 1`` against the configured database and
returns a structured, non-sensitive result. Connection strings and driver
errors are never surfaced verbatim.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy import text

from app.core.logging_config import get_logger
from app.database.engine import get_engine

logger = get_logger(__name__)

_PROBE_SQL = text("SELECT 1")


@dataclass(frozen=True)
class DatabaseHealth:
    """Result of a database connectivity probe."""

    healthy: bool
    latency_ms: float
    detail: str = ""


async def check_database() -> DatabaseHealth:
    """Return connectivity status for the database.

    Never raises: failures are reported via the returned object so health
    endpoints can respond gracefully.
    """
    started = time.perf_counter()
    try:
        engine = get_engine()
        async with engine.connect() as connection:
            await connection.execute(_PROBE_SQL)
        latency_ms = (time.perf_counter() - started) * 1000.0
        return DatabaseHealth(healthy=True, latency_ms=round(latency_ms, 2))
    except Exception:  # noqa: BLE001 - health probe must never propagate
        latency_ms = (time.perf_counter() - started) * 1000.0
        logger.error("database_health_check_failed")
        return DatabaseHealth(
            healthy=False,
            latency_ms=round(latency_ms, 2),
            detail="database_unreachable",
        )
