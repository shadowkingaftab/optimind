"""Circuit breaker for the model service.

Prevents cascading failures by short-circuiting calls after a threshold of
consecutive failures, then allowing a single probe after a cool-down.
"""

from __future__ import annotations

import time
from enum import StrEnum
from typing import Optional


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """A minimal, single-process circuit breaker."""

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        reset_timeout_seconds: float = 30.0,
        clock=time.monotonic,
    ) -> None:
        self.failure_threshold = max(1, failure_threshold)
        self.reset_timeout_seconds = max(0.0, reset_timeout_seconds)
        self._clock = clock
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at: Optional[float] = None

    @property
    def state(self) -> CircuitState:
        self._maybe_half_open()
        return self._state

    def _maybe_half_open(self) -> None:
        if (
            self._state is CircuitState.OPEN
            and self._opened_at is not None
            and (self._clock() - self._opened_at) >= self.reset_timeout_seconds
        ):
            self._state = CircuitState.HALF_OPEN

    def allow_request(self) -> bool:
        """Return True when a call may proceed."""
        self._maybe_half_open()
        return self._state is not CircuitState.OPEN

    def record_success(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._state is CircuitState.HALF_OPEN:
            self._trip()
        elif self._failures >= self.failure_threshold:
            self._trip()

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()

    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = None
