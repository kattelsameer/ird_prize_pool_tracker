"""Daily Nepal-time sync scheduler (CLAUDE.md §38), plus failure-retry
scheduling (CLAUDE.md §10e: after a failed sync, retry after 1 hour, then 4
hours, then 24 hours -- not immediately, and not indefinitely-fast).

Uses APScheduler's CronTrigger with an explicit `timezone="Asia/Kathmandu"` so
the daily 00:00 fire time is correct regardless of the host container's local
timezone (which may be UTC in Docker).
"""
from __future__ import annotations

import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from app.core.config import get_settings
from app.core.timeutil import now_kathmandu

logger = logging.getLogger("app.scheduler")

_scheduler: BackgroundScheduler | None = None
_sync_job = None

RETRY_JOB_ID = "sync_retry"


def start_scheduler(sync_job) -> BackgroundScheduler | None:
    """Start the background scheduler and register the daily sync job.

    Returns None (and does not start anything) when DEMO_MODE is enabled or
    the scheduler is explicitly disabled via SCHEDULER_ENABLED=false -- demo
    mode exercises the app via seeded fixtures instead of live IRD calls
    (CLAUDE.md §58).
    """
    global _scheduler, _sync_job
    settings = get_settings()
    _sync_job = sync_job
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


def schedule_sync_retry(delay_seconds: int) -> None:
    """Schedule a one-off retry of the sync job `delay_seconds` from now.
    A no-op if the scheduler isn't running (demo mode, tests, or scheduler
    disabled) -- there is nothing to schedule against.
    """
    if _scheduler is None or _sync_job is None:
        return
    run_date = now_kathmandu() + timedelta(seconds=delay_seconds)
    _scheduler.add_job(
        _sync_job,
        trigger=DateTrigger(run_date=run_date),
        id=RETRY_JOB_ID,
        replace_existing=True,
        misfire_grace_time=3600,
    )
    logger.info("Sync retry scheduled for %s (in %ss)", run_date.isoformat(), delay_seconds)


def cancel_sync_retry() -> None:
    """Clear any pending retry job -- called after a successful sync so a
    stale retry never fires once the data is already fresh.
    """
    if _scheduler is None:
        return
    if _scheduler.get_job(RETRY_JOB_ID) is not None:
        _scheduler.remove_job(RETRY_JOB_ID)
        logger.info("Pending sync retry canceled")


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
