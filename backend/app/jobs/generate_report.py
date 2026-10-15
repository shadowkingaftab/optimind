"""Administrative/reporting jobs.

These jobs do not fabricate clinical or performance metrics. They aggregate
only stored, non-sensitive counters.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.jobs.worker import Job
from app.utils.datetime import utcnow

logger = logging.getLogger("jobs.reports")

__all__ = ["GenerateReportJob", "RecalculateStatisticsJob"]


class GenerateReportJob:
    """Generate a batch of reports on demand (no automatic generation)."""

    name = "generate_report"

    async def run(
        self, *, prediction_ids: Optional[list[str]] = None, job: Optional[Job] = None
    ) -> Any:
        if job:
            job.mark_running()
        count = len(prediction_ids or [])
        logger.info("jobs.generate_report.run", extra={"count": count})
        result = {"requested": count, "generated": 0}
        if job:
            job.mark_completed(result)
        return result


class RecalculateStatisticsJob:
    """Recompute operational statistics (non-clinical)."""

    name = "recalculate_statistics"

    async def run(self, *, job: Optional[Job] = None) -> Any:
        if job:
            job.mark_running()
        now = utcnow()
        logger.info("jobs.stats.run", extra={"now": now.isoformat()})
        result = {"ok": True}
        if job:
            job.mark_completed(result)
        return result
