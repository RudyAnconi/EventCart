from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.idempotency import IdempotencyKey


async def get_idempotency_key(
    session: AsyncSession, user_id: str, key: str
) -> IdempotencyKey | None:
    result = await session.execute(
        select(IdempotencyKey).where(IdempotencyKey.user_id == user_id, IdempotencyKey.key == key)
    )
    return result.scalar_one_or_none()


async def create_idempotency_key(
    session: AsyncSession, user_id: str, key: str, request_hash: str, response: dict
) -> IdempotencyKey:
    record = IdempotencyKey(
        user_id=user_id, key=key, request_hash=request_hash, response=response
    )
    session.add(record)
    await session.flush()
    return record
