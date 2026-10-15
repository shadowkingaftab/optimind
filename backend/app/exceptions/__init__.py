"""Exception package exports.

Import from this module so consumers do not depend on individual files:

    from app.exceptions import NotFoundError, ImageQualityError
"""

from __future__ import annotations

from app.exceptions.authentication import (
    AccountInactiveError,
    InvalidCredentialsError,
    SessionNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.exceptions.authorization import (
    ConsentExpiredError,
    ConsentRequiredError,
    PermissionDeniedError,
    RoleAssignmentError,
)
from app.exceptions.base import (
    APIException,
    APIValidationError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ConfigurationError,
    ConflictError,
    NotFoundError,
    PayloadTooLargeError,
    RateLimitError,
    ServiceUnavailableError,
    UnsupportedMediaTypeError,
)
from app.exceptions.database import (
    DatabaseError,
    DatabaseUnavailableError,
    DuplicateRecordError,
    IntegrityConstraintError,
    MigrationRequiredError,
    RecordNotFoundError,
)
from app.exceptions.inference import (
    CircuitOpenError,
    InferenceContractError,
    InferenceError,
    InferenceTimeoutError,
    InferenceUnavailableError,
    ModelNotReadyError,
)
from app.exceptions.storage import (
    ObjectNotFoundError,
    SignedUrlError,
    StorageError,
    StorageQuotaExceededError,
    StorageUnavailableError,
)
from app.exceptions.validation import (
    ImageDecodeError,
    ImageQualityError,
    ImageTooLargeError,
    RequestValidationError,
    UnsupportedImageFormatError,
)

__all__ = [
    "APIException",
    "APIValidationError",
    "AccountInactiveError",
    "AuthenticationError",
    "AuthorizationError",
    "BadRequestError",
    "CircuitOpenError",
    "ConfigurationError",
    "ConflictError",
    "ConsentExpiredError",
    "ConsentRequiredError",
    "DatabaseError",
    "DatabaseUnavailableError",
    "DuplicateRecordError",
    "ImageDecodeError",
    "ImageQualityError",
    "ImageTooLargeError",
    "InferenceContractError",
    "InferenceError",
    "InferenceTimeoutError",
    "InferenceUnavailableError",
    "IntegrityConstraintError",
    "InvalidCredentialsError",
    "MigrationRequiredError",
    "ModelNotReadyError",
    "NotFoundError",
    "ObjectNotFoundError",
    "PayloadTooLargeError",
    "PermissionDeniedError",
    "RateLimitError",
    "RecordNotFoundError",
    "RequestValidationError",
    "RoleAssignmentError",
    "ServiceUnavailableError",
    "SessionNotFoundError",
    "SignedUrlError",
    "StorageError",
    "StorageQuotaExceededError",
    "StorageUnavailableError",
    "TokenExpiredError",
    "TokenInvalidError",
    "UnsupportedImageFormatError",
    "UnsupportedMediaTypeError",
]
