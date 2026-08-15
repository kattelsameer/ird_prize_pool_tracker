"""Scenario tables for test_nepali_calendar.py. No imports of code under test."""
from datetime import date

# (name, gregorian_date, expected_fiscal_year_code)
# Anchor values taken verbatim from CLAUDE.md's own worked example:
#   "A transaction on July 16, 2026 (Gregorian) falls in the previous fiscal
#    year (2082-83 in BS). A transaction on July 17, 2026 falls in fiscal year
#    2083-84."
FISCAL_YEAR_BOUNDARY_CASES = [
    ("day_before_boundary_is_prior_fy", date(2026, 7, 16), "2082-83"),
    ("boundary_day_is_new_fy", date(2026, 7, 17), "2083-84"),
    ("well_into_new_fy", date(2026, 8, 1), "2083-84"),
    ("well_into_prior_fy", date(2025, 12, 1), "2082-83"),
]
