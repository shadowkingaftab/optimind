"""Tracing stubs.

No-op tracer so instrumentation does not create external dependencies or
leak information.
"""

from __future__ import annotations

from typing import Any, ContextManager, Optional

__all__ = ["Span", "Tracer", "get_tracer"]


class Span:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> "Span":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover
        return None


class Tracer:
    def start_span(self, name: str) -> ContextManager[Span]:
        return Span(name)


def get_tracer() -> Tracer:
    return Tracer()
