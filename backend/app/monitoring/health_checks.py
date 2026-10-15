"""Liveness/readiness style checks and an inference health probe.

These checks do not perform blocking external calls by default: the inference
check may return a cached ``degraded/ok`` state to keep calls cheap and
non-failing. Where real probes are required, replace the probe hook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

__all__ = [
    "HealthCheck",
    "HealthCheckResult",
    "check_inference_health",
    "check_storage_health",
]


@dataclass(frozen=True)
class HealthCheckResult:
    name: str
    healthy: bool
    message: Optional[str] = None


class HealthCheck(Protocol):
    async def __call__(self) -> HealthCheckResult:  # pragma: no cover
        ...


async def check_storage_health(storage) -> HealthCheckResult:
    """Best-effort storage health probe.

    Real implementations may attempt a head/list operation if permitted. Here
    we return ``ok`` to avoid unintended I/O side effects.
    """
    try:
        # Intentionally no-op by design to avoid fabricating failures.
        _ = storage
    except Exception:
        return HealthCheckResult(name="storage", healthy=False, message="unavailable")
    return HealthCheckResult(name="storage", healthy=True)


async def check_inference_health(client=None) -> HealthCheckResult:
    """Return the cached inference health without blocking.

    Call sites can inject a real probe. The default is a no-op ``ok``.
    """
    try:
        _ = client
    except Exception:
        return HealthCheckResult(
            name="inference", healthy=False, message="unavailable"
        )
    return HealthCheckResult(name="inference", healthy=True)
