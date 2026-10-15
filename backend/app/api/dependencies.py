"""Shared FastAPI dependencies.

Phase 2 provides the infrastructure-level dependencies (database session,
settings, pagination, request context). Authentication/authorization
dependencies are added in Phase 3.
"""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import RequestContext, get_context
from app.core.settings import Settings, get_settings
from app.database.session import get_db
from app.schemas.pagination import PageParams
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.consent_service import ConsentService
from app.services.model_version_service import ModelVersionService
from app.services.patient_service import PatientService
from app.services.prediction_service import PredictionService
from app.services.report_service import ReportService
from app.services.upload_service import UploadService
from app.services.user_service import UserService
from app.authentication.session_service import SessionService

# Re-exported for route use: ``db: Annotated[AsyncSession, Depends(get_session)]``
get_session = get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_app_settings() -> Settings:
    """Dependency returning cached application settings."""
    return get_settings()


def get_request_context() -> RequestContext:
    """Dependency returning the current request context snapshot."""
    return get_context()


def get_request_id() -> Optional[str]:
    """Dependency returning the current request id, if any."""
    return get_context().request_id


def pagination_params(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageParams:
    """Dependency producing validated pagination parameters."""
    return PageParams(page=page, page_size=page_size)


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
PageParamsDep = Annotated[PageParams, Depends(pagination_params)]
RequestContextDep = Annotated[RequestContext, Depends(get_request_context)]


# ---------------------------------------------------------------------------
# Service dependencies
# ---------------------------------------------------------------------------
def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


def get_patient_service(session: SessionDep) -> PatientService:
    return PatientService(session)


def get_consent_service(session: SessionDep) -> ConsentService:
    return ConsentService(session)


def get_upload_service(session: SessionDep) -> UploadService:
    return UploadService(session)


def get_prediction_service(session: SessionDep) -> PredictionService:
    return PredictionService(session)


def get_report_service(session: SessionDep) -> ReportService:
    return ReportService(session)


def get_model_version_service(session: SessionDep) -> ModelVersionService:
    return ModelVersionService(session)


def get_audit_service(session: SessionDep) -> AuditService:
    return AuditService(session)


def get_session_service(session: SessionDep) -> SessionService:
    return SessionService(session)


AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]
ConsentServiceDep = Annotated[ConsentService, Depends(get_consent_service)]
UploadServiceDep = Annotated[UploadService, Depends(get_upload_service)]
PredictionServiceDep = Annotated[PredictionService, Depends(get_prediction_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
ModelVersionServiceDep = Annotated[
    ModelVersionService, Depends(get_model_version_service)
]
