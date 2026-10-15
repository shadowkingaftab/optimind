"""Health endpoint schemas.

Small, dependency-light models used by the health/readiness probes.
"""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str = "ok"
    version: str


class ReadinessResponse(BaseModel):
    """Readiness probe response including dependency status."""

    status: str = "ok"
    version: str
    database: str = "unknown"
