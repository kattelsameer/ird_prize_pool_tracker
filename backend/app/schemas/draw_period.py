from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class DrawPeriodStatusRead(BaseModel):
    """Application-derived information (CLAUDE.md §6): which draw period a
    coupon's transaction date falls into, and whether that draw has actually
    been published yet. This never claims a match outcome -- pair with
    GET /api/matches for that. `is_estimated=True` means the period/publish
    date shown is computed from the regular 1st/16th cadence, not an
    IRD-published fact (CLAUDE.md §65)."""

    coupon_id: str
    state: Literal["DRAWN", "PENDING", "UNKNOWN"]
    eligible_from: date | None
    eligible_to: date | None
    draw_id: str | None
    draw_title_en: str | None
    published_at: datetime | None
    estimated_publish_date: date | None
    is_estimated: bool
