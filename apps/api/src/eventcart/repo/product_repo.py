from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eventcart.models.product import Product


async def list_products(session: AsyncSession) -> list[Product]:
    result = await session.execute(select(Product).order_by(Product.name))
    return list(result.scalars().all())


async def get_products_by_ids(session: AsyncSession, product_ids: list[str]) -> list[Product]:
    result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
    return list(result.scalars().all())


async def update_stock(session: AsyncSession, product: Product, new_qty: int) -> None:
    product.stock_qty = new_qty
    await session.flush()
