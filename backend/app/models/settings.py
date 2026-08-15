"""Single-row app settings model (CLAUDE.md §36) -- notification preferences."""
from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[str] = mapped_column(String(10), primary_key=True, default="singleton")
    notify_new_match: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_claim_expiring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_claim_expired: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_sync_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_sync_failures: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
