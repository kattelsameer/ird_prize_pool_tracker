import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useCoupon, useUpdateCoupon } from "../api/coupons";
import { useMatches } from "../api/matches";
import { useSettings } from "../api/settings";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { DataSourceBadge } from "../components/DataSourceBadge";
import { WinnerCard } from "../components/WinnerCard";
import { CouponForm } from "../components/CouponForm";
import { MatchStatusTag, type MatchStatus } from "../components/MatchStatusTag";
import type { CouponInput } from "../api/types";
import styles from "./CouponDetail.module.css";

export function CouponDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);

  const coupon = useCoupon(id);
  const matches = useMatches();
  const settings = useSettings();
  const updateCoupon = useUpdateCoupon(id ?? "");

  if (coupon.isLoading) return <LoadingState label="Loading coupon…" />;
  if (coupon.isError) return <ErrorState error={coupon.error} onRetry={() => coupon.refetch()} />;
  if (!coupon.data) return <ErrorState error={null} fallbackMessage="Coupon not found." />;

  const match = (matches.data ?? []).find((m) => m.coupon.id === coupon.data.id);
  const status: MatchStatus = match ? match.claim_status : "NO_MATCH";

  function handleUpdate(input: CouponInput) {
    updateCoupon.mutate(input, { onSuccess: () => setIsEditing(false) });
  }

  return (
    <div className={styles.page}>
      <Link to="/coupons" className={styles.backLink}>
        ← Back to my coupons
      </Link>

      <div className={styles.header}>
        <h1>Coupon {coupon.data.coupon_code}</h1>
        <MatchStatusTag status={status} />
      </div>

      {isEditing ? (
        <CouponForm
          initialValue={coupon.data}
          networks={settings.data?.networks}
          submitLabel="Save changes"
          onSubmit={handleUpdate}
          onCancel={() => setIsEditing(false)}
          isSubmitting={updateCoupon.isPending}
          submitError={updateCoupon.isError ? "We couldn't save your changes. Please try again." : null}
        />
      ) : (
        <>
          <dl className={styles.detailGrid}>
            <div className={styles.detailItem}>
              <dt>Coupon ID</dt>
              <dd>{coupon.data.coupon_id}</dd>
            </div>
            <div className={styles.detailItem}>
              <dt>Transaction date</dt>
              <dd>{coupon.data.transaction_date}</dd>
            </div>
            <div className={styles.detailItem}>
              <dt>Fiscal year</dt>
              <dd>{coupon.data.fiscal_year ?? "Not specified"}</dd>
            </div>
            <div className={styles.detailItem}>
              <dt>Network</dt>
              <dd>{coupon.data.network ?? "Not specified"}</dd>
            </div>
          </dl>
          <DataSourceBadge source="user">
            You added this coupon on{" "}
            {new Date(coupon.data.created_at).toLocaleDateString("en-US", { dateStyle: "medium" })}
          </DataSourceBadge>

          <div className={styles.editActions}>
            <button type="button" onClick={() => setIsEditing(true)}>
              Edit coupon
            </button>
          </div>
        </>
      )}

      {match ? (
        <WinnerCard match={match} />
      ) : (
        <div className={styles.nextSteps}>
          <DataSourceBadge source="app">
            No matching prize-pool result was found for this coupon yet
          </DataSourceBadge>
          <p>
            New draws are announced every 1st and 16th of the Nepali calendar month. We'll notify
            you the moment this coupon matches a published result.
          </p>
        </div>
      )}

      <div className={styles.nextSteps}>
        <h2>How to claim if you win</h2>
        <ol>
          <li>Visit an Inland Revenue Office in person — online claims are not accepted.</li>
          <li>Bring your original physical bill (photocopies are not accepted).</li>
          <li>Bring a government photo ID (citizenship, national ID, passport, or driving license).</li>
          <li>Bring your PAN (Personal Account Number) — mandatory.</li>
          <li>Bring your bank account details for the prize deposit.</li>
          <li>Claim within 15 calendar days of the announcement, or the prize is permanently forfeited.</li>
        </ol>
      </div>

      <button type="button" onClick={() => navigate(-1)}>
        Back
      </button>
    </div>
  );
}
