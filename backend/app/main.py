"""FastAPI application entrypoint (CLAUDE.md §19-21, §41-43, §47)."""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import coupons, health, matches, notifications, profile, prize_pools, settings as settings_api, sync
from app.core.config import get_settings
from app.core.db import SessionLocal, engine
from app.core.logging import configure_logging
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.models import Base
from app.repositories.network_repo import ensure_default_networks
from app.repositories.profile_repo import get_or_create_default_profile
from app.services.sync_service import run_sync

logger = logging.getLogger("app.main")

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Sajha Coupon Tracker API",
    description=(
        "Unofficial consumer tracker for Nepal's IRD Taxpayer Incentive Gift "
        "Program prize pool. Not affiliated with or endorsed by the Government "
        "of Nepal or the Inland Revenue Department."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pydantic validation errors are safe to return as-is (no internals leaked)
    # and are already user-actionable (CLAUDE.md §42).
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces / internal details to the client (CLAUDE.md §43).
    # Full detail is logged server-side only.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


app.include_router(health.router)
app.include_router(profile.router)
app.include_router(coupons.router)
app.include_router(prize_pools.router)
app.include_router(matches.router)
app.include_router(notifications.router)
app.include_router(settings_api.router)
app.include_router(sync.router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Application starting (demo_mode=%s)", settings.demo_mode)

    # Table creation: Alembic (`alembic upgrade head`) is the source of truth
    # for schema management (CLAUDE.md §22), but we also create_all here as a
    # safety net for first-run/demo bootstrapping so the app never 500s on a
    # completely fresh database file before migrations have been run.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        get_or_create_default_profile(db)
        ensure_default_networks(db)

        if settings.demo_mode:
            from scripts.seed_demo import seed_demo_data

            seed_demo_data(db)
            logger.info("Demo mode: seeded deterministic demo fixtures")
    finally:
        db.close()

    if not settings.demo_mode:
        start_scheduler(run_sync)
    logger.info("Application started")


@app.on_event("shutdown")
def on_shutdown() -> None:
    shutdown_scheduler()
    logger.info("Application shutting down")
