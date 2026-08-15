"""Per-profile app settings model (CLAUDE.md §36) -- notification preferences.

One row per ConsumerProfile (via the unique `profile_id` FK) -- these are
personal preferences, not global config, now that there's more than one
profile in the system.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consumer_profiles.id"), nullable=False, unique=True, index=True
    )
    notify_new_match: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_claim_expiring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_claim_expired: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_sync_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_sync_failures: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
