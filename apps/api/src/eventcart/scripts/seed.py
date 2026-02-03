from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from eventcart.core.security import hash_password
from eventcart.core.settings import settings
from eventcart.db.session import SessionLocal
from eventcart.models.product import Product
from eventcart.models.user import User


async def seed() -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.seed_demo_email))
        existing = result.scalar_one_or_none()
        if not existing:
            user = User(email=settings.seed_demo_email, password_hash=hash_password(settings.seed_demo_password))
            session.add(user)

        result = await session.execute(select(Product))
        products = list(result.scalars().all())
        if not products:
            items = []
            for idx in range(1, 11):
                items.append(
                    Product(
                        sku=f"EVT-{idx:03d}",
                        name=f"Event Ticket {idx}",
                        price_cents=1500 + idx * 250,
                        stock_qty=20 + idx,
                        created_at=datetime.now(timezone.utc),
                    )
                )
            session.add_all(items)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
