"""Backend-wide constants.

These values are intentionally non-clinical. Prediction *states* mirror the
shared contract (``contracts/json-schemas/prediction-response.schema.json``)
and must not be extended here without updating the contract first.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Application / API versioning
# ---------------------------------------------------------------------------
APP_VERSION: Final[str] = "0.1.0"
API_VERSION: Final[str] = "v1"
API_PREFIX: Final[str] = "/api/v1"
API_TITLE: Final[str] = "EyeDx Backend API"
API_DESCRIPTION: Final[str] = (
    "EyeDx screening API. This software is a screening and research aid only "
    "and does not provide a medical diagnosis."
)

# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------
REQUEST_ID_HEADER: Final[str] = "X-Request-ID"
CORRELATION_ID_HEADER: Final[str] = "X-Correlation-ID"

# ---------------------------------------------------------------------------
# Prediction states (must match the shared contract enums)
# ---------------------------------------------------------------------------
PREDICTION_STATUS_SUCCESS: Final[str] = "success"
PREDICTION_STATUS_LOW_QUALITY: Final[str] = "low_quality"
PREDICTION_STATUS_UNCERTAIN: Final[str] = "uncertain"
PREDICTION_STATUS_ABSTAINED: Final[str] = "abstained"
PREDICTION_STATUS_FAILED: Final[str] = "failed"

PREDICTION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        PREDICTION_STATUS_SUCCESS,
        PREDICTION_STATUS_LOW_QUALITY,
        PREDICTION_STATUS_UNCERTAIN,
        PREDICTION_STATUS_ABSTAINED,
        PREDICTION_STATUS_FAILED,
    }
)

# Terminal states that cannot transition further.
PREDICTION_TERMINAL_STATUSES: Final[frozenset[str]] = frozenset(
    {
        PREDICTION_STATUS_SUCCESS,
        PREDICTION_STATUS_LOW_QUALITY,
        PREDICTION_STATUS_UNCERTAIN,
        PREDICTION_STATUS_ABSTAINED,
        PREDICTION_STATUS_FAILED,
    }
)

# ---------------------------------------------------------------------------
# Image upload constraints (structural only; not clinical thresholds)
# ---------------------------------------------------------------------------
ALLOWED_IMAGE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".jpg", ".jpeg", ".png"}
)
ALLOWED_IMAGE_MEDIA_TYPES: Final[frozenset[str]] = frozenset(
    {"image/jpeg", "image/png"}
)

# ---------------------------------------------------------------------------
# Roles (RBAC scaffolding; authoritative role set is Phase 3)
# ---------------------------------------------------------------------------
ROLE_ADMIN: Final[str] = "admin"
ROLE_CLINICIAN: Final[str] = "clinician"
ROLE_OPERATOR: Final[str] = "operator"
ROLE_RESEARCHER: Final[str] = "researcher"

DEFAULT_ROLES: Final[tuple[str, ...]] = (
    ROLE_ADMIN,
    ROLE_CLINICIAN,
    ROLE_OPERATOR,
    ROLE_RESEARCHER,
)

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# ---------------------------------------------------------------------------
# Screening limitation notice (never a diagnosis)
# ---------------------------------------------------------------------------
SCREENING_LIMITATION_NOTICE: Final[str] = (
    "This is a screening aid only. It does not provide a medical diagnosis "
    "and must be reviewed by a qualified healthcare professional."
)
