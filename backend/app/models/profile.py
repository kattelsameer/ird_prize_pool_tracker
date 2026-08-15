"""ConsumerProfile model (CLAUDE.md §23).

Deliberately minimal: no PAN, no bank details, no citizenship data -- those
only matter at in-person claim time and are explicitly out of scope for this
application (CLAUDE.md §10d).

One profile per authenticated User (one-to-one via the unique `user_id` FK) --
created at registration time, never shared across accounts.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String

from app.models.types import TZDateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutil import now_kathmandu
from app.models.base import Base


class ConsumerProfile(Base):
    __tablename__ = "consumer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZDateTime(), default=now_kathmandu)
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime(), default=now_kathmandu, onupdate=now_kathmandu
    )
