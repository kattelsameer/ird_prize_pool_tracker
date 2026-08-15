from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.models.sync_run import SyncRun


def start_sync_run(db: Session) -> SyncRun:
    run = SyncRun(started_at=now_kathmandu(), status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_sync_run(
    db: Session,
    run: SyncRun,
    *,
    status: str,
    records_received: int = 0,
    records_inserted: int = 0,
    records_updated: int = 0,
    records_skipped: int = 0,
    error_message: str | None = None,
) -> SyncRun:
    run.finished_at = now_kathmandu()
    run.status = status
    run.records_received = records_received
    run.records_inserted = records_inserted
    run.records_updated = records_updated
    run.records_skipped = records_skipped
    run.error_message = error_message
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_latest_sync_run(db: Session) -> SyncRun | None:
    return db.execute(select(SyncRun).order_by(SyncRun.started_at.desc()).limit(1)).scalar_one_or_none()


def get_latest_successful_sync_run(db: Session) -> SyncRun | None:
    return db.execute(
        select(SyncRun)
        .where(SyncRun.status == "success")
        .order_by(SyncRun.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def count_consecutive_failed_runs(db: Session, *, recent_limit: int = 50) -> int:
    """How many sync runs in a row (most recent first) have status="failed",
    counting from the latest run backwards until the first non-failed run.
    Used to pick the retry backoff stage (CLAUDE.md §10e: 1h, then 4h, then
    24h) -- a single isolated failure retries sooner than a run of them.

    `recent_limit` bounds the walk-back so a very long unbroken failure
    streak can never make this an unbounded query.
    """
    runs = db.execute(
        select(SyncRun.status).order_by(SyncRun.started_at.desc()).limit(recent_limit)
    ).scalars().all()
    count = 0
    for status in runs:
        if status != "failed":
            break
        count += 1
    return count
