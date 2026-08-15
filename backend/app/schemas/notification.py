from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    coupon_id: str | None
    draw_id: str | None
    message: str
    created_at: datetime
    read_at: datetime | None
