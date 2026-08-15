"""Custom SQLAlchemy column types.

`DateTime(timezone=True)` is honored by PostgreSQL but SQLite (our default,
CLAUDE.md §22) has no native timezone-aware storage: the stock SQLite dialect
persists/reads datetimes as naive strings, silently dropping tzinfo on
read-back. Every tz-aware comparison in this app (claim-deadline math,
`Asia/Kathmandu` "now" checks -- CLAUDE.md §69) depends on tzinfo surviving a
round trip through the database, so we use this TypeDecorator everywhere
instead of the raw SQLAlchemy `DateTime(timezone=True)`.

Values are normalized to UTC and stored naive internally (portable to
PostgreSQL later -- a `TIMESTAMP WITHOUT TIME ZONE` column storing UTC is a
completely standard, common pattern there too), and tzinfo=UTC is reattached
on every read.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError(
                "TZDateTime column received a naive datetime; all datetimes "
                "stored in this app must be tz-aware (CLAUDE.md §69)."
            )
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc)
