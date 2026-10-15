"""Audit action and resource vocabulary.

Central definitions keep audit records consistent and machine-aggregatable.
Action values are stable, snake_case strings; changing them is a breaking
change for audit consumers.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
ACTION_LOGIN_SUCCESS: Final[str] = "auth.login.success"
ACTION_LOGIN_FAILURE: Final[str] = "auth.login.failure"
ACTION_LOGOUT: Final[str] = "auth.logout"
ACTION_TOKEN_REFRESH: Final[str] = "auth.token.refresh"

ACTION_USER_CREATE: Final[str] = "user.create"
ACTION_USER_UPDATE: Final[str] = "user.update"
ACTION_USER_DEACTIVATE: Final[str] = "user.deactivate"
ACTION_ROLE_ASSIGN: Final[str] = "user.role.assign"

ACTION_PATIENT_CREATE: Final[str] = "patient.create"
ACTION_PATIENT_UPDATE: Final[str] = "patient.update"

ACTION_CONSENT_GRANT: Final[str] = "consent.grant"
ACTION_CONSENT_WITHDRAW: Final[str] = "consent.withdraw"

ACTION_UPLOAD_CREATE: Final[str] = "upload.create"

ACTION_PREDICTION_CREATE: Final[str] = "prediction.create"

ACTION_REPORT_GENERATE: Final[str] = "report.generate"

ACTION_MODEL_REGISTER: Final[str] = "model.register"
ACTION_MODEL_ACTIVATE: Final[str] = "model.activate"

# ---------------------------------------------------------------------------
# Resource types
# ---------------------------------------------------------------------------
RESOURCE_USER: Final[str] = "user"
RESOURCE_PATIENT: Final[str] = "patient"
RESOURCE_CONSENT: Final[str] = "consent"
RESOURCE_EYE_IMAGE: Final[str] = "eye_image"
RESOURCE_PREDICTION: Final[str] = "prediction"
RESOURCE_REPORT: Final[str] = "report"
RESOURCE_MODEL_VERSION: Final[str] = "model_version"
RESOURCE_SESSION: Final[str] = "session"

# ---------------------------------------------------------------------------
# Recorded status
# ---------------------------------------------------------------------------
STATUS_SUCCESS: Final[str] = "success"
STATUS_FAILURE: Final[str] = "failure"
STATUS_DENIED: Final[str] = "denied"
