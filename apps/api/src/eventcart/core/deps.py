from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select

from eventcart.core.security import decode_token
from eventcart.db.session import SessionLocal
from eventcart.models.user import User


@dataclass(frozen=True)
class UserIdentity:
    id: str
    email: str


async def get_current_user(request: Request) -> UserIdentity:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = auth_header.replace("Bearer ", "", 1)
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserIdentity(id=str(user.id), email=user.email)
