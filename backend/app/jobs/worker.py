"""Job status tracking primitives."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Optional

from app.utils.datetime import utcnow

__all__ = ["JobStatus", "Job"]


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    def __init__(
        self,
        job_id: str,
        name: str,
        *,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        self.id = job_id
        self.name = name
        self.status = JobStatus.PENDING
        self.payload = payload or {}
        self.result: Any | None = None
        self.error: str | None = None
        self.created_at = utcnow()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

    def mark_running(self) -> None:
        if self.status == JobStatus.PENDING:
            self.status = JobStatus.RUNNING
            self.started_at = utcnow()

    def mark_completed(self, result: Any = None) -> None:
        self.status = JobStatus.COMPLETED
        self.result = result
        self.completed_at = utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = JobStatus.FAILED
        self.error = error
        self.completed_at = utcnow()

    def mark_cancelled(self) -> None:
        self.status = JobStatus.CANCELLED
        self.completed_at = utcnow()

    @property
    def duration_ms(self) -> Optional[float]:
        if self.started_at is None or self.completed_at is None:
            return None
        return (self.completed_at - self.started_at).total_seconds() * 1000.0
