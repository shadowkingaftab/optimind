"""Retry policy for transient model-service failures.

Retries only explicitly transient exceptions (timeouts/connection errors) with
exponential backoff and jitter. Business rejections are never retried.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Awaitable, Callable, Tuple, Type, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 4.0
    jitter: bool = True

    def delay_for(self, attempt: int) -> float:
        # attempt is 1-based.
        delay = min(self.max_delay_seconds, self.base_delay_seconds * (2 ** (attempt - 1)))
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay


async def run_with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy,
    retry_on: Tuple[Type[BaseException], ...],
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Run ``operation`` with retries on ``retry_on`` exceptions."""
    last_exc: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return await operation()
        except retry_on as exc:  # noqa: PERF203
            last_exc = exc
            if attempt >= policy.max_attempts:
                break
            await sleep(policy.delay_for(attempt))
    assert last_exc is not None
    raise last_exc
