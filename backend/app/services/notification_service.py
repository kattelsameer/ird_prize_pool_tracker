"""Notification generation (CLAUDE.md §33, §10e).

Every notification created here goes through `create_notification_if_new`,
which is a no-op if the same `dedup_key` already exists -- this is what
prevents a re-sync from spamming the user with the same event twice.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.domain.claim_status import ClaimStatus
from app.domain.matching import MatchResult
from app.repositories.notification_repo import create_notification_if_new
from app.repositories.settings_repo import get_or_create_settings
from app.services.matching_service import build_match_message

logger = logging.getLogger("app.services.notification")


def generate_match_and_claim_notifications(
    db: Session, profile_id: str, matches: list[MatchResult]
) -> int:
    """Create NEW_MATCH / CLAIM_EXPIRING / CLAIM_EXPIRED notifications for
    matches, skipping any event already notified (by dedup_key). Returns the
    number of genuinely new notifications created.
    """
    settings = get_or_create_settings(db)
    created = 0

    for match in matches:
        if settings.notify_new_match:
            dedup_key = f"NEW_MATCH:{match.coupon_id}:{match.draw_id}"
            notification = create_notification_if_new(
                db,
                profile_id=profile_id,
                type_="NEW_MATCH",
                message=build_match_message(match),
                dedup_key=dedup_key,
                coupon_id=match.coupon_id,
                draw_id=match.draw_id,
            )
            if notification is not None:
                created += 1

        if match.claim_status == ClaimStatus.CLAIM_EXPIRING and settings.notify_claim_expiring:
            dedup_key = f"CLAIM_EXPIRING:{match.coupon_id}:{match.draw_id}"
            notification = create_notification_if_new(
                db,
                profile_id=profile_id,
                type_="CLAIM_EXPIRING",
                message=(
                    "Your claim deadline is approaching for a coupon that matches "
                    "a published IRD result. Visit an Inland Revenue Office with your "
                    "original bill and PAN before the deadline."
                ),
                dedup_key=dedup_key,
                coupon_id=match.coupon_id,
                draw_id=match.draw_id,
            )
            if notification is not None:
                created += 1
        elif match.claim_status == ClaimStatus.CLAIM_EXPIRED and settings.notify_claim_expired:
            dedup_key = f"CLAIM_EXPIRED:{match.coupon_id}:{match.draw_id}"
            notification = create_notification_if_new(
                db,
                profile_id=profile_id,
                type_="CLAIM_EXPIRED",
                message=(
                    "Your claim period has expired for a coupon that matched a "
                    "published IRD result. Unclaimed prizes are transferred to the "
                    "Prime Minister's Disaster Relief Fund."
                ),
                dedup_key=dedup_key,
                coupon_id=match.coupon_id,
                draw_id=match.draw_id,
            )
            if notification is not None:
                created += 1

    if created:
        logger.info("Generated %s new match/claim notifications", created)
    return created


def generate_sync_data_notification(
    db: Session, profile_id: str, *, sync_run_id: str, new_winner_count: int
) -> bool:
    """Only notify on a sync that actually added new government data
    (CLAUDE.md §33: 'Do not notify on routine syncs with no changes')."""
    settings = get_or_create_settings(db)
    if not settings.notify_sync_updates or new_winner_count <= 0:
        return False
    dedup_key = f"NEW_SYNC_DATA:{sync_run_id}"
    notification = create_notification_if_new(
        db,
        profile_id=profile_id,
        type_="NEW_SYNC_DATA",
        message=f"New government prize-pool data is available ({new_winner_count} new winner record(s)).",
        dedup_key=dedup_key,
    )
    return notification is not None


def generate_sync_recovered_notification(db: Session, profile_id: str, *, sync_run_id: str) -> bool:
    """Notify when a previously-failing sync has now succeeded, even if this
    particular run added no new winner records (CLAUDE.md §33: 'a previous
    failure was resolved' is one of the conditions that should notify)."""
    settings = get_or_create_settings(db)
    if not settings.notify_sync_updates:
        return False
    dedup_key = f"SYNC_RECOVERED:{sync_run_id}"
    notification = create_notification_if_new(
        db,
        profile_id=profile_id,
        type_="NEW_SYNC_DATA",
        message="Government data synchronization is working again after a previous failure.",
        dedup_key=dedup_key,
    )
    return notification is not None


def generate_sync_failed_notification(db: Session, profile_id: str, *, sync_run_id: str) -> bool:
    settings = get_or_create_settings(db)
    if not settings.notify_sync_failures:
        return False
    dedup_key = f"SYNC_FAILED:{sync_run_id}"
    notification = create_notification_if_new(
        db,
        profile_id=profile_id,
        type_="SYNC_FAILED",
        message=(
            "Government data could not be synchronized. Existing data is still "
            "available and nothing has been deleted."
        ),
        dedup_key=dedup_key,
    )
    return notification is not None
