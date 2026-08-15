"""User account model. Each user owns exactly one ConsumerProfile (§23's
single-profile-per-consumer design still holds -- it's now per-user rather
than a single global implicit profile).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutil import now_kathmandu
from app.models.base import Base
from app.models.types import TZDateTime


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TZDateTime(), default=now_kathmandu)
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime(), default=now_kathmandu, onupdate=now_kathmandu
    )
