"""Request-scoped context.

Uses :mod:`contextvars` so request identifiers and the authenticated subject
propagate through async call chains (middleware, services, logging) without
being passed explicitly.
"""

from __future__ import annotations

import contextvars
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Iterator, Optional

_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)
_user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)


@dataclass(frozen=True)
class RequestContext:
    """Immutable snapshot of the current request context."""

    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None


def get_request_id() -> Optional[str]:
    return _request_id_var.get()


def set_request_id(value: Optional[str]) -> contextvars.Token:
    return _request_id_var.set(value)


def get_correlation_id() -> Optional[str]:
    return _correlation_id_var.get()


def set_correlation_id(value: Optional[str]) -> contextvars.Token:
    return _correlation_id_var.set(value)


def get_user_id() -> Optional[str]:
    return _user_id_var.get()


def set_user_id(value: Optional[str]) -> contextvars.Token:
    return _user_id_var.set(value)


def reset_request_id(token: contextvars.Token) -> None:
    _request_id_var.reset(token)


def reset_correlation_id(token: contextvars.Token) -> None:
    _correlation_id_var.reset(token)


def reset_user_id(token: contextvars.Token) -> None:
    _user_id_var.reset(token)


def get_context() -> RequestContext:
    """Return the current context snapshot."""
    return RequestContext(
        request_id=get_request_id(),
        correlation_id=get_correlation_id(),
        user_id=get_user_id(),
    )


@contextmanager
def bind_context(
    *,
    request_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Iterator[RequestContext]:
    """Temporarily bind context values, restoring prior values on exit."""
    tokens: list[tuple[contextvars.ContextVar, contextvars.Token]] = []
    if request_id is not None:
        tokens.append((_request_id_var, _request_id_var.set(request_id)))
    if correlation_id is not None:
        tokens.append((_correlation_id_var, _correlation_id_var.set(correlation_id)))
    if user_id is not None:
        tokens.append((_user_id_var, _user_id_var.set(user_id)))
    try:
        yield get_context()
    finally:
        # Restore in reverse order of assignment.
        for var, token in reversed(tokens):
            var.reset(token)


def with_user(user_id: Optional[str]) -> None:
    """Attach the authenticated subject to the current context."""
    _user_id_var.set(user_id)
