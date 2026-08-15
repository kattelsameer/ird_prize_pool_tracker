"""Pure normalization helpers for government/user data (CLAUDE.md §28).

These functions never mutate the *authoritative* raw value held elsewhere in the
data model -- callers are expected to store both `original_value` and the
`normalized_value` produced here side by side.
"""
from __future__ import annotations

import re

_WHITESPACE_OR_HYPHEN_RE = re.compile(r"[\s\-]+")
_NON_ALNUM_RE = re.compile(r"[^A-Z0-9]")


def normalize_coupon_code(raw_code: str) -> str:
    """Normalize a coupon code for matching/searching.

    Confirmed live IRD data (`prize_coupon_number`) is a clean 12-digit numeric
    string with no separators. CLAUDE.md's own example (`"007 315 254 493BUMPER"`)
    suggests a human-formatted display variant may exist elsewhere, so this
    normalizer defensively:
      - strips all whitespace and hyphens
      - uppercases the remainder
      - drops any other non-alphanumeric characters (defensive; observed data
        never contains them)

    The original value is never altered -- this only produces a *derived*
    normalized value for indexing/matching.
    """
    if raw_code is None:
        return ""
    value = raw_code.strip()
    value = _WHITESPACE_OR_HYPHEN_RE.sub("", value)
    value = value.upper()
    value = _NON_ALNUM_RE.sub("", value)
    return value


def normalize_fiscal_year(raw_fy: str | None) -> str | None:
    """Normalize a Nepal fiscal-year label to the canonical `YYYY-YY` form.

    Accepts common variants such as `"2083/84"`, `" 2083-84 "`, `"2083-084"`, and
    normalizes separators/whitespace without changing the semantic year values.
    Returns None if the input is None/blank -- fiscal year is optional on a user
    coupon per CLAUDE.md §10e (coupon-code-only matching must still work).
    """
    if raw_fy is None:
        return None
    value = raw_fy.strip()
    if not value:
        return None
    value = value.replace("/", "-")
    value = re.sub(r"\s+", "", value)
    parts = value.split("-")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        start = parts[0]
        end = parts[1]
        # Normalize a possible 4-digit end (e.g. "2083-2084") down to 2 digits.
        if len(end) == 4:
            end = end[-2:]
        return f"{start}-{end.zfill(2)}"
    return value


def normalize_network_name(raw_network: str | None) -> str | None:
    """Normalize free-text network/provider names for comparison/display only.

    Network is never a matching criterion (CLAUDE.md §10e, §G) -- this is purely
    for consistent display and de-duplicating Settings dropdown entries.
    """
    if raw_network is None:
        return None
    value = raw_network.strip()
    if not value:
        return None
    return " ".join(value.split())
