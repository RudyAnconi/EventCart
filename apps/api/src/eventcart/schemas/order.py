from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: str
    qty: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    qty: int
    unit_price_cents: int


class OrderResponse(BaseModel):
    id: str
    status: str
    total_cents: int
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
