"""Daily Nepal-time sync scheduler (CLAUDE.md §38).

Uses APScheduler's CronTrigger with an explicit `timezone="Asia/Kathmandu"` so
the daily 00:00 fire time is correct regardless of the host container's local
timezone (which may be UTC in Docker).
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings

logger = logging.getLogger("app.scheduler")

_scheduler: BackgroundScheduler | None = None


def start_scheduler(sync_job) -> BackgroundScheduler | None:
    """Start the background scheduler and register the daily sync job.

    Returns None (and does not start anything) when DEMO_MODE is enabled or
    the scheduler is explicitly disabled via SCHEDULER_ENABLED=false -- demo
    mode exercises the app via seeded fixtures instead of live IRD calls
    (CLAUDE.md §58).
    """
    global _scheduler
    settings = get_settings()
    if settings.demo_mode or not settings.scheduler_enabled:
        logger.info(
            "Scheduler not started (demo_mode=%s, scheduler_enabled=%s)",
            settings.demo_mode,
            settings.scheduler_enabled,
        )
        return None

    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
    scheduler.add_job(
        sync_job,
        trigger=CronTrigger(hour=0, minute=0, timezone=settings.scheduler_timezone),
        id="daily_ird_sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info("Scheduler started: daily IRD sync at 00:00 %s", settings.scheduler_timezone)
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
