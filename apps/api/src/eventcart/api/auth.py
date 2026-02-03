from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.core.deps import get_current_user
from eventcart.core.settings import settings
from eventcart.db.session import get_session
from eventcart.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from eventcart.services.auth_service import authenticate_user, logout, refresh_tokens, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, response: Response, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    async with session.begin():
        access, refresh = await register_user(session, payload.email, payload.password)
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.api_refresh_token_expire_days,
        path="/",
    )
    return TokenResponse(access_token=access)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    async with session.begin():
        access, refresh = await authenticate_user(session, payload.email, payload.password)
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.api_refresh_token_expire_days,
        path="/",
    )
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token", "")
    async with session.begin():
        access, new_refresh = await refresh_tokens(session, refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.api_refresh_token_expire_days,
        path="/",
    )
    return TokenResponse(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_route(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
) -> Response:
    refresh_token = request.cookies.get("refresh_token", "")
    async with session.begin():
        await logout(session, refresh_token)
    response.delete_cookie("refresh_token", path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=str(current_user.id), email=current_user.email)
