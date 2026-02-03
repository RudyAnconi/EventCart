from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.order import Order
from eventcart.repo.order_repo import update_order_status
from eventcart.repo.outbox_repo import create_outbox_event


async def confirm_payment(session: AsyncSession, order: Order) -> None:
    if order.status != "PENDING_PAYMENT":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order state")

    await update_order_status(session, order, "PAID")

    await create_outbox_event(
        session,
        aggregate_type="order",
        aggregate_id=str(order.id),
        event_type="order.paid",
        payload={"order_id": str(order.id), "user_id": str(order.user_id)},
    )
