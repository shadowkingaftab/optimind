"""User persistence."""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy import func, select

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.utils.datetime import utcnow


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        normalized = email.strip().lower()
        stmt = select(User).where(func.lower(User.email) == normalized)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str = "",
        role_id: Optional[uuid.UUID] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            role_id=role_id,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        return await self.add(user)

    async def list_users(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        include_inactive: bool = True,
    ) -> Sequence[User]:
        stmt = select(User).order_by(User.created_at.desc())
        if not include_inactive:
            stmt = stmt.where(User.is_active.is_(True))
        stmt = stmt.offset(offset).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()

    async def record_login(self, user: User) -> None:
        user.last_login_at = utcnow()
        await self.session.flush()

    async def set_active(self, user: User, is_active: bool) -> None:
        user.is_active = is_active
        await self.session.flush()

    async def set_role(self, user: User, role_id: Optional[uuid.UUID]) -> None:
        user.role_id = role_id
        await self.session.flush()
