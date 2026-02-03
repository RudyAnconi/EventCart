from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.session import Session


async def create_session(
    session: AsyncSession,
    user_id: str,
    refresh_token_hash: str,
    expires_at: datetime,
    session_id: str | None = None,
) -> Session:
    db_session = Session(
        id=session_id,
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
    )
    session.add(db_session)
    await session.flush()
    return db_session


async def get_session_by_id(session: AsyncSession, session_id: str) -> Session | None:
    result = await session.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def revoke_session(session: AsyncSession, db_session: Session, revoked_at: datetime) -> None:
    db_session.revoked_at = revoked_at
    await session.flush()
