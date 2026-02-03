from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.outbox import OutboxEvent


async def create_outbox_event(
    session: AsyncSession,
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    payload: dict,
) -> OutboxEvent:
    event = OutboxEvent(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload,
    )
    session.add(event)
    await session.flush()
    return event


async def mark_outbox_processed(session: AsyncSession, event: OutboxEvent, processed_at: datetime) -> None:
    event.status = "PROCESSED"
    event.processed_at = processed_at
    await session.flush()


async def mark_outbox_failed(
    session: AsyncSession,
    event: OutboxEvent,
    attempt_count: int,
    next_attempt_at: datetime,
    last_error: str,
    status: str,
) -> None:
    event.attempt_count = attempt_count
    event.next_attempt_at = next_attempt_at
    event.last_error = last_error
    event.status = status
    await session.flush()


async def fetch_due_events(session: AsyncSession, now: datetime, limit: int = 10) -> list[OutboxEvent]:
    stmt = (
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING", OutboxEvent.next_attempt_at <= now)
        .order_by(OutboxEvent.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

