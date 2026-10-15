"""In-memory metrics registry.

Tracks simple counters, histograms and gauges. Values are process-local and
volatile; they are not persisted or exported to external systems. Histograms
store raw samples so percentiles are computed on demand.
"""

from __future__ import annotations

import math
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Optional, Sequence

__all__ = ["Gauge", "Histogram", "MetricRegistry", "MetricsRegistry"]


@dataclass(slots=True)
class Gauge:
    value: float = 0.0


@dataclass(slots=True)
class Counter:
    value: int = 0


class Histogram:
    def __init__(self, max_samples: int = 1000) -> None:
        self._samples: deque[float] = deque(maxlen=max_samples)
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._samples.append(float(value))

    def count(self) -> int:
        with self._lock:
            return len(self._samples)

    def sum(self) -> float:
        with self._lock:
            return float(sum(self._samples))

    def avg(self) -> float:
        with self._lock:
            if not self._samples:
                return 0.0
            return self.sum() / len(self._samples)

    def p(self, percentile: float) -> float:
        if not (0 <= percentile <= 100):
            return 0.0
        with self._lock:
            samples = list(self._samples)
        if not samples:
            return 0.0
        samples.sort()
        k = (len(samples) - 1) * percentile / 100.0
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return samples[int(k)]
        return samples[f] * (c - k) + samples[c] * (k - f)

    def snapshot(self) -> dict[str, Any]:
        return {
            "count": self.count(),
            "sum": self.sum(),
            "avg": self.avg(),
            "p50": self.p(50),
            "p90": self.p(90),
            "p99": self.p(99),
        }


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, Counter] = defaultdict(Counter)
        self._gauges: dict[str, Gauge] = defaultdict(Gauge)
        self._histograms: dict[str, Histogram] = defaultdict(Histogram)
        self._lock = threading.Lock()

    def inc(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name].value += int(amount)

    def get_counter(self, name: str) -> int:
        with self._lock:
            return self._counters[name].value

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name].value = float(value)

    def get_gauge(self, name: str) -> float:
        with self._lock:
            return self._gauges[name].value

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms[name].observe(value)

    def histogram_snapshot(self, name: str) -> dict[str, Any]:
        with self._lock:
            return self._histograms[name].snapshot()

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


MetricRegistry = MetricsRegistry

__all__ = ["Gauge", "Histogram", "MetricRegistry", "MetricsRegistry"]
