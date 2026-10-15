"""Repository layer.

Repositories provide intention-revealing persistence methods over the ORM.
They flush but never commit; transactions are owned by the service layer via
``session_scope`` or the request-scoped DB dependency.
"""

from __future__ import annotations

from app.repositories.audit_repository import AuditRepository
from app.repositories.base_repository import BaseRepository
from app.repositories.consent_repository import ConsentRepository
from app.repositories.eye_image_repository import EyeImageRepository
from app.repositories.model_version_repository import ModelVersionRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.system_event_repository import SystemEventRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "AuditRepository",
    "BaseRepository",
    "ConsentRepository",
    "EyeImageRepository",
    "ModelVersionRepository",
    "PatientRepository",
    "PredictionRepository",
    "RefreshTokenRepository",
    "ReportRepository",
    "RoleRepository",
    "SystemEventRepository",
    "UserRepository",
]
