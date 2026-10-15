"""Health and readiness endpoints.

Liveness is dependency-free; readiness probes the database. Responses are
non-sensitive and safe for infrastructure probes.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.constants import APP_VERSION
from app.database.health_check import check_database
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ReadinessResponse, summary="Health probe")
async def health() -> ReadinessResponse:
    """Return service and database status."""
    db = await check_database()
    return ReadinessResponse(
        status="ok" if db.healthy else "degraded",
        version=APP_VERSION,
        database="ok" if db.healthy else "unavailable",
    )


@router.get("/health/live", response_model=HealthResponse, summary="Liveness probe")
async def liveness() -> HealthResponse:
    """Return liveness without touching dependencies."""
    return HealthResponse(status="ok", version=APP_VERSION)
