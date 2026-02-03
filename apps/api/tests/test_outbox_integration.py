from __future__ import annotations

from sqlalchemy import select

from eventcart.core.security import hash_password
from eventcart.models.order import Order
from eventcart.models.product import Product
from eventcart.models.user import User
from eventcart.repo.order_repo import get_order_by_id
from eventcart.services.order_service import create_order_with_idempotency
from eventcart.services.payment_service import confirm_payment
from eventcart.services.outbox_service import claim_due_events, mark_processed
from eventcart.services.processor import handle_outbox_event


async def test_order_payment_outbox_flow(db_session):
    user = User(email="flow@example.com", password_hash=hash_password("Password123!"))
    product = Product(sku="SKU-2", name="VIP", price_cents=2500, stock_qty=10)

    async with db_session.begin():
        db_session.add_all([user, product])

    async with db_session.begin():
        response = await create_order_with_idempotency(
            db_session, str(user.id), [{"product_id": str(product.id), "qty": 1}], "flow-1"
        )

    order_id = response["id"]

    async with db_session.begin():
        order = await get_order_by_id(db_session, order_id)
        assert order is not None
        await confirm_payment(db_session, order)

    async with db_session.begin():
        events = await claim_due_events(db_session, batch_size=5)
        assert len(events) == 1
        await handle_outbox_event(db_session, events[0])
        await mark_processed(db_session, events[0])

    result = await db_session.execute(select(Order).where(Order.id == order_id))
    updated = result.scalar_one()
    assert updated.status == "FULFILLED"
