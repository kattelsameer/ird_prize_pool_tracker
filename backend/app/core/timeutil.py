"""Timezone helpers (CLAUDE.md §69). Always use Asia/Kathmandu explicitly."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

KATHMANDU_TZ = ZoneInfo("Asia/Kathmandu")


def now_kathmandu() -> datetime:
    """Current time as a tz-aware datetime in Asia/Kathmandu.

    Never use `datetime.now()`/`datetime.utcnow()` directly for business logic
    -- always route through this function so the timezone is explicit and
    testable (CLAUDE.md §69).
    """
    return datetime.now(KATHMANDU_TZ)


def to_kathmandu(value: datetime) -> datetime:
    """Convert any tz-aware datetime to Asia/Kathmandu. Raises on naive input."""
    if value.tzinfo is None:
        raise ValueError("to_kathmandu requires a tz-aware datetime")
    return value.astimezone(KATHMANDU_TZ)
