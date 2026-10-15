"""Report service.

Generates a screening report from a persisted prediction: builds the
document, renders a PDF (honestly failing if the renderer is unavailable),
stores it and records the outcome.
"""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import ACTION_REPORT_GENERATE, RESOURCE_REPORT
from app.audit.audit_logger import AuditLogger
from app.exceptions.base import NotFoundError
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.reports import (
    ReportRenderError,
    build_report_document,
    render_pdf,
    render_text,
    store_report,
)
from app.repositories.patient_repository import PatientRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.report_repository import ReportRepository
from app.utils.datetime import utcnow


class ReportService:
    """Creates and retrieves screening reports."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._reports = ReportRepository(session)
        self._predictions = PredictionRepository(session)
        self._patients = PatientRepository(session)
        self._audit = AuditLogger(session)

    async def get(self, report_id: uuid.UUID) -> Report:
        report = await self._reports.get(report_id)
        if report is None:
            raise NotFoundError("The requested report was not found.")
        return report

    async def count_for_patient(self, patient_id: uuid.UUID) -> int:
        return await self._reports.count_for_patient(patient_id)

    async def generate_for_prediction(
        self,
        *,
        prediction_id: uuid.UUID,
        actor: Optional[User] = None,
    ) -> Report:
        prediction = await self._predictions.get(prediction_id)
        if prediction is None:
            raise NotFoundError("The requested prediction was not found.")

        patient = await self._patients.get(prediction.patient_id)
        document = build_report_document(
            prediction,
            patient_code=patient.patient_code if patient else None,
            generated_at=utcnow(),
        )

        report = await self._reports.create(
            patient_id=prediction.patient_id,
            status=ReportStatus.PENDING,
            prediction_id=prediction.id,
            generated_by_user_id=actor.id if actor else None,
        )

        try:
            pdf_bytes = render_pdf(document)
        except ReportRenderError as exc:
            await self._reports.mark_failed(report, error_code=exc.error_code)
            await self._session.commit()
            raise

        stored = await store_report(
            patient_id=str(prediction.patient_id), data=pdf_bytes
        )
        await self._reports.mark_generated(
            report,
            storage_key=stored.key,
            media_type="application/pdf",
            byte_size=stored.size_bytes,
            checksum_sha256=stored.checksum_sha256,
            generated_at=document.generated_at,
        )
        await self._audit.record(
            ACTION_REPORT_GENERATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_REPORT,
            resource_id=str(report.id),
            metadata={"prediction_id": str(prediction.id)},
        )
        await self._session.commit()
        return report

    async def preview_text(self, prediction_id: uuid.UUID) -> str:
        prediction = await self._predictions.get(prediction_id)
        if prediction is None:
            raise NotFoundError("The requested prediction was not found.")
        patient = await self._patients.get(prediction.patient_id)
        document = build_report_document(
            prediction,
            patient_code=patient.patient_code if patient else None,
        )
        return render_text(document)
