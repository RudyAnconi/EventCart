from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.core.deps import get_current_user
from eventcart.db.session import get_session
from eventcart.repo.order_repo import get_order, list_order_items, list_orders
from eventcart.schemas.order import OrderCreate, OrderResponse
from eventcart.services.order_service import create_order_with_idempotency

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> OrderResponse:
    async with session.begin():
        response = await create_order_with_idempotency(
            session,
            str(current_user.id),
            [item.model_dump() for item in payload.items],
            idempotency_key,
        )
    return OrderResponse(**response)


@router.get("", response_model=list[OrderResponse])
async def list_user_orders(
    session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)
) -> list[OrderResponse]:
    orders = await list_orders(session, str(current_user.id))
    responses: list[OrderResponse] = []
    for order in orders:
        items = await list_order_items(session, str(order.id))
        responses.append(
            OrderResponse(
                id=str(order.id),
                status=order.status,
                total_cents=order.total_cents,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    {
                        "id": str(item.id),
                        "product_id": str(item.product_id),
                        "qty": item.qty,
                        "unit_price_cents": item.unit_price_cents,
                    }
                    for item in items
                ],
            )
        )
    return responses


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> OrderResponse:
    order = await get_order(session, str(current_user.id), order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    items = await list_order_items(session, str(order.id))
    return OrderResponse(
        id=str(order.id),
        status=order.status,
        total_cents=order.total_cents,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "qty": item.qty,
                "unit_price_cents": item.unit_price_cents,
            }
            for item in items
        ],
    )
