from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SyncRunRead(BaseModel):
    id: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    records_received: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    error_message: str | None


class SyncStatusRead(BaseModel):
    is_running: bool
    latest_run: SyncRunRead | None


class SyncTriggerResponse(BaseModel):
    accepted: bool
    message: str
