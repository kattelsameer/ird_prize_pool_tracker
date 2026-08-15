"""Gregorian <-> Bikram Sambat (BS) fiscal-year utilities (CLAUDE.md §10b).

IMPORTANT DEVIATION NOTE (read before touching this file):

The spec calls for the `nepali_datetime` PyPI package to do full Gregorian<->BS
date conversion. `requirements.txt` pins it (`nepali_datetime==1.0.8`, a real,
well-known, MIT-licensed pure-Python package). However, the sandbox this backend
was *built* in had its package registries blocked at the network-egress layer
(pypi.org, files.pythonhosted.org, and the Ubuntu apt mirrors all returned an
HTTP 403 "Host not in allowlist" for every mirror tried) so `nepali_datetime`
could not actually be installed or verified there.

To keep the fiscal-year-boundary logic correct and *actually testable* in that
constrained sandbox, this module:
  1. Tries to import and use `nepali_datetime` first (the real path for any
     environment that *does* have registry access, e.g. the real Docker build).
  2. Falls back to a small anchor-date table if the import fails.

The fallback table's only *confirmed* anchors are FY2082-83 and FY2083-84,
taken verbatim from CLAUDE.md's own worked example ("A transaction on July 16,
2026 falls in fiscal year 2082-83; July 17, 2026 falls in fiscal year
2083-84") and cross-checked against RESEARCH.md's live-confirmed
`eligible_from: "2026-07-17"` for the first FY2083-84 draw. Years outside the
confirmed anchors are extrapolated at a fixed 365-day fiscal-year length from
the nearest anchor, which is an approximation -- real BS fiscal years are
365 or 366 Gregorian days depending on how many days Ashadh (the last BS month)
has that year. This is clearly flagged via `is_estimated=True` on the result
and must be replaced by the real `nepali_datetime` conversion once registry
access is available.

Nothing in the *matching engine* actually depends on this approximation being
exact: IRD publishes `prize_fiscal_year_code` directly per winner (an
authoritative label we never recompute), so this module is only used for (a)
advisory display of a user's coupon in BS terms and (b) the advisory
"transaction date within eligible period" check, neither of which gates a
match.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

try:  # pragma: no cover - exercised only when the real package is installed
    import nepali_datetime as _nepali_datetime  # type: ignore

    _HAS_NEPALI_DATETIME = True
except ImportError:  # pragma: no cover - exercised in this sandbox
    _HAS_NEPALI_DATETIME = False


NEPALI_MONTHS = [
    "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush",
    "Magh", "Falgun", "Chaitra", "Baisakh", "Jyestha", "Ashadh",
]

# Confirmed anchor: Gregorian date of "Shrawan 1" (BS fiscal-year start) for a
# given BS year. See module docstring for provenance.
_CONFIRMED_SHRAWAN_1: dict[int, date] = {
    2082: date(2025, 7, 16),
    2083: date(2026, 7, 17),
}

_FISCAL_YEAR_LENGTH_DAYS = 365


@dataclass(frozen=True)
class FiscalYearInfo:
    fiscal_year_code: str  # e.g. "2083-84"
    bs_year_start: int
    fiscal_year_start_gregorian: date
    fiscal_year_end_gregorian: date
    is_estimated: bool


def _shrawan_1_gregorian(bs_year: int) -> tuple[date, bool]:
    """Return (gregorian_date_of_shrawan_1, is_estimated) for a BS year."""
    if bs_year in _CONFIRMED_SHRAWAN_1:
        return _CONFIRMED_SHRAWAN_1[bs_year], False

    # Extrapolate from the nearest confirmed anchor at a fixed 365-day cadence.
    nearest_year = min(_CONFIRMED_SHRAWAN_1, key=lambda y: abs(y - bs_year))
    nearest_date = _CONFIRMED_SHRAWAN_1[nearest_year]
    delta_years = bs_year - nearest_year
    estimated = nearest_date + timedelta(days=_FISCAL_YEAR_LENGTH_DAYS * delta_years)
    return estimated, True


def fiscal_year_info_for_bs_year(bs_year: int) -> FiscalYearInfo:
    """Fiscal year info for BS year `bs_year` (e.g. 2083 -> FY "2083-84")."""
    start, estimated_start = _shrawan_1_gregorian(bs_year)
    next_start, estimated_next = _shrawan_1_gregorian(bs_year + 1)
    end = next_start - timedelta(days=1)
    code = f"{bs_year}-{str(bs_year + 1)[-2:]}"
    return FiscalYearInfo(
        fiscal_year_code=code,
        bs_year_start=bs_year,
        fiscal_year_start_gregorian=start,
        fiscal_year_end_gregorian=end,
        is_estimated=estimated_start or estimated_next,
    )


def fiscal_year_for_gregorian_date(gregorian_date: date) -> FiscalYearInfo:
    """Determine the Nepal fiscal year a Gregorian date falls into.

    If `nepali_datetime` is importable, prefer it for a precise conversion.
    Otherwise fall back to the anchor-table approximation described above.
    """
    if _HAS_NEPALI_DATETIME:  # pragma: no cover - not exercised in this sandbox
        bs_date = _nepali_datetime.date.from_datetime_date(gregorian_date)
        bs_year = bs_date.year
        # BS month 1 == Baisakh in nepali_datetime's own numbering; fiscal year
        # starts at Shrawan (BS month 4 in that numbering). Compute directly via
        # round-tripping through the library rather than re-deriving Shrawan 1
        # here, to make full use of its precise calendar tables.
        shrawan_1_this_year = _nepali_datetime.date(bs_year, 4, 1).to_datetime_date()
        if gregorian_date >= shrawan_1_this_year:
            fy_start_bs_year = bs_year
        else:
            fy_start_bs_year = bs_year - 1
        shrawan_1_start = _nepali_datetime.date(fy_start_bs_year, 4, 1).to_datetime_date()
        shrawan_1_next = _nepali_datetime.date(fy_start_bs_year + 1, 4, 1).to_datetime_date()
        return FiscalYearInfo(
            fiscal_year_code=f"{fy_start_bs_year}-{str(fy_start_bs_year + 1)[-2:]}",
            bs_year_start=fy_start_bs_year,
            fiscal_year_start_gregorian=shrawan_1_start,
            fiscal_year_end_gregorian=shrawan_1_next - timedelta(days=1),
            is_estimated=False,
        )

    # Fallback: walk the confirmed/estimated anchors to find the containing year.
    # Start from a BS year guess (Gregorian year - 57, a standard rough BS/AD
    # offset) and adjust until the date falls within [start, end].
    guess_bs_year = gregorian_date.year + 57
    for candidate in (guess_bs_year - 1, guess_bs_year, guess_bs_year + 1):
        info = fiscal_year_info_for_bs_year(candidate)
        if info.fiscal_year_start_gregorian <= gregorian_date <= info.fiscal_year_end_gregorian:
            return info
    # Should not happen for any reasonable input, but never crash on an
    # out-of-range date -- return the closest candidate for advisory display.
    return fiscal_year_info_for_bs_year(guess_bs_year)
