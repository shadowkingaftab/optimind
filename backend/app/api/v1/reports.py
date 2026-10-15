"""Report endpoints.

Reports restate screening output for a prediction and always carry the
non-diagnostic limitation notice. Generation may be unavailable when the PDF
renderer is not installed; that is surfaced honestly.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import PageParamsDep, ReportServiceDep
from app.authentication.current_user import CurrentUserDep
from app.authorization.access_control import require_permission
from app.core.permissions import REPORTS_GENERATE, REPORTS_READ
from app.schemas.pagination import Page
from app.schemas.report import ReportGenerateRequest, ReportPreview, ReportRead

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportRead,
    status_code=201,
    summary="Generate a report for a prediction",
    dependencies=[Depends(require_permission(REPORTS_GENERATE))],
)
async def generate_report(
    payload: ReportGenerateRequest,
    service: ReportServiceDep,
    actor: CurrentUserDep,
) -> ReportRead:
    report = await service.generate_for_prediction(
        prediction_id=payload.prediction_id, actor=actor
    )
    return ReportRead.model_validate(report)


@router.get(
    "/{report_id}",
    response_model=ReportRead,
    summary="Get a report",
    dependencies=[Depends(require_permission(REPORTS_READ))],
)
async def get_report(report_id: uuid.UUID, service: ReportServiceDep) -> ReportRead:
    report = await service.get(report_id)
    return ReportRead.model_validate(report)


@router.get(
    "/preview/{prediction_id}",
    response_model=ReportPreview,
    summary="Preview a report as plain text",
    dependencies=[Depends(require_permission(REPORTS_READ))],
)
async def preview_report(
    prediction_id: uuid.UUID, service: ReportServiceDep
) -> ReportPreview:
    text = await service.preview_text(prediction_id)
    return ReportPreview(prediction_id=prediction_id, text=text)


@router.get(
    "",
    response_model=Page[ReportRead],
    summary="List reports for a patient",
    dependencies=[Depends(require_permission(REPORTS_READ))],
)
async def list_reports(
    service: ReportServiceDep,
    params: PageParamsDep,
    patient_id: uuid.UUID = Query(...),
) -> Page[ReportRead]:
    items = await service.list_for_patient(
        patient_id, limit=params.limit, offset=params.offset
    )
    total = await service.count_for_patient(patient_id)
    return Page.create(
        [ReportRead.model_validate(item) for item in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
