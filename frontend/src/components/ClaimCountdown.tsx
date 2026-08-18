import { useEffect, useState } from "react";
import { claimStatusPresentation, computeClaimCountdown } from "../lib/claimStatus";
import { NoticeBanner, type NoticeTone } from "./NoticeBanner";
import type { ClaimStatus } from "../api/types";

export interface ClaimCountdownProps {
  claimDeadline: string;
  claimStatus: ClaimStatus;
}

const TONE_BY_CLAIM_TONE: Record<ReturnType<typeof claimStatusPresentation>["tone"], NoticeTone> = {
  active: "success",
  expiring: "warning",
  expired: "urgent",
};

/** Live-updating claim deadline countdown. Recomputes every minute; never overrides the
 * server's authoritative claim_status (§34), only renders it alongside a friendly countdown.
 * Reuses NoticeBanner's icon+title+body treatment rather than a parallel implementation, so
 * every tone-colored callout in the app shares one visual language. */
export function ClaimCountdown({ claimDeadline, claimStatus }: ClaimCountdownProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(id);
  }, []);

  const countdown = computeClaimCountdown(claimDeadline, now);
  const presentation = claimStatusPresentation(claimStatus);

  return (
    <NoticeBanner tone={TONE_BY_CLAIM_TONE[presentation.tone]} title={presentation.label}>
      {countdown.label}
      {!countdown.isExpired && (
        <>
          {" "}
          (by{" "}
          {new Date(claimDeadline).toLocaleString("en-US", {
            dateStyle: "medium",
            timeStyle: "short",
            timeZone: "Asia/Kathmandu",
          })}{" "}
          Nepal time)
        </>
      )}
    </NoticeBanner>
  );
}
