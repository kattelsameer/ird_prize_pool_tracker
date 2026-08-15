from __future__ import annotations

import logging
import threading

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.sync_repo import get_latest_sync_run
from app.schemas.sync import SyncRunRead, SyncStatusRead, SyncTriggerResponse
from app.services.sync_service import is_sync_in_progress, run_sync

logger = logging.getLogger("app.api.sync")

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.get("/status", response_model=SyncStatusRead)
def sync_status_endpoint(db: Session = Depends(get_db)):
    latest = get_latest_sync_run(db)
    return SyncStatusRead(
        is_running=is_sync_in_progress(),
        latest_run=SyncRunRead.model_validate(latest, from_attributes=True) if latest else None,
    )


@router.post("", response_model=SyncTriggerResponse, status_code=202)
def trigger_sync_endpoint(user: User = Depends(get_current_user)):
    if is_sync_in_progress():
        return SyncTriggerResponse(accepted=False, message="A synchronization is already in progress.")

    def _background_sync():
        try:
            run_sync()
        except Exception:  # noqa: BLE001 - already logged/recorded inside run_sync
            logger.exception("Background sync thread raised unexpectedly")

    thread = threading.Thread(target=_background_sync, daemon=True)
    thread.start()
    return SyncTriggerResponse(accepted=True, message="Synchronization started.")
