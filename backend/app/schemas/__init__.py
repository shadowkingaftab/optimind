"""Pydantic schemas.

Phase 2 defines the shared building blocks; Phase 3 adds the resource
schemas that mirror the shared contracts under ``contracts/``.
"""

from __future__ import annotations

from app.schemas.admin import AuditLogRead, SystemStatistics
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SessionInfo,
    TokenResponse,
)
from app.schemas.common import (
    HealthStatus,
    IdentifiedModel,
    MessageResponse,
    ORMModel,
    TimestampedResponse,
)
from app.schemas.errors import ErrorResponse, ValidationIssue
from app.schemas.health import HealthResponse, ReadinessResponse
from app.schemas.image_quality import ImageQualitySummary
from app.schemas.model_version import (
    ModelCapabilities,
    ModelMetadata,
    ModelVersionRead,
    ModelVersionRegister,
)
from app.schemas.pagination import Page, PageParams, pagination_meta
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from app.schemas.prediction import (
    PredictionItemResponse,
    PredictionRead,
    PredictionRequest,
    PredictionResponse,
)
from app.schemas.report import ReportGenerateRequest, ReportPreview, ReportRead
from app.schemas.upload import UploadResponse
from app.schemas.user import (
    RoleAssignRequest,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    "AuditLogRead",
    "ErrorResponse",
    "HealthResponse",
    "HealthStatus",
    "IdentifiedModel",
    "ImageQualitySummary",
    "LoginRequest",
    "LogoutRequest",
    "MessageResponse",
    "ModelCapabilities",
    "ModelMetadata",
    "ModelVersionRead",
    "ModelVersionRegister",
    "ORMModel",
    "Page",
    "PageParams",
    "PatientCreate",
    "PatientRead",
    "PatientUpdate",
    "PredictionItemResponse",
    "PredictionRead",
    "PredictionRequest",
    "PredictionResponse",
    "ReadinessResponse",
    "RefreshRequest",
    "ReportGenerateRequest",
    "ReportPreview",
    "ReportRead",
    "RoleAssignRequest",
    "SessionInfo",
    "SystemStatistics",
    "TimestampedResponse",
    "TokenResponse",
    "UploadResponse",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "ValidationIssue",
    "pagination_meta",
]
