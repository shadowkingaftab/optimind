"""Preprocessing package: validation, decoding, sanitization and quality."""

from __future__ import annotations

from app.preprocessing.file_validator import ValidatedUpload, validate_upload
from app.preprocessing.image_decoder import decode_image
from app.preprocessing.image_metadata import aspect_ratio, extract_metadata
from app.preprocessing.image_quality_gateway import assess_quality
from app.preprocessing.image_sanitizer import encode_png, sanitize_image
from app.preprocessing.preprocessing_contract import (
    ImageInfo,
    PreprocessedImage,
    QualityResult,
)

__all__ = [
    "ImageInfo",
    "PreprocessedImage",
    "QualityResult",
    "ValidatedUpload",
    "aspect_ratio",
    "assess_quality",
    "decode_image",
    "encode_png",
    "extract_metadata",
    "sanitize_image",
    "validate_upload",
]
