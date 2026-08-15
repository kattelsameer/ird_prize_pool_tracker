from __future__ import annotations

from pydantic import BaseModel


class NetworkRead(BaseModel):
    id: str
    name: str
    active: bool


class NetworkCreate(BaseModel):
    name: str


class NetworkUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None


class SettingsRead(BaseModel):
    notify_new_match: bool
    notify_claim_expiring: bool
    notify_claim_expired: bool
    notify_sync_updates: bool
    notify_sync_failures: bool
    networks: list[NetworkRead]


class SettingsUpdate(BaseModel):
    notify_new_match: bool | None = None
    notify_claim_expiring: bool | None = None
    notify_claim_expired: bool | None = None
    notify_sync_updates: bool | None = None
    notify_sync_failures: bool | None = None
