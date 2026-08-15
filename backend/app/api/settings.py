from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_current_user, get_db
from app.models.profile import ConsumerProfile
from app.models.user import User
from app.repositories.network_repo import (
    add_network,
    ensure_default_networks,
    get_network,
    list_networks,
    update_network,
)
from app.repositories.settings_repo import get_or_create_settings, update_settings
from app.schemas.settings import NetworkCreate, NetworkRead, NetworkUpdate, SettingsRead, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def read_settings(db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)):
    settings = get_or_create_settings(db, profile.id)
    # Self-healing default for networks (shared/global reference data, not
    # per-profile): app.main's startup event already seeds these against the
    # app's own engine, but a request-scoped session (e.g. under test, where
    # get_db is overridden to a different database) shouldn't depend on that
    # lifecycle event having touched the same database.
    ensure_default_networks(db)
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
def update_settings_endpoint(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    settings = get_or_create_settings(db, profile.id)
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
def add_network_endpoint(payload: NetworkCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    network = add_network(db, payload.name)
    return NetworkRead(id=network.id, name=network.name, active=network.active)


@router.patch("/networks/{network_id}", response_model=NetworkRead)
def update_network_endpoint(
    network_id: str,
    payload: NetworkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    network = get_network(db, network_id)
    if network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    updated = update_network(db, network, name=payload.name, active=payload.active)
    return NetworkRead(id=updated.id, name=updated.name, active=updated.active)
