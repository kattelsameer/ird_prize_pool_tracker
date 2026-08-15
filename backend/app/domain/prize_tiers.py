"""Fixed prize-tier amounts published by IRD (CLAUDE.md §10a).

IRD's public winners API does not include a per-record prize amount -- these
are the two known, fixed published tiers (Daily Prize / Bumper Prize). If IRD
later publishes a category outside this table, return (None, None) rather
than guessing at an amount (CLAUDE.md §5: never fabricate data).
"""
from __future__ import annotations

_TIERS: dict[str, tuple[int, int]] = {
    "Daily Prize": (133_334, 100_000),
    "Bumper Prize": (1_000_000, 750_000),
}


def prize_amounts_for_category(category_title_en: str | None) -> tuple[int | None, int | None]:
    """Returns (gross_amount, net_amount_after_25pct_tax) for a known category."""
    if category_title_en is None:
        return None, None
    return _TIERS.get(category_title_en, (None, None))
