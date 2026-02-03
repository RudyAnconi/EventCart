from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import text

from eventcart.db.session import SessionLocal


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def _cleanup(session):
    await session.execute(text("DELETE FROM order_items"))
    await session.execute(text("DELETE FROM orders"))
    await session.execute(text("DELETE FROM outbox_events"))
    await session.execute(text("DELETE FROM idempotency_keys"))
    await session.execute(text("DELETE FROM products"))
    await session.execute(text("DELETE FROM sessions"))
    await session.execute(text("DELETE FROM users"))


@pytest.fixture()
async def db_session():
    async with SessionLocal() as session:
        yield session
        async with session.begin():
            await _cleanup(session)
