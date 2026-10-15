"""Inference package and client factory.

Selects a mock client in non-production environments when mock mode is
enabled, and the HTTP model-service client otherwise. The factory never
silently falls back from a real service to a mock in production.
"""

from __future__ import annotations

from app.core.logging_config import get_logger
from app.core.settings import get_settings
from app.inference.inference_contract import InferenceRequest, InferenceResult

logger = get_logger(__name__)

_client = None


def get_inference_client():
    """Return the configured inference client (cached)."""
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    if settings.allow_mock_inference():
        from app.inference.mock_inference_client import MockInferenceClient

        _client = MockInferenceClient(status=settings.inference_mock_result)
        logger.warning(
            "Mock inference client active (result=%s). No real model is used.",
            settings.inference_mock_result,
        )
        return _client

    from app.inference.inference_client import HttpInferenceClient

    if not settings.model_service_url:
        # validate_for_startup() should have caught this; guard anyway.
        from app.exceptions.inference import InferenceUnavailableError

        raise InferenceUnavailableError(
            "The model service URL is not configured."
        )

    _client = HttpInferenceClient(
        settings.model_service_url,
        timeout_seconds=settings.model_service_timeout_seconds,
    )
    return _client


async def close_inference_client() -> None:
    """Close and clear the cached client (used on shutdown)."""
    global _client
    if _client is not None:
        aclose = getattr(_client, "aclose", None)
        if aclose is not None:
            await aclose()
        _client = None


__all__ = [
    "InferenceRequest",
    "InferenceResult",
    "close_inference_client",
    "get_inference_client",
]
