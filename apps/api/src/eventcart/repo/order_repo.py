from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.order import Order
from eventcart.models.order_item import OrderItem


async def create_order(
    session: AsyncSession, user_id: str, status: str, total_cents: int
) -> Order:
    order = Order(user_id=user_id, status=status, total_cents=total_cents)
    session.add(order)
    await session.flush()
    return order


async def add_order_item(
    session: AsyncSession, order_id: str, product_id: str, qty: int, unit_price_cents: int
) -> OrderItem:
    item = OrderItem(
        order_id=order_id, product_id=product_id, qty=qty, unit_price_cents=unit_price_cents
    )
    session.add(item)
    await session.flush()
    return item


async def list_orders(session: AsyncSession, user_id: str) -> list[Order]:
    result = await session.execute(select(Order).where(Order.user_id == user_id))
    return list(result.scalars().all())


async def get_order(session: AsyncSession, user_id: str, order_id: str) -> Order | None:
    result = await session.execute(
        select(Order).where(Order.user_id == user_id, Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_order_by_id(session: AsyncSession, order_id: str) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def list_order_items(session: AsyncSession, order_id: str) -> list[OrderItem]:
    result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


async def update_order_status(session: AsyncSession, order: Order, status: str) -> None:
    order.status = status
    order.updated_at = datetime.now(timezone.utc)
    await session.flush()
