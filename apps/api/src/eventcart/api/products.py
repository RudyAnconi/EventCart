from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.db.session import get_session
from eventcart.repo.product_repo import list_products
from eventcart.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
async def get_products(session: AsyncSession = Depends(get_session)) -> list[ProductResponse]:
    products = await list_products(session)
    return [
        ProductResponse(
            id=str(product.id),
            sku=product.sku,
            name=product.name,
            price_cents=product.price_cents,
            stock_qty=product.stock_qty,
        )
        for product in products
    ]
