"""Inference benchmarking.

Measures real latency/throughput for a given predictor and inputs. Reported
numbers are always measured, never assumed.
"""

from __future__ import annotations

import statistics
import time
from typing import Any, Callable, Dict, List, Optional

from eyedx_ml.errors import NotConfiguredError

__all__ = ["benchmark_callable", "benchmark_predictor"]


def benchmark_callable(
    fn: Callable[[], Any],
    *,
    warmup: int = 3,
    repeats: int = 20,
) -> Dict[str, Any]:
    """Time a zero-argument callable over ``repeats`` runs after ``warmup``."""
    if repeats < 1:
        raise NotConfiguredError("repeats must be >= 1")
    for _ in range(max(0, warmup)):
        fn()
    timings: List[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        timings.append((time.perf_counter() - start) * 1000.0)
    timings.sort()
    return {
        "warmup": int(warmup),
        "repeats": int(repeats),
        "mean_ms": float(statistics.mean(timings)),
        "median_ms": float(statistics.median(timings)),
        "min_ms": float(timings[0]),
        "max_ms": float(timings[-1]),
        "p95_ms": float(timings[min(len(timings) - 1, int(0.95 * len(timings)))]),
    }


def benchmark_predictor(
    predictor,
    input_tensor,
    *,
    warmup: int = 3,
    repeats: int = 20,
    raw_image: Optional[Any] = None,
) -> Dict[str, Any]:
    def _run():
        return predictor.predict(input_tensor, raw_image=raw_image)

    return benchmark_callable(_run, warmup=warmup, repeats=repeats)
