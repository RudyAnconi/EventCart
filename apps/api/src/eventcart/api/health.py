from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@router.get("/ready")
async def ready() -> dict:
    return {"status": "ready", "time": datetime.now(timezone.utc).isoformat()}
