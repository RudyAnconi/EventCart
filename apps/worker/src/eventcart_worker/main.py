from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.core.logging import configure_logging
from eventcart.core.settings import settings
from eventcart.db.session import SessionLocal
from eventcart.services.processor import handle_outbox_event
from eventcart.services.outbox_service import claim_due_events, mark_failed, mark_processed

logger = structlog.get_logger()


async def worker_loop() -> None:
    configure_logging(settings.api_log_level)
    logger.info("worker.started")
    while True:
        events = []
        async with SessionLocal() as session:
            async with session.begin():
                events = await claim_due_events(session, batch_size=10)
                for event in events:
                    try:
                        await handle_outbox_event(session, event)
                        await mark_processed(session, event)
                    except Exception as exc:  # noqa: BLE001
                        attempt = event.attempt_count + 1
                        await mark_failed(
                            session,
                            event,
                            attempt,
                            str(exc)[:1000],
                            settings.worker_max_attempts,
                        )
        if not events:
            await asyncio.sleep(settings.worker_poll_interval_seconds)
        else:
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(worker_loop())
