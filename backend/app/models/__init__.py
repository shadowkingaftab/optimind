"""ORM models.

Importing this package registers every model with the shared metadata so
that Alembic autogenerate and ``Base.metadata.create_all`` see the full
schema.
"""

from __future__ import annotations

from app.models.audit_log import AuditLog
from app.models.consent import Consent, ConsentStatus, ConsentType
from app.models.eye_image import EyeImage, EyeSide, QualityStatus
from app.models.model_version import ModelStatus, ModelVersion
from app.models.patient import Patient
from app.models.prediction import Prediction, PredictionStatus, RiskLevel
from app.models.prediction_item import PredictionItem
from app.models.refresh_token import RefreshToken
from app.models.report import Report, ReportStatus
from app.models.role import Role
from app.models.system_event import EventSeverity, SystemEvent
from app.models.user import User

__all__ = [
    "AuditLog",
    "Consent",
    "ConsentStatus",
    "ConsentType",
    "EventSeverity",
    "EyeImage",
    "EyeSide",
    "ModelStatus",
    "ModelVersion",
    "Patient",
    "Prediction",
    "PredictionItem",
    "PredictionStatus",
    "QualityStatus",
    "RefreshToken",
    "Report",
    "ReportStatus",
    "RiskLevel",
    "Role",
    "SystemEvent",
    "User",
]
