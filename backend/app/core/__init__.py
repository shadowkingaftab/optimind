"""Core cross-cutting concerns for the EyeDx backend.

Exposes configuration, security helpers, logging, request context,
permission vocabulary and exception handling registration.
"""

from __future__ import annotations

from app.core.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
