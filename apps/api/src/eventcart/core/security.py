from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from jose import jwt

from eventcart.core.settings import settings

_ALGORITHM = "HS256"
_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except Exception:
        return False


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.api_access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, settings.api_secret_key, algorithm=_ALGORITHM)


def create_refresh_token(subject: str, session_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.api_refresh_token_expire_days)
    to_encode = {"sub": subject, "exp": expire, "type": "refresh", "sid": session_id}
    return jwt.encode(to_encode, settings.api_secret_key, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.api_secret_key, algorithms=[_ALGORITHM])
