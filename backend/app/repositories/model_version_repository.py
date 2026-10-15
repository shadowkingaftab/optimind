"""Model version registry persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import select, update

from app.models.model_version import ModelStatus, ModelVersion
from app.repositories.base_repository import BaseRepository


class ModelVersionRepository(BaseRepository[ModelVersion]):
    model = ModelVersion

    async def get_by_version(self, version: str) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).where(ModelVersion.version == version)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_active(self) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).where(
            ModelVersion.is_active.is_(True),
            ModelVersion.status == ModelStatus.APPROVED,
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def list_versions(
        self, *, limit: int = 100, offset: int = 0
    ) -> Sequence[ModelVersion]:
        stmt = (
            select(ModelVersion)
            .order_by(ModelVersion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def create(
        self,
        *,
        version: str,
        name: str = "",
        status: ModelStatus = ModelStatus.CANDIDATE,
        artifact_uri: Optional[str] = None,
        checksum: Optional[str] = None,
        input_contract_version: Optional[str] = None,
        output_contract_version: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ModelVersion:
        model = ModelVersion(
            version=version,
            name=name,
            status=status,
            artifact_uri=artifact_uri,
            checksum=checksum,
            input_contract_version=input_contract_version,
            output_contract_version=output_contract_version,
            extra_metadata=extra_metadata,
        )
        return await self.add(model)

    async def activate(self, model: ModelVersion, *, approved_at: datetime) -> None:
        """Mark ``model`` as the single active approved version."""
        await self.session.execute(
            update(ModelVersion)
            .where(ModelVersion.is_active.is_(True))
            .values(is_active=False)
        )
        model.is_active = True
        model.status = ModelStatus.APPROVED
        model.approved_at = approved_at
        await self.session.flush()
