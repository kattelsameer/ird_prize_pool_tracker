from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_db
from app.models.profile import ConsumerProfile
from app.schemas.draw_period import DrawPeriodStatusRead
from app.schemas.match import MatchRead
from app.services.claim_service import list_claims_for_profile, list_wins_for_profile
from app.services.draw_period_service import compute_draw_period_statuses_for_profile
from app.services.matching_service import build_match_message, compute_matches_for_profile

router = APIRouter(prefix="/api", tags=["matches"])


def _to_read(match) -> MatchRead:
    return MatchRead(
        coupon_id=match.coupon_id,
        coupon_code=match.coupon_code,
        draw_id=match.draw_id,
        prize_coupon_number=match.prize_coupon_number,
        winner_rank=match.winner_rank,
        category_title_en=match.category_title_en or None,
        draw_type=match.draw_type or None,
        draw_title_en=match.draw_title_en or None,
        fiscal_year_unconfirmed=match.fiscal_year_unconfirmed,
        eligible_period_warning=match.eligible_period_warning,
        claim_status=match.claim_status,
        claim_deadline=match.claim_deadline,
        claim_open=match.claim_open,
        prize_amount=match.prize_amount,
        prize_amount_net=match.prize_amount_net,
        eligible_from=match.eligible_from,
        eligible_to=match.eligible_to,
        message=build_match_message(match),
    )


@router.get("/matches", response_model=list[MatchRead])
def list_matches_endpoint(
    db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)
):
    matches = compute_matches_for_profile(db, profile.id)
    return [_to_read(m) for m in matches]


@router.get("/wins", response_model=list[MatchRead])
def list_wins_endpoint(
    db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)
):
    return [_to_read(m) for m in list_wins_for_profile(db, profile.id)]


@router.get("/claims", response_model=list[MatchRead])
def list_claims_endpoint(
    db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)
):
    return [_to_read(m) for m in list_claims_for_profile(db, profile.id)]


@router.get("/matches/draw-periods", response_model=list[DrawPeriodStatusRead])
def list_draw_period_statuses_endpoint(
    db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)
):
    """Per-coupon draw-period context (CLAUDE.md §6/§29), independent of
    whether the coupon actually won -- see the module docstring on
    `app.domain.draw_period` for what DRAWN/PENDING/UNKNOWN mean."""
    statuses = compute_draw_period_statuses_for_profile(db, profile.id)
    return [
        DrawPeriodStatusRead(coupon_id=coupon_id, **status.__dict__)
        for coupon_id, status in statuses.items()
    ]
