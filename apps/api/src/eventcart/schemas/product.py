from __future__ import annotations

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    price_cents: int
    stock_qty: int
