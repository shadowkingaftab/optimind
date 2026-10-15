"""Validation and image-quality related exceptions.

These cover request/payload validation as well as image quality rejection.
They never embed patient data; only structural, non-sensitive descriptions.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from app.exceptions.base import APIException


class RequestValidationError(APIException):
    status_code = 422
    error_code = "validation_failed"
    default_message = "The request failed validation."


class UnsupportedImageFormatError(APIException):
    status_code = 415
    error_code = "unsupported_image_format"
    default_message = "The provided image format is not supported."


class ImageDecodeError(APIException):
    status_code = 422
    error_code = "image_decode_failed"
    default_message = "The provided image could not be decoded."


class ImageTooLargeError(APIException):
    status_code = 413
    error_code = "image_too_large"
    default_message = "The provided image exceeds the allowed size."


class ImageQualityError(APIException):
    """Raised when an image fails the quality gate.

    Produces an honest, non-diagnostic rejection: no disease result is
    returned for a low-quality image.
    """

    status_code = 422
    error_code = "quality_insufficient"
    default_message = (
        "The image quality is insufficient for screening. "
        "Please retry with a clearer image."
    )

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        issues: Optional[list[str]] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        merged: dict[str, Any] = dict(details) if details is not None else {}
        if issues:
            merged["issues"] = list(issues)
        super().__init__(message, details=merged or None)
