"""Claim-deadline status calculation (CLAUDE.md §30, §34, §10e).

All comparisons here operate on tz-aware datetimes. Callers must convert to
`Asia/Kathmandu` before calling `now()` for display purposes (see
`app.core.timeutil`), but the comparisons below are timezone-correct regardless
of which tz-aware zone is passed in, since datetime comparison in Python
normalizes tz-aware values to an absolute instant.
"""
from __future__ import annotations

import enum
from datetime import datetime, timedelta


class ClaimStatus(str, enum.Enum):
    NOT_CHECKED = "NOT_CHECKED"
    NO_MATCH = "NO_MATCH"
    CLAIM_ACTIVE = "CLAIM_ACTIVE"
    CLAIM_EXPIRING = "CLAIM_EXPIRING"
    CLAIM_EXPIRED = "CLAIM_EXPIRED"


EXPIRING_THRESHOLD = timedelta(days=2)


def compute_claim_status(
    *,
    now: datetime,
    claim_deadline: datetime,
    claim_open: bool,
) -> ClaimStatus:
    """Compute claim status for a single matched winner record.

    Rules (CLAUDE.md §10e, verbatim):
      - CLAIM_EXPIRED  -- now >= claim_deadline OR claim_open is False
      - CLAIM_EXPIRING -- claim_deadline - now < 2 days (and not yet expired)
      - CLAIM_ACTIVE   -- otherwise (now < claim_deadline and claim_open is True)

    `now` and `claim_deadline` must both be tz-aware; naive datetimes raise
    ValueError to avoid silent, incorrect comparisons (CLAUDE.md §69).
    """
    if now.tzinfo is None or claim_deadline.tzinfo is None:
        raise ValueError("compute_claim_status requires tz-aware datetimes")

    if now >= claim_deadline or not claim_open:
        return ClaimStatus.CLAIM_EXPIRED

    remaining = claim_deadline - now
    if remaining < EXPIRING_THRESHOLD:
        return ClaimStatus.CLAIM_EXPIRING

    return ClaimStatus.CLAIM_ACTIVE
