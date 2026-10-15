"""API v1 router aggregation.

Resource routers are attached here. This module owns the v1 prefix and shared
tags so individual routers stay location-agnostic. ``app.api.router`` mounts
this tree under ``/api/v1``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.models import router as models_router
from app.api.v1.patients import router as patients_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.reports import router as reports_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(patients_router)
api_router.include_router(uploads_router)
api_router.include_router(predictions_router)
api_router.include_router(models_router)
api_router.include_router(reports_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]
