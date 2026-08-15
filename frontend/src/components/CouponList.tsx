import { Link } from "react-router-dom";
import type { Coupon, MatchResult } from "../api/types";
import { MatchStatusTag, type MatchStatus } from "./MatchStatusTag";
import { EmptyState } from "./EmptyState";
import styles from "./CouponList.module.css";

export interface CouponListProps {
  coupons: Coupon[];
  matches: MatchResult[];
  onDelete: (coupon: Coupon) => void;
}

export function deriveMatchStatus(coupon: Coupon, matches: MatchResult[]): MatchStatus {
  const match = matches.find((m) => m.coupon.id === coupon.id);
  if (!match) return "NO_MATCH";
  return match.claim_status;
}

export function CouponList({ coupons, matches, onDelete }: CouponListProps) {
  if (coupons.length === 0) {
    return (
      <EmptyState
        icon="🎟"
        title="No coupons yet"
        description="Add your first coupon to start tracking prize-pool results."
      />
    );
  }

  return (
    <table className={styles.table}>
      <caption className="visually-hidden">Your coupons</caption>
      <thead>
        <tr>
          <th scope="col">Coupon code</th>
          <th scope="col">Transaction date</th>
          <th scope="col">Fiscal year</th>
          <th scope="col">Network</th>
          <th scope="col">Match status</th>
          <th scope="col">
            <span className="visually-hidden">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {coupons.map((coupon) => (
          <tr key={coupon.id}>
            <td data-label="Coupon code">
              <Link to={`/coupons/${coupon.id}`}>{coupon.coupon_code}</Link>
            </td>
            <td data-label="Transaction date">{coupon.transaction_date}</td>
            <td data-label="Fiscal year">{coupon.fiscal_year ?? "—"}</td>
            <td data-label="Network">{coupon.network ?? "—"}</td>
            <td data-label="Match status">
              <MatchStatusTag status={deriveMatchStatus(coupon, matches)} />
            </td>
            <td data-label="Actions" className={styles.actionsCell}>
              <Link to={`/coupons/${coupon.id}`} className={styles.actionLink}>
                View
              </Link>
              <button
                type="button"
                className={styles.deleteButton}
                onClick={() => onDelete(coupon)}
                aria-label={`Delete coupon ${coupon.coupon_code}`}
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
