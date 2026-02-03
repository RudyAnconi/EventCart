from __future__ import annotations

from sqlalchemy import select

from eventcart.core.security import hash_password
from eventcart.models.order import Order
from eventcart.models.product import Product
from eventcart.models.user import User
from eventcart.services.order_service import create_order_with_idempotency


async def test_idempotency_reuses_response(db_session):
    user = User(email="idempotent@example.com", password_hash=hash_password("Password123!"))
    product = Product(sku="SKU-1", name="Ticket", price_cents=1000, stock_qty=5)

    async with db_session.begin():
        db_session.add_all([user, product])

    items = [{"product_id": str(product.id), "qty": 2}]
    key = "idem-123"

    async with db_session.begin():
        first = await create_order_with_idempotency(
            db_session, str(user.id), items, key
        )
    async with db_session.begin():
        second = await create_order_with_idempotency(
            db_session, str(user.id), items, key
        )

    assert first == second

    result = await db_session.execute(select(Order))
    orders = list(result.scalars().all())
    assert len(orders) == 1
