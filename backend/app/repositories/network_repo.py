from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.normalization import normalize_network_name
from app.models.network import Network

DEFAULT_NETWORKS = ["eSewa", "Khalti", "IME Pay", "Bank Transfer", "Cash/Manual"]


def ensure_default_networks(db: Session) -> None:
    existing = {n.name for n in db.execute(select(Network)).scalars().all()}
    changed = False
    for name in DEFAULT_NETWORKS:
        if name not in existing:
            db.add(Network(name=name, active=True))
            changed = True
    if changed:
        db.commit()


def list_networks(db: Session, *, active_only: bool = False) -> list[Network]:
    stmt = select(Network)
    if active_only:
        stmt = stmt.where(Network.active.is_(True))
    return list(db.execute(stmt.order_by(Network.name)).scalars().all())


def add_network(db: Session, name: str) -> Network:
    normalized = normalize_network_name(name) or name
    existing = db.execute(select(Network).where(Network.name == normalized)).scalar_one_or_none()
    if existing:
        if not existing.active:
            existing.active = True
            db.add(existing)
            db.commit()
            db.refresh(existing)
        return existing
    network = Network(name=normalized, active=True)
    db.add(network)
    db.commit()
    db.refresh(network)
    return network
