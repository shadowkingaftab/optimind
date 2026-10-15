"""Model version endpoints.

The registry tracks which artifact is approved and active. Metadata is only
returned when it was provided for the version; performance metrics are never
synthesised.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import ModelVersionServiceDep
from app.authentication.current_user import CurrentUserDep
from app.authorization.access_control import require_permission
from app.core.permissions import MODELS_MANAGE, MODELS_READ
from app.exceptions.base import NotFoundError
from app.schemas.model_version import (
    ModelCapabilities,
    ModelMetadata,
    ModelVersionRead,
    ModelVersionRegister,
)

router = APIRouter(prefix="/models", tags=["Models"])


@router.get(
    "",
    response_model=list[ModelVersionRead],
    summary="List model versions",
    dependencies=[Depends(require_permission(MODELS_READ))],
)
async def list_model_versions(
    service: ModelVersionServiceDep,
) -> list[ModelVersionRead]:
    versions = await service.list_versions()
    return [ModelVersionRead.model_validate(v) for v in versions]


@router.get(
    "/active",
    response_model=ModelVersionRead,
    summary="Get the active model version",
    dependencies=[Depends(require_permission(MODELS_READ))],
)
async def get_active_model(service: ModelVersionServiceDep) -> ModelVersionRead:
    active = await service.get_active()
    if active is None:
        raise NotFoundError("No active model version is configured.")
    return ModelVersionRead.model_validate(active)


@router.post(
    "",
    response_model=ModelVersionRead,
    status_code=201,
    summary="Register a model version",
    dependencies=[Depends(require_permission(MODELS_MANAGE))],
)
async def register_model(
    payload: ModelVersionRegister,
    service: ModelVersionServiceDep,
    actor: CurrentUserDep,
) -> ModelVersionRead:
    model = await service.register(
        version=payload.version,
        name=payload.name,
        artifact_uri=payload.artifact_uri,
        checksum=payload.checksum,
        input_contract_version=payload.input_contract_version,
        output_contract_version=payload.output_contract_version,
        metadata=payload.metadata,
        actor=actor,
    )
    return ModelVersionRead.model_validate(model)


@router.post(
    "/{version}/activate",
    response_model=ModelVersionRead,
    summary="Activate a model version",
    dependencies=[Depends(require_permission(MODELS_MANAGE))],
)
async def activate_model(
    version: str,
    service: ModelVersionServiceDep,
    actor: CurrentUserDep,
) -> ModelVersionRead:
    model = await service.activate_by_version(version, actor=actor)
    return ModelVersionRead.model_validate(model)


@router.get(
    "/{version}/metadata",
    response_model=ModelMetadata,
    summary="Get model metadata",
    dependencies=[Depends(require_permission(MODELS_READ))],
)
async def get_model_metadata(
    version: str, service: ModelVersionServiceDep
) -> ModelMetadata:
    model = await service.get_by_version(version)
    if model is None:
        raise NotFoundError("The requested model version was not found.")
    metadata = model.extra_metadata or {}
    return ModelMetadata(
        model_id=str(metadata.get("model_id", model.name or model.version)),
        model_version=model.version,
        created_at=model.created_at,
        labels=list(metadata.get("labels", [])),
        preprocessing=dict(metadata.get("preprocessing", {})),
        capabilities=ModelCapabilities(**(metadata.get("capabilities", {}) or {})),
        description=metadata.get("description"),
    )
