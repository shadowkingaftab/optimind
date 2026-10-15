"""Inference / model-service related exceptions.

These represent honest unavailable or failure states. They must never be
converted into a fabricated successful prediction.
"""

from __future__ import annotations

from typing import Optional

from app.exceptions.base import APIException


class InferenceError(APIException):
    status_code = 503
    error_code = "inference_error"
    default_message = "The model service could not complete the request."


class InferenceUnavailableError(APIException):
    status_code = 503
    error_code = "inference_unavailable"
    default_message = "The model service is currently unavailable."


class InferenceTimeoutError(APIException):
    status_code = 504
    error_code = "inference_timeout"
    default_message = "The model service timed out while processing the request."


class ModelNotReadyError(APIException):
    status_code = 503
    error_code = "model_not_ready"
    default_message = "No approved model is currently loaded for inference."


class InferenceContractError(APIException):
    """Raised when a model-service response violates the shared contract."""

    status_code = 502
    error_code = "inference_contract_violation"
    default_message = "The model service returned an incompatible response."


class CircuitOpenError(APIException):
    status_code = 503
    error_code = "inference_circuit_open"
    default_message = (
        "Inference is temporarily paused after repeated failures. "
        "Please retry later."
    )

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message)
