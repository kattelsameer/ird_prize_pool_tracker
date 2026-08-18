"""Scenario data for test_draw_period.py. No imports of code under test."""
from datetime import date, datetime, timezone

from app.domain.draw_period import KnownDrawPeriod

# Two consecutive real-shaped synced periods, matching the Shrawan 16-31 /
# Bhadra 1-15 example verified in tests/data_nepali_calendar.py.
SHRAWAN_16_31 = KnownDrawPeriod(
    draw_id="draw-shrawan-16-31",
    draw_title_en="Fortnightly Draw",
    eligible_from=date(2026, 8, 1),
    eligible_to=date(2026, 8, 16),
    published_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
)

BHADRA_1_15 = KnownDrawPeriod(
    draw_id="draw-bhadra-1-15",
    draw_title_en="Fortnightly Draw",
    eligible_from=date(2026, 8, 17),
    eligible_to=date(2026, 8, 31),
    published_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
)

KNOWN_PERIODS = [SHRAWAN_16_31, BHADRA_1_15]
