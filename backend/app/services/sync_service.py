"""Government data synchronization orchestration (CLAUDE.md §37-40, §67-68).

    IRD API -> IrdClient -> adapter -> SyncService -> repositories -> DB
                                            |
                                            +-> matching_service -> notification_service

A failed sync NEVER deletes or mutates existing PrizePoolWinner rows beyond
what a successful upsert would do; on any failure we simply record a failed
SyncRun and stop, leaving all previously-synced data intact (CLAUDE.md §68).
"""
from __future__ import annotations

import logging
import threading

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.integrations.ird.ird_client import IrdClient, IrdClientConfig, IrdClientError
from app.repositories.profile_repo import get_or_create_default_profile
from app.repositories.prize_pool_repo import upsert_winner
from app.repositories.sync_repo import finish_sync_run, get_latest_sync_run, start_sync_run
from app.services.matching_service import compute_matches_for_profile
from app.services.notification_service import (
    generate_match_and_claim_notifications,
    generate_sync_data_notification,
    generate_sync_failed_notification,
    generate_sync_recovered_notification,
)

logger = logging.getLogger("app.services.sync")

_sync_lock = threading.Lock()
_sync_in_progress = False


def is_sync_in_progress() -> bool:
    return _sync_in_progress


def run_sync(db: Session | None = None) -> str:
    """Execute one full synchronization pass. Safe to call from the scheduler
    or an on-demand API trigger. Returns the resulting SyncRun id.

    A lock prevents two syncs from running concurrently (e.g. a manual
    "sync now" click racing the scheduled midnight run).
    """
    global _sync_in_progress

    if not _sync_lock.acquire(blocking=False):
        logger.info("Sync already in progress; skipping this trigger")
        raise RuntimeError("A synchronization is already in progress")

    owns_session = db is None
    session = db or SessionLocal()
    _sync_in_progress = True

    # Capture the previous run's status BEFORE creating this run's row --
    # once start_sync_run() commits, this run immediately becomes "the latest
    # run", so this is the only point at which we can tell whether the prior
    # sync had failed (needed for the "failure just resolved" notification).
    previous_run = get_latest_sync_run(session)
    previously_failing = previous_run is not None and previous_run.status == "failed"

    run = start_sync_run(session)
    logger.info("Sync started: run_id=%s", run.id)

    try:
        settings = get_settings()
        client_config = IrdClientConfig(
            base_url=settings.ird_api_base_url,
            timeout_seconds=settings.ird_request_timeout_seconds,
            page_limit=settings.ird_page_limit,
            max_retries=settings.ird_max_retries,
        )
        client = IrdClient(config=client_config)
        try:
            pages = client.fetch_all_pages()
        finally:
            client.close()

        records_received = 0
        records_inserted = 0
        records_updated = 0
        records_skipped = 0

        for page in pages:
            for record in page.winners:
                records_received += 1
                try:
                    _row, was_inserted = upsert_winner(session, record, source_sync_id=run.id)
                    if was_inserted:
                        records_inserted += 1
                    else:
                        records_updated += 1
                except Exception:  # noqa: BLE001 - defensive per-record isolation
                    logger.exception("Failed to upsert winner for draw_id=%s", record.draw_id)
                    records_skipped += 1

        session.commit()

        finish_sync_run(
            session,
            run,
            status="success" if records_skipped == 0 else "partial",
            records_received=records_received,
            records_inserted=records_inserted,
            records_updated=records_updated,
            records_skipped=records_skipped,
        )
        logger.info(
            "Sync completed: run_id=%s received=%s inserted=%s updated=%s skipped=%s",
            run.id,
            records_received,
            records_inserted,
            records_updated,
            records_skipped,
        )

        # Refresh matches/notifications only if there's any chance something
        # changed (new/updated winners) -- avoids noisy "sync completed"
        # notifications on truly no-op syncs (CLAUDE.md §33).
        profile = get_or_create_default_profile(session)

        if records_inserted or records_updated or previously_failing:
            matches = compute_matches_for_profile(session, profile.id)
            generate_match_and_claim_notifications(session, profile.id, matches)
            if records_inserted:
                generate_sync_data_notification(
                    session, profile.id, sync_run_id=run.id, new_winner_count=records_inserted
                )
            elif previously_failing:
                generate_sync_recovered_notification(session, profile.id, sync_run_id=run.id)
            session.commit()

        return run.id

    except IrdClientError as exc:
        session.rollback()
        logger.error("Sync failed (IRD client error): %s", exc)
        finish_sync_run(session, run, status="failed", error_message=str(exc))
        profile = get_or_create_default_profile(session)
        generate_sync_failed_notification(session, profile.id, sync_run_id=run.id)
        session.commit()
        return run.id
    except Exception as exc:  # noqa: BLE001 - never let a sync crash the scheduler
        session.rollback()
        logger.exception("Sync failed (unexpected error)")
        finish_sync_run(session, run, status="failed", error_message=str(exc))
        session.commit()
        return run.id
    finally:
        _sync_in_progress = False
        _sync_lock.release()
        if owns_session:
            session.close()
