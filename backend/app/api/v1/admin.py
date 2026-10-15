"""Administrative endpoints: audit trail and operational statistics."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.api.dependencies import AuditServiceDep, PageParamsDep, SessionDep
from app.authorization.access_control import require_admin, require_permission
from app.core.permissions import AUDIT_READ
from app.repositories.eye_image_repository import EyeImageRepository
from app.repositories.model_version_repository import ModelVersionRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.admin import AuditLogRead, SystemStatistics
from app.schemas.pagination import Page

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/audit",
    response_model=Page[AuditLogRead],
    summary="Query the audit trail",
    dependencies=[Depends(require_permission(AUDIT_READ))],
)
async def list_audit(
    service: AuditServiceDep,
    params: PageParamsDep,
    action: Optional[str] = Query(default=None),
    resource_type: Optional[str] = Query(default=None),
) -> Page[AuditLogRead]:
    entries = await service.list_entries(
        action=action,
        resource_type=resource_type,
        limit=params.limit,
        offset=params.offset,
    )
    return Page.create(
        [AuditLogRead.model_validate(entry) for entry in entries],
        total=len(entries),
        page=params.page,
        page_size=params.page_size,
    )


@router.get(
    "/statistics",
    response_model=SystemStatistics,
    summary="Operational statistics",
    dependencies=[Depends(require_admin())],
)
async def statistics(session: SessionDep) -> SystemStatistics:
    predictions = PredictionRepository(session)
    by_status = await predictions.count_by_status()
    total_predictions = await predictions.count()
    total_patients = await PatientRepository(session).count()
    total_uploads = await EyeImageRepository(session).count()
    active = await ModelVersionRepository(session).get_active()
    return SystemStatistics(
        total_predictions=total_predictions,
        predictions_by_status=by_status,
        total_patients=total_patients,
        total_uploads=total_uploads,
        active_model_version=active.version if active else None,
    )
