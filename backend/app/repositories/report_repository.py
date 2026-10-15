"""Report persistence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select

from app.models.report import Report, ReportStatus
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[Report]):
    model = Report

    async def list_for_patient(
        self, patient_id: uuid.UUID, *, limit: int = 50, offset: int = 0
    ) -> Sequence[Report]:
        stmt = (
            select(Report)
            .where(Report.patient_id == patient_id)
            .order_by(Report.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def list_for_prediction(self, prediction_id: uuid.UUID) -> Sequence[Report]:
        stmt = (
            select(Report)
            .where(Report.prediction_id == prediction_id)
            .order_by(Report.created_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def count_for_patient(self, patient_id: uuid.UUID) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Report).where(
            Report.patient_id == patient_id
        )
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def create(
        self,
        *,
        patient_id: uuid.UUID,
        status: ReportStatus = ReportStatus.PENDING,
        prediction_id: Optional[uuid.UUID] = None,
        generated_by_user_id: Optional[uuid.UUID] = None,
    ) -> Report:
        report = Report(
            patient_id=patient_id,
            status=status,
            prediction_id=prediction_id,
            generated_by_user_id=generated_by_user_id,
        )
        return await self.add(report)

    async def mark_generated(
        self,
        report: Report,
        *,
        storage_key: str,
        media_type: str,
        byte_size: int,
        checksum_sha256: Optional[str],
        generated_at: datetime,
    ) -> None:
        report.status = ReportStatus.GENERATED
        report.storage_key = storage_key
        report.media_type = media_type
        report.byte_size = byte_size
        report.checksum_sha256 = checksum_sha256
        report.generated_at = generated_at
        report.error_code = None
        await self.session.flush()

    async def mark_failed(self, report: Report, *, error_code: str) -> None:
        report.status = ReportStatus.FAILED
        report.error_code = error_code
        await self.session.flush()
