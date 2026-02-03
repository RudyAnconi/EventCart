from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from eventcart.core.settings import settings
from eventcart.repo.session_repo import create_session, get_session_by_id, revoke_session
from eventcart.repo.user_repo import create_user, get_user_by_email


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def register_user(session: AsyncSession, email: str, password: str) -> tuple[str, str]:
    existing = await get_user_by_email(session, email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    password_hash = hash_password(password)
    user = await create_user(session, email, password_hash)

    session_id = str(uuid.uuid4())
    refresh = create_refresh_token(subject=str(user.id), session_id=session_id)
    refresh_hash = _hash_token(refresh)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.api_refresh_token_expire_days)
    await create_session(session, str(user.id), refresh_hash, expires_at, session_id=session_id)

    access = create_access_token(subject=str(user.id))
    return access, refresh


async def authenticate_user(session: AsyncSession, email: str, password: str) -> tuple[str, str]:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session_id = str(uuid.uuid4())
    refresh = create_refresh_token(subject=str(user.id), session_id=session_id)
    refresh_hash = _hash_token(refresh)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.api_refresh_token_expire_days)
    await create_session(session, str(user.id), refresh_hash, expires_at, session_id=session_id)

    access = create_access_token(subject=str(user.id))
    return access, refresh


async def refresh_tokens(session: AsyncSession, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    session_id = payload.get("sid")
    user_id = payload.get("sub")
    if not session_id or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_session = await get_session_by_id(session, session_id)
    if not db_session or db_session.revoked_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked")

    if db_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    incoming_hash = _hash_token(refresh_token)
    if incoming_hash != db_session.refresh_token_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Rotate refresh token
    await revoke_session(session, db_session, datetime.now(timezone.utc))

    new_session_id = str(uuid.uuid4())
    new_refresh = create_refresh_token(subject=str(user_id), session_id=new_session_id)
    new_hash = _hash_token(new_refresh)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.api_refresh_token_expire_days)
    await create_session(session, str(user_id), new_hash, expires_at, session_id=new_session_id)

    access = create_access_token(subject=str(user_id))
    return access, new_refresh


async def logout(session: AsyncSession, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return
    session_id = payload.get("sid")
    if not session_id:
        return
    db_session = await get_session_by_id(session, session_id)
    if not db_session:
        return
    await revoke_session(session, db_session, datetime.now(timezone.utc))
