from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.outbox import OutboxEvent
from eventcart.repo.outbox_repo import fetch_due_events, mark_outbox_failed, mark_outbox_processed


def compute_backoff(attempt: int, base_seconds: float = 2.0, max_seconds: float = 60.0) -> float:
    exp = min(max_seconds, base_seconds * (2 ** attempt))
    jitter = random.uniform(0.0, 0.5 * exp)
    return exp + jitter


async def claim_due_events(session: AsyncSession, batch_size: int = 10) -> list[OutboxEvent]:
    now = datetime.now(timezone.utc)
    return await fetch_due_events(session, now, limit=batch_size)


async def mark_processed(session: AsyncSession, event: OutboxEvent) -> None:
    await mark_outbox_processed(session, event, datetime.now(timezone.utc))


async def mark_failed(
    session: AsyncSession, event: OutboxEvent, attempt: int, error: str, max_attempts: int
) -> None:
    if attempt >= max_attempts:
        status = "DEAD"
        next_attempt = datetime.now(timezone.utc) + timedelta(days=365)
    else:
        status = "PENDING"
        delay = compute_backoff(attempt)
        next_attempt = datetime.now(timezone.utc) + timedelta(seconds=delay)

    await mark_outbox_failed(session, event, attempt, next_attempt, error, status)
