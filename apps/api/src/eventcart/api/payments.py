from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.core.deps import get_current_user
from eventcart.db.session import get_session
from eventcart.repo.order_repo import get_order
from eventcart.services.payment_service import confirm_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/confirm/{order_id}", status_code=status.HTTP_200_OK)
async def confirm_order_payment(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
) -> dict:
    async with session.begin():
        order = await get_order(session, str(current_user.id), order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        await confirm_payment(session, order)
    return {"status": "paid", "order_id": order_id}
