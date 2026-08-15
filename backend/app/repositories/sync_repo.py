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
