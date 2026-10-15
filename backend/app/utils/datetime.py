"""UTC date/time helpers.

All persisted timestamps are timezone-aware and stored in UTC. These helpers
keep that invariant explicit and avoid naive/aware comparison bugs.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def ensure_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Coerce ``value`` to a timezone-aware UTC datetime.

    Naive datetimes are assumed to already be UTC.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_expired(value: Optional[datetime], *, now: Optional[datetime] = None) -> bool:
    """Return True when ``value`` is in the past."""
    if value is None:
        return False
    reference = ensure_utc(now) or utcnow()
    return ensure_utc(value) <= reference


def seconds_until(value: datetime, *, now: Optional[datetime] = None) -> int:
    """Return whole seconds from ``now`` until ``value`` (may be negative)."""
    reference = ensure_utc(now) or utcnow()
    delta = ensure_utc(value) - reference
    return int(delta.total_seconds())


def to_iso(value: Optional[datetime]) -> Optional[str]:
    """Return an ISO-8601 string (UTC) or ``None``."""
    aware = ensure_utc(value)
    return aware.isoformat() if aware is not None else None
