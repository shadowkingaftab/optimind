"""User schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import User


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    full_name: str = Field(default="", max_length=255)
    role: Optional[str] = Field(default=None, max_length=64)
    is_superuser: bool = False


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class RoleAssignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Optional[str] = Field(default=None, max_length=64)


class UserRead(BaseModel):
    """A user as exposed to clients. Never includes the password hash."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    role: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserRead":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            role=user.role.name if user.role is not None else None,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
