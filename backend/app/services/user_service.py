"""User administration service."""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import (
    ACTION_ROLE_ASSIGN,
    ACTION_USER_CREATE,
    ACTION_USER_DEACTIVATE,
    ACTION_USER_UPDATE,
    RESOURCE_USER,
)
from app.audit.audit_logger import AuditLogger
from app.authentication.password_hasher import hash_password, validate_password
from app.exceptions.base import ConflictError, NotFoundError
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class UserService:
    """Creates and maintains user accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._roles = RoleRepository(session)
        self._audit = AuditLogger(session)

    async def get(self, user_id: uuid.UUID) -> User:
        user = await self._users.get(user_id)
        if user is None:
            raise NotFoundError("The requested user was not found.")
        return user

    async def list_users(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        include_inactive: bool = True,
    ) -> Sequence[User]:
        return await self._users.list_users(
            limit=limit, offset=offset, include_inactive=include_inactive
        )

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str = "",
        role_name: Optional[str] = None,
        is_superuser: bool = False,
        actor: Optional[User] = None,
    ) -> User:
        normalized = email.strip().lower()
        if await self._users.get_by_email(normalized) is not None:
            raise ConflictError("An account with this email already exists.")

        validate_password(password)
        role_id: Optional[uuid.UUID] = None
        if role_name:
            role = await self._roles.get_by_name(role_name)
            if role is None:
                raise NotFoundError("The requested role does not exist.")
            role_id = role.id

        user = await self._users.create(
            email=normalized,
            hashed_password=hash_password(password),
            full_name=full_name,
            role_id=role_id,
            is_superuser=is_superuser,
        )
        await self._audit.record(
            ACTION_USER_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_USER,
            resource_id=str(user.id),
            metadata={"role": role_name} if role_name else None,
        )
        await self._session.commit()
        return user

    async def update_user(
        self,
        user: User,
        *,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        actor: Optional[User] = None,
    ) -> User:
        if full_name is not None:
            user.full_name = full_name
        if is_active is not None:
            user.is_active = is_active
        await self._session.flush()
        await self._audit.record(
            ACTION_USER_UPDATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_USER,
            resource_id=str(user.id),
        )
        await self._session.commit()
        return user

    async def set_active(
        self, user: User, *, is_active: bool, actor: Optional[User] = None
    ) -> User:
        await self._users.set_active(user, is_active)
        action = ACTION_USER_DEACTIVATE if not is_active else ACTION_USER_UPDATE
        await self._audit.record(
            action,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_USER,
            resource_id=str(user.id),
        )
        await self._session.commit()
        return user

    async def assign_role(
        self,
        user: User,
        *,
        role_name: Optional[str],
        actor: Optional[User] = None,
    ) -> User:
        role_id: Optional[uuid.UUID] = None
        if role_name:
            role = await self._roles.get_by_name(role_name)
            if role is None:
                raise NotFoundError("The requested role does not exist.")
            role_id = role.id
        await self._users.set_role(user, role_id)
        await self._audit.record(
            ACTION_ROLE_ASSIGN,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_USER,
            resource_id=str(user.id),
            metadata={"role": role_name},
        )
        await self._session.commit()
        return user
