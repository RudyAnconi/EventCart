from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    timestamp: datetime
    errors: list[dict] | None = None
