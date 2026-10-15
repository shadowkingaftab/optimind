"""User administration endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.api.dependencies import PageParamsDep, SessionServiceDep, UserServiceDep
from app.authentication.current_user import CurrentUserDep
from app.authorization.access_control import require_permission
from app.core.permissions import USERS_READ, USERS_WRITE
from app.schemas.auth import SessionInfo
from app.schemas.pagination import Page
from app.schemas.user import (
    RoleAssignRequest,
    UserCreate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=201,
    summary="Create a user",
    dependencies=[Depends(require_permission(USERS_WRITE))],
)
async def create_user(
    payload: UserCreate,
    service: UserServiceDep,
    actor: CurrentUserDep,
) -> UserRead:
    user = await service.create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role_name=payload.role,
        is_superuser=payload.is_superuser,
        actor=actor,
    )
    return UserRead.from_user(user)


@router.get(
    "",
    response_model=Page[UserRead],
    summary="List users",
    dependencies=[Depends(require_permission(USERS_READ))],
)
async def list_users(
    service: UserServiceDep, params: PageParamsDep
) -> Page[UserRead]:
    users = await service.list_users(limit=params.limit, offset=params.offset)
    return Page.create(
        [UserRead.from_user(user) for user in users],
        total=len(users),
        page=params.page,
        page_size=params.page_size,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user",
    dependencies=[Depends(require_permission(USERS_READ))],
)
async def get_user(user_id: uuid.UUID, service: UserServiceDep) -> UserRead:
    user = await service.get(user_id)
    return UserRead.from_user(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    dependencies=[Depends(require_permission(USERS_WRITE))],
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    service: UserServiceDep,
    actor: CurrentUserDep,
) -> UserRead:
    user = await service.get(user_id)
    updated = await service.update_user(
        user,
        full_name=payload.full_name,
        is_active=payload.is_active,
        actor=actor,
    )
    return UserRead.from_user(updated)


@router.post(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Assign a role",
    dependencies=[Depends(require_permission(USERS_WRITE))],
)
async def assign_role(
    user_id: uuid.UUID,
    payload: RoleAssignRequest,
    service: UserServiceDep,
    actor: CurrentUserDep,
) -> UserRead:
    user = await service.get(user_id)
    updated = await service.assign_role(
        user, role_name=payload.role, actor=actor
    )
    return UserRead.from_user(updated)


@router.get(
    "/{user_id}/sessions",
    response_model=list[SessionInfo],
    summary="List active sessions",
    dependencies=[Depends(require_permission(USERS_READ))],
)
async def list_sessions(
    user_id: uuid.UUID,
    service: UserServiceDep,
    sessions_service: SessionServiceDep,
) -> list[SessionInfo]:
    user = await service.get(user_id)
    sessions = await sessions_service.list_sessions(user.id)
    return [SessionInfo.model_validate(session) for session in sessions]
