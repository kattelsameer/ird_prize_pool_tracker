from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settings import AppSettings


def get_or_create_settings(db: Session) -> AppSettings:
    settings = db.execute(select(AppSettings).where(AppSettings.id == "singleton")).scalar_one_or_none()
    if settings is None:
        settings = AppSettings(id="singleton")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, settings: AppSettings, updates: dict) -> AppSettings:
    for key, value in updates.items():
        if value is not None and hasattr(settings, key):
            setattr(settings, key, value)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
