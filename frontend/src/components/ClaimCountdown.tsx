import { useEffect, useState } from "react";
import { claimStatusPresentation, computeClaimCountdown } from "../lib/claimStatus";
import type { ClaimStatus } from "../api/types";
import styles from "./ClaimCountdown.module.css";

export interface ClaimCountdownProps {
  claimDeadline: string;
  claimStatus: ClaimStatus;
}

/** Live-updating claim deadline countdown. Recomputes every minute; never overrides the
 * server's authoritative claim_status (§34), only renders it alongside a friendly countdown. */
export function ClaimCountdown({ claimDeadline, claimStatus }: ClaimCountdownProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(id);
  }, []);

  const countdown = computeClaimCountdown(claimDeadline, now);
  const presentation = claimStatusPresentation(claimStatus);

  return (
    <div className={`${styles.wrapper} ${styles[presentation.tone]}`} role="status">
      <span aria-hidden="true" className={styles.icon}>
        {presentation.icon}
      </span>
      <span className={styles.text}>
        <strong>{presentation.label}.</strong> {countdown.label}
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
      </span>
    </div>
  );
}
