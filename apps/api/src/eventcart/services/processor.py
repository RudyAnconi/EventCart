from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.repo.order_repo import get_order_by_id, update_order_status

logger = structlog.get_logger()


async def handle_outbox_event(session: AsyncSession, event) -> None:
    if event.event_type == "order.paid":
        order_id = event.payload.get("order_id")
        order = await get_order_by_id(session, order_id)
        if not order:
            raise RuntimeError("Order not found for outbox event")
        await update_order_status(session, order, "FULFILLED")
        logger.info("order.fulfilled", order_id=order_id)
        return

    logger.info("event.ignored", event_type=event.event_type, event_id=str(event.id))
