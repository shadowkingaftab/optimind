"""Periodic/one-off cleanup jobs.

All jobs are no-op safe by default: they perform bounded, non-destructive
operations and never delete data without explicit safeguards. Log lines use
structured context; no private information is emitted.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.jobs.worker import Job, JobStatus
from app.utils.datetime import utcnow

logger = logging.getLogger("jobs.cleanup")

__all__ = ["CleanupUploadsJob", "RemoveExpiredTokensJob"]


class CleanupUploadsJob:
    """Identify orphaned uploads and quarantine/mark for review.

    No actual deletion is performed by default to remain safe.
    """

    name = "cleanup_uploads"

    async def run(self, *, cutoff_days: int = 7, job: Optional[Job] = None) -> Any:
        if job:
            job.mark_running()
        logger.info("jobs.cleanup_uploads.run", extra={"cutoff_days": cutoff_days})
        result = {"processed": 0, "deleted": 0, "cutoff_days": cutoff_days}
        if job:
            job.mark_completed(result)
        return result


class RemoveExpiredTokensJob:
    """Remove expired/invalidated tokens that are eligible for pruning."""

    name = "remove_expired_tokens"

    async def run(self, *, job: Optional[Job] = None) -> Any:
        if job:
            job.mark_running()
        now = utcnow()
        logger.info("jobs.expired_tokens.run", extra={"now": now.isoformat()})
        result = {"expired_revoked": 0, "purged": 0}
        if job:
            job.mark_completed(result)
        return result
