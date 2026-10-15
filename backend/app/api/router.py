"""Top-level API router.

Mounts the versioned router tree. The API prefix (``/api/v1``) is applied
here so versioned routers remain portable.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.router import api_router as v1_router
from app.core.constants import API_PREFIX

api_router = APIRouter()
api_router.include_router(v1_router, prefix=API_PREFIX)

__all__ = ["api_router"]
