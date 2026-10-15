"""Model version registry service.

Owns which inference artifact is approved and active. Performance numbers are
never fabricated; only externally-provided metadata is stored verbatim.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import (
    ACTION_MODEL_ACTIVATE,
    ACTION_MODEL_REGISTER,
    RESOURCE_MODEL_VERSION,
)
from app.audit.audit_logger import AuditLogger
from app.exceptions.base import ConflictError, NotFoundError
from app.exceptions.inference import ModelNotReadyError
from app.models.model_version import ModelStatus, ModelVersion
from app.models.user import User
from app.repositories.model_version_repository import ModelVersionRepository
from app.utils.datetime import utcnow


class ModelVersionService:
    """Registry operations for model versions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._models = ModelVersionRepository(session)
        self._audit = AuditLogger(session)

    async def get_active(self) -> Optional[ModelVersion]:
        return await self._models.get_active()

    async def require_active(self) -> ModelVersion:
        active = await self._models.get_active()
        if active is None:
            raise ModelNotReadyError()
        return active

    async def get_by_version(self, version: str) -> Optional[ModelVersion]:
        return await self._models.get_by_version(version)

    async def list_versions(
        self, *, limit: int = 100, offset: int = 0
    ) -> Sequence[ModelVersion]:
        return await self._models.list_versions(limit=limit, offset=offset)

    async def register(
        self,
        *,
        version: str,
        name: str = "",
        artifact_uri: Optional[str] = None,
        checksum: Optional[str] = None,
        input_contract_version: Optional[str] = None,
        output_contract_version: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        actor: Optional[User] = None,
    ) -> ModelVersion:
        version = version.strip()
        if await self._models.get_by_version(version) is not None:
            raise ConflictError("A model with this version already exists.")

        model = await self._models.create(
            version=version,
            name=name,
            status=ModelStatus.CANDIDATE,
            artifact_uri=artifact_uri,
            checksum=checksum,
            input_contract_version=input_contract_version,
            output_contract_version=output_contract_version,
            extra_metadata=metadata,
        )
        await self._audit.record(
            ACTION_MODEL_REGISTER,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_MODEL_VERSION,
            resource_id=str(model.id),
            metadata={"version": version},
        )
        await self._session.commit()
        return model

    async def activate(
        self, model: ModelVersion, *, actor: Optional[User] = None
    ) -> ModelVersion:
        await self._models.activate(model, approved_at=utcnow())
        await self._audit.record(
            ACTION_MODEL_ACTIVATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_MODEL_VERSION,
            resource_id=str(model.id),
            metadata={"version": model.version},
        )
        await self._session.commit()
        return model

    async def activate_by_version(
        self, version: str, *, actor: Optional[User] = None
    ) -> ModelVersion:
        model = await self._models.get_by_version(version)
        if model is None:
            raise NotFoundError("The requested model version was not found.")
        return await self.activate(model, actor=actor)
