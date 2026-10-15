"""Build the model-service request payload from sanitized image bytes."""

from __future__ import annotations

import base64

from app.inference.inference_contract import InferenceRequest
from app.utils.file_utils import guess_media_type


def build_request(
    *,
    image_bytes: bytes,
    consent_id: str,
    image_ext: str,
    request_id: str | None = None,
) -> InferenceRequest:
    """Base64-encode the image and assemble a contract-valid request."""
    media = guess_media_type(image_ext)
    image_format = "png" if media == "image/png" else "jpeg"
    return InferenceRequest(
        image_base64=base64.b64encode(image_bytes).decode("ascii"),
        consent_id=str(consent_id),
        image_format=image_format,
        request_id=str(request_id) if request_id else None,
    )
