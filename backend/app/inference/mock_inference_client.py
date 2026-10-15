"""Mock inference client for local development and testing.

The mock NEVER returns a successful prediction. It reports an honest
``abstained`` (default), ``uncertain`` or ``low_quality`` state so that no
synthetic clinical result is ever produced. Any other requested mode is
rejected at construction time.
"""

from __future__ import annotations

import time
from typing import Any

from app.core.constants import SCREENING_LIMITATION_NOTICE
from app.inference.inference_contract import InferenceRequest, InferenceResult

_ALLOWED_MOCK_STATUSES = frozenset({"abstained", "uncertain", "low_quality"})

_MOCK_REASONS = {
    "abstained": "mock_inference_active",
    "uncertain": "mock_uncertainty",
    "low_quality": "mock_quality_rejection",
}


class MockInferenceClient:
    """Deterministic, non-clinical mock inference client."""

    def __init__(self, *, status: str = "abstained", model_version: str = "0.0.0-mock") -> None:
        normalized = status.strip().lower()
        if normalized not in _ALLOWED_MOCK_STATUSES:
            raise ValueError(
                "Mock inference status must be one of "
                f"{sorted(_ALLOWED_MOCK_STATUSES)}; refusing to fabricate a "
                "successful prediction."
            )
        self._status = normalized
        self._model_version = model_version

    async def predict(self, request: InferenceRequest) -> InferenceResult:
        started = time.perf_counter()
        processing_ms = max(1, int((time.perf_counter() - started) * 1000))
        failure_reason = None
        if self._status == "low_quality":
            failure_reason = None
        return InferenceResult(
            request_id=request.request_id or "",
            status=self._status,
            model_id="mock",
            model_version=self._model_version,
            processing_time_ms=processing_ms,
            predictions=[],
            uncertainty={"mock": True} if self._status == "uncertain" else None,
            quality_checks={"mock": True, "acceptable": False}
            if self._status == "low_quality"
            else {"mock": True, "acceptable": True},
            abstention_reason=_MOCK_REASONS.get(self._status),
            failure_reason=failure_reason,
            limitation_notice=SCREENING_LIMITATION_NOTICE,
        )

    async def model_info(self) -> dict[str, Any]:
        return {
            "model_id": "mock",
            "model_version": self._model_version,
            "labels": [],
            "preprocessing": {},
            "capabilities": {
                "supports_uncertainty": False,
                "supports_explanation": False,
                "supports_abstention": True,
            },
            "description": "Mock inference client active. No model is loaded.",
        }

    async def health(self) -> dict[str, Any]:
        return {"available": True, "status_code": 200, "latency_ms": 0.0}

    async def aclose(self) -> None:
        return None
