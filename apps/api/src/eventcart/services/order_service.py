from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.order import Order
from eventcart.models.order_item import OrderItem
from eventcart.models.product import Product
from eventcart.repo.idempotency_repo import create_idempotency_key, get_idempotency_key
from eventcart.repo.order_repo import add_order_item, create_order, update_order_status
from eventcart.repo.product_repo import update_stock


def _request_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _order_response(order: Order, items: list[OrderItem]) -> dict:
    return {
        "id": str(order.id),
        "status": order.status,
        "total_cents": order.total_cents,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "qty": item.qty,
                "unit_price_cents": item.unit_price_cents,
            }
            for item in items
        ],
    }


async def create_order_with_idempotency(
    session: AsyncSession,
    user_id: str,
    items_payload: list[dict],
    idempotency_key: str | None,
) -> dict:
    payload_hash = _request_hash({"items": items_payload})

    if not items_payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items")

    if idempotency_key:
        existing = await get_idempotency_key(session, user_id, idempotency_key)
        if existing:
            if existing.request_hash != payload_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key reuse with different payload",
                )
            return existing.response

    product_ids = [item["product_id"] for item in items_payload]
    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate items")

    stmt = select(Product).where(Product.id.in_(product_ids)).with_for_update()
    result = await session.execute(stmt)
    products = list(result.scalars().all())

    if len(products) != len(product_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product")

    products_by_id = {str(product.id): product for product in products}

    total_cents = 0
    for item in items_payload:
        product = products_by_id[item["product_id"]]
        if item["qty"] > product.stock_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}",
            )
        total_cents += product.price_cents * item["qty"]

    order = await create_order(session, user_id, "PENDING_PAYMENT", total_cents)

    order_items: list[OrderItem] = []
    for item in items_payload:
        product = products_by_id[item["product_id"]]
        await update_stock(session, product, product.stock_qty - item["qty"])
        order_item = await add_order_item(
            session, str(order.id), str(product.id), item["qty"], product.price_cents
        )
        order_items.append(order_item)

    order.updated_at = datetime.now(timezone.utc)
    response = _order_response(order, order_items)

    if idempotency_key:
        await create_idempotency_key(session, user_id, idempotency_key, payload_hash, response)

    return response


async def mark_order_paid(session: AsyncSession, order: Order) -> None:
    await update_order_status(session, order, "PAID")


async def mark_order_fulfilled(session: AsyncSession, order: Order) -> None:
    await update_order_status(session, order, "FULFILLED")
