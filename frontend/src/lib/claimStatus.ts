/**
 * Claim status / countdown logic.
 *
 * The backend is the authority on `claim_status` (it derives ACTIVE/EXPIRING/EXPIRED using
 * Asia/Kathmandu time, per CLAUDE.md §34/§69). The frontend never recomputes claim_status
 * from scratch to decide "did I win" — it always trusts the server value for that. What the
 * frontend *does* compute locally, for live countdown display only, is the human-readable
 * "time remaining" string, derived from the server-provided `claim_deadline` timestamp and
 * the browser's current time. This mirrors the server's own EXPIRING threshold (<2 days)
 * purely for consistent copy/urgency styling, never to override the server's claim_status.
 */

import type { ClaimStatus } from "../api/types";

export const EXPIRING_THRESHOLD_MS = 2 * 24 * 60 * 60 * 1000; // 2 days

export interface ClaimCountdown {
  /** Milliseconds remaining until the deadline; negative if already past. */
  msRemaining: number;
  days: number;
  hours: number;
  minutes: number;
  isExpired: boolean;
  isExpiring: boolean;
  label: string;
}

/**
 * Compute a display-friendly countdown from now to `claimDeadlineIso`.
 * `now` is injectable for deterministic testing of boundary cases.
 */
export function computeClaimCountdown(claimDeadlineIso: string, now: Date = new Date()): ClaimCountdown {
  const deadline = new Date(claimDeadlineIso).getTime();
  const msRemaining = deadline - now.getTime();
  const isExpired = msRemaining <= 0;
  const isExpiring = !isExpired && msRemaining < EXPIRING_THRESHOLD_MS;

  const absMs = Math.abs(msRemaining);
  const days = Math.floor(absMs / (24 * 60 * 60 * 1000));
  const hours = Math.floor((absMs % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
  const minutes = Math.floor((absMs % (60 * 60 * 1000)) / (60 * 1000));

  let label: string;
  if (isExpired) {
    label = "Claim window expired";
  } else if (days >= 1) {
    label = `${days} day${days === 1 ? "" : "s"} remaining to claim`;
  } else if (hours >= 1) {
    label = `${hours} hour${hours === 1 ? "" : "s"} remaining to claim`;
  } else {
    label = `${Math.max(minutes, 1)} minute${minutes === 1 ? "" : "s"} remaining to claim`;
  }

  return { msRemaining, days, hours, minutes, isExpired, isExpiring, label };
}

/** Map a claim status to a short, non-color-dependent status label + icon glyph. */
export function claimStatusPresentation(status: ClaimStatus): {
  label: string;
  icon: string;
  tone: "active" | "expiring" | "expired";
} {
  switch (status) {
    case "CLAIM_ACTIVE":
      return { label: "Claim active", icon: "✓", tone: "active" }; // check mark
    case "CLAIM_EXPIRING":
      return { label: "Claim deadline approaching", icon: "⚠", tone: "expiring" }; // warning
    case "CLAIM_EXPIRED":
      return { label: "Claim expired", icon: "✕", tone: "expired" }; // cross mark
    default:
      return { label: "Unknown claim status", icon: "?", tone: "expired" };
  }
}
