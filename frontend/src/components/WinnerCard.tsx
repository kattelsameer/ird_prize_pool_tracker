import { Link } from "react-router-dom";
import { DataSourceBadge } from "./DataSourceBadge";
import { ClaimCountdown } from "./ClaimCountdown";
import type { MatchResult } from "../api/types";
import styles from "./WinnerCard.module.css";

export interface WinnerCardProps {
  match: MatchResult;
}

/**
 * Renders a matched coupon. Always shows all three data-source categories explicitly
 * (government / user / app-derived) and never claims a guaranteed prize — only that the
 * coupon matches published data (§65).
 */
function formatRupees(amount: number): string {
  return `Rs ${amount.toLocaleString("en-US")}`;
}

export function WinnerCard({ match }: WinnerCardProps) {
  return (
    <article className={styles.card} aria-labelledby={`winner-${match.coupon_id}-heading`}>
      <h3 id={`winner-${match.coupon_id}-heading`} className={styles.heading}>
        Your coupon matches a published prize-pool result
      </h3>

      {match.prize_amount !== null && (
        <p className={styles.amount}>
          {formatRupees(match.prize_amount)}
          {match.prize_amount_net !== null && (
            <span className={styles.amountNet}> ({formatRupees(match.prize_amount_net)} after 25% tax)</span>
          )}
          <span className={styles.rank}> · Rank {match.winner_rank}</span>
        </p>
      )}

      <div className={styles.badges}>
        <DataSourceBadge source="government">
          Coupon {match.prize_coupon_number} selected in{" "}
          {match.category_title_en ?? "the prize pool"}
          {match.draw_title_en ? ` (${match.draw_title_en})` : ""}
        </DataSourceBadge>
        <DataSourceBadge source="user">Your coupon: {match.coupon_code}</DataSourceBadge>
        <DataSourceBadge source="app">
          Status: matched{match.fiscal_year_unconfirmed ? " (fiscal year unconfirmed)" : ""}
        </DataSourceBadge>
      </div>

      {match.fiscal_year_unconfirmed && (
        <p className={styles.notice} role="note">
          Your coupon code matches, but you haven't confirmed a fiscal year on this coupon, so
          we can't fully verify the match yet. Double-check the coupon details.
        </p>
      )}

      <ClaimCountdown claimDeadline={match.claim_deadline} claimStatus={match.claim_status} />

      <p className={styles.disclaimer}>
        This match does not guarantee payment. To claim, you must bring the{" "}
        <strong>original physical bill</strong> (no photocopies), a valid government photo ID,
        your PAN, and your bank account details to an Inland Revenue Office in person before the
        deadline above.
      </p>

      <Link to={`/coupons/${match.coupon_id}`} className={styles.link}>
        View claim details →
      </Link>
    </article>
  );
}
