"""Generic async repository.

Encapsulates common persistence operations so that services depend on
intention-revealing methods rather than raw SQLAlchemy. Repositories flush but
never commit: the unit of work is owned by the caller/service.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD repository for a single ORM model."""

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: uuid.UUID) -> Optional[ModelT]:
        return await self.session.get(self.model, entity_id)

    async def get_or_none(self, entity_id: uuid.UUID) -> Optional[ModelT]:
        return await self.session.get(self.model, entity_id)

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(self.model.id).where(self.model.id == entity_id)
        return (await self.session.execute(stmt)).scalar_one_or_none() is not None

    async def count(self, *where: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        if where:
            stmt = stmt.where(*where)
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[Any] = None,
    ) -> Sequence[ModelT]:
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()
