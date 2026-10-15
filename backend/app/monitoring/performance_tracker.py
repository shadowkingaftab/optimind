"""Lightweight performance timing utilities.

Timers are stateless and safe in async code. No external telemetry backends
are attached by default.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from app.monitoring.metrics import MetricsRegistry

__all__ = ["async_timed"]


@asynccontextmanager
async def async_timed(
    registry: MetricsRegistry, name: str
) -> AsyncIterator[dict[str, Any]]:
    start = time.perf_counter()
    ctx: dict[str, Any] = {"name": name}
    try:
        yield ctx
    finally:
        duration_ms = (time.perf_counter() - start) * 1000.0
        ctx["duration_ms"] = duration_ms
        registry.observe(f"{name}.duration_ms", duration_ms)
        registry.inc(f"{name}.count")
