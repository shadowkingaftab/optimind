"""HTTP client for the versioned model service.

Wraps ``httpx`` with a timeout, bounded retries for transient failures, and a
circuit breaker. Failures surface as honest ``Inference*`` exceptions; the
client never synthesises a result.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from app.core.logging_config import get_logger
from app.exceptions.inference import (
    CircuitOpenError,
    InferenceContractError,
    InferenceError,
    InferenceTimeoutError,
    InferenceUnavailableError,
)
from app.inference.circuit_breaker import CircuitBreaker
from app.inference.inference_contract import InferenceRequest, InferenceResult
from app.inference.response_mapper import map_response
from app.inference.retry_policy import RetryPolicy, run_with_retry

logger = get_logger(__name__)


class HttpInferenceClient:
    """Inference client that calls a remote model service over HTTP."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 30.0,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._retry = retry_policy or RetryPolicy()
        self._breaker = circuit_breaker or CircuitBreaker()
        self._client = http_client or httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout_seconds
        )

    @property
    def breaker(self) -> CircuitBreaker:
        return self._breaker

    async def predict(self, request: InferenceRequest) -> InferenceResult:
        if not self._breaker.allow_request():
            raise CircuitOpenError()

        async def _call() -> httpx.Response:
            return await self._client.post("/predict", json=request.to_payload())

        try:
            response = await run_with_retry(
                _call,
                policy=self._retry,
                retry_on=(httpx.TimeoutException, httpx.TransportError),
            )
        except httpx.TimeoutException as exc:
            self._breaker.record_failure()
            raise InferenceTimeoutError() from exc
        except httpx.TransportError as exc:
            self._breaker.record_failure()
            raise InferenceUnavailableError() from exc

        if response.status_code == 503:
            self._breaker.record_failure()
            raise InferenceUnavailableError()
        if response.status_code >= 400:
            # A structured client error is not a transient failure.
            self._breaker.record_success()
            raise InferenceError(
                "The model service rejected the request.",
                details={"status_code": response.status_code},
            )

        self._breaker.record_success()
        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise InferenceContractError("Model service returned invalid JSON.") from exc
        return map_response(payload)

    async def model_info(self) -> dict[str, Any]:
        if not self._breaker.allow_request():
            raise CircuitOpenError()
        try:
            response = await self._client.get("/model/info")
        except httpx.TimeoutException as exc:
            raise InferenceTimeoutError() from exc
        except httpx.TransportError as exc:
            raise InferenceUnavailableError() from exc

        if response.status_code == 503:
            raise InferenceUnavailableError()
        if response.status_code >= 400:
            raise InferenceError("Model info unavailable.")
        return response.json()

    async def health(self) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            response = await self._client.get("/health")
            ok = response.status_code == 200
            return {
                "available": ok,
                "status_code": response.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000.0, 2),
            }
        except httpx.HTTPError:
            return {
                "available": False,
                "status_code": None,
                "latency_ms": round((time.perf_counter() - started) * 1000.0, 2),
            }

    async def aclose(self) -> None:
        await self._client.aclose()
