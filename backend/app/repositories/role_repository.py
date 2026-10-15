"""Role persistence."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select

from app.models.role import Role
from app.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name.strip().lower())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_roles(self) -> Sequence[Role]:
        stmt = select(Role).order_by(Role.name)
        return (await self.session.execute(stmt)).scalars().all()

    async def ensure(
        self, *, name: str, description: str = "", is_system: bool = False
    ) -> Role:
        existing = await self.get_by_name(name)
        if existing is not None:
            return existing
        role = Role(
            name=name.strip().lower(),
            description=description,
            is_system=is_system,
        )
        return await self.add(role)
