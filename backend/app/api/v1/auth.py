"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.dependencies import AuthServiceDep
from app.authentication.current_user import CurrentUserDep
from app.core.settings import get_settings
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _to_token_response(tokens, *, expires_in: int) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=expires_in,
    )


@router.post("/login", response_model=TokenResponse, summary="Authenticate")
async def login(
    payload: LoginRequest,
    request: Request,
    service: AuthServiceDep,
) -> TokenResponse:
    _, tokens = await service.login(
        email=payload.email,
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    return _to_token_response(
        tokens, expires_in=get_settings().jwt_expiry_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh session")
async def refresh(
    payload: RefreshRequest,
    request: Request,
    service: AuthServiceDep,
) -> TokenResponse:
    _, tokens = await service.refresh(
        refresh_token=payload.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    return _to_token_response(
        tokens, expires_in=get_settings().jwt_expiry_minutes * 60
    )


@router.post("/logout", response_model=MessageResponse, summary="End session")
async def logout(
    payload: LogoutRequest,
    service: AuthServiceDep,
    user: CurrentUserDep,
) -> MessageResponse:
    await service.logout(refresh_token=payload.refresh_token, user=user)
    return MessageResponse(message="Signed out.")


@router.get("/me", response_model=UserRead, summary="Current user")
async def me(user: CurrentUserDep) -> UserRead:
    return UserRead.from_user(user)
