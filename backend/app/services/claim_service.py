"""Claim-focused view over the matching engine (CLAUDE.md §34, §41 GET /api/claims).

This is a thin filter over `matching_service.compute_matches_for_profile` --
claims are not a separately-stored concept, they are derived live from the
current match set so status is always up to date relative to "now".
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.claim_status import ClaimStatus
from app.domain.matching import MatchResult
from app.services.matching_service import compute_matches_for_profile


def list_claims_for_profile(db: Session, profile_id: str) -> list[MatchResult]:
    """All matches that represent an active claims concern, i.e. every match
    (a coupon that matched a published winner always has *some* claim status
    per CLAUDE.md §30)."""
    return compute_matches_for_profile(db, profile_id)


def list_wins_for_profile(db: Session, profile_id: str) -> list[MatchResult]:
    """Alias of the full match list for the /api/wins endpoint -- every match
    is a 'win' in the sense of matching published data (CLAUDE.md §65 language
    care: this still never claims a guaranteed payout)."""
    return compute_matches_for_profile(db, profile_id)


def list_expiring_claims(db: Session, profile_id: str) -> list[MatchResult]:
    return [
        m
        for m in compute_matches_for_profile(db, profile_id)
        if m.claim_status == ClaimStatus.CLAIM_EXPIRING
    ]
