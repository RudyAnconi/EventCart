from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from eventcart.api.auth import router as auth_router
from eventcart.api.health import router as health_router
from eventcart.api.orders import router as orders_router
from eventcart.api.payments import router as payments_router
from eventcart.api.products import router as products_router
from eventcart.core.logging import configure_logging
from eventcart.core.settings import settings
from eventcart.schemas.common import ProblemDetail

configure_logging(settings.api_log_level)
logger = structlog.get_logger()

app = FastAPI(
    title="EventCart API",
    description="Order system with outbox pattern and async processing.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = None
    try:
        response = await call_next(request)
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request.complete",
            method=request.method,
            path=request.url.path,
            status_code=getattr(response, "status_code", 500),
            duration_ms=round(duration_ms, 2),
        )
        structlog.contextvars.clear_contextvars()
    if response is None:
        response = JSONResponse(status_code=500, content={"detail": "Internal server error"})
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    problem = ProblemDetail(
        title="Request failed",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url.path),
        timestamp=datetime.now(timezone.utc),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(mode="json"),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    problem = ProblemDetail(
        title="Validation error",
        status=422,
        detail="Request validation failed",
        instance=str(request.url.path),
        timestamp=datetime.now(timezone.utc),
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=problem.model_dump(mode="json"),
        media_type="application/problem+json",
    )


@app.get("/")
async def root() -> dict:
    return {"name": "EventCart API", "status": "ok"}


app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(health_router)
