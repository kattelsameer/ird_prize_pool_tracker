from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.network_repo import add_network, list_networks
from app.repositories.settings_repo import get_or_create_settings, update_settings
from app.schemas.settings import NetworkCreate, NetworkRead, SettingsRead, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def read_settings(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    networks = list_networks(db)
    return SettingsRead(
        notify_new_match=settings.notify_new_match,
        notify_claim_expiring=settings.notify_claim_expiring,
        notify_claim_expired=settings.notify_claim_expired,
        notify_sync_updates=settings.notify_sync_updates,
        notify_sync_failures=settings.notify_sync_failures,
        networks=[NetworkRead(id=n.id, name=n.name, active=n.active) for n in networks],
    )


@router.put("", response_model=SettingsRead)
def update_settings_endpoint(payload: SettingsUpdate, db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    update_settings(db, settings, payload.model_dump(exclude_unset=True))
    networks = list_networks(db)
    return SettingsRead(
        notify_new_match=settings.notify_new_match,
        notify_claim_expiring=settings.notify_claim_expiring,
        notify_claim_expired=settings.notify_claim_expired,
        notify_sync_updates=settings.notify_sync_updates,
        notify_sync_failures=settings.notify_sync_failures,
        networks=[NetworkRead(id=n.id, name=n.name, active=n.active) for n in networks],
    )


@router.post("/networks", response_model=NetworkRead, status_code=201)
def add_network_endpoint(payload: NetworkCreate, db: Session = Depends(get_db)):
    network = add_network(db, payload.name)
    return NetworkRead(id=network.id, name=network.name, active=network.active)
