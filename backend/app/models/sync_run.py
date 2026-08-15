"""Sync observability model (CLAUDE.md §40)."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Integer, String

from app.models.types import TZDateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutil import now_kathmandu
from app.models.base import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at: Mapped[datetime] = mapped_column(TZDateTime(), default=now_kathmandu)
    finished_at: Mapped[datetime | None] = mapped_column(TZDateTime(), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running", index=True)
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
