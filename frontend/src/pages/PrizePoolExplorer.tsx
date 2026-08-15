import { useState } from "react";
import { usePrizePools } from "../api/prizePools";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import { DataSourceBadge } from "../components/DataSourceBadge";
import { claimStatusPresentation } from "../lib/claimStatus";
import { generateFiscalYearOptions } from "../lib/fiscalYears";
import styles from "./PrizePoolExplorer.module.css";

const FISCAL_YEAR_OPTIONS = generateFiscalYearOptions();

export function PrizePoolExplorer() {
  const [couponCode, setCouponCode] = useState("");
  const [fiscalYear, setFiscalYear] = useState("");
  const [category, setCategory] = useState("");
  const [claimStatus, setClaimStatus] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sort, setSort] = useState("-published_at");
  const [page, setPage] = useState(1);

  const prizePools = usePrizePools({
    coupon_code: couponCode,
    fiscal_year: fiscalYear,
    category,
    claim_status: claimStatus,
    date_from: dateFrom,
    date_to: dateTo,
    sort,
    page,
    page_size: 20,
  });

  function toggleSort(field: string) {
    setSort((current) => (current === `-${field}` ? field : `-${field}`));
    setPage(1);
  }

  const totalPages = prizePools.data
    ? Math.max(1, Math.ceil(prizePools.data.total / prizePools.data.limit))
    : 1;

  return (
    <div className={styles.page}>
      <h1>Prize Pool Explorer</h1>
      <DataSourceBadge source="government">
        All draws and winners published by IRD — searchable across every consumer, not just your
        own coupons
      </DataSourceBadge>

      <form
        className={styles.filters}
        role="search"
        aria-label="Filter prize pool records"
        onSubmit={(e) => e.preventDefault()}
      >
        <div className={styles.filterField}>
          <label htmlFor="pp-coupon">Coupon code</label>
          <input
            id="pp-coupon"
            type="search"
            value={couponCode}
            onChange={(e) => {
              setPage(1);
              setCouponCode(e.target.value);
            }}
          />
        </div>
        <div className={styles.filterField}>
          <label htmlFor="pp-fy">Fiscal year</label>
          <select
            id="pp-fy"
            value={fiscalYear}
            onChange={(e) => {
              setPage(1);
              setFiscalYear(e.target.value);
            }}
          >
            <option value="">All</option>
            {FISCAL_YEAR_OPTIONS.map((fy) => (
              <option key={fy} value={fy}>
                FY {fy}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.filterField}>
          <label htmlFor="pp-category">Prize category</label>
          <select
            id="pp-category"
            value={category}
            onChange={(e) => {
              setPage(1);
              setCategory(e.target.value);
            }}
          >
            <option value="">All</option>
            <option value="Daily Prize">Daily Prize</option>
            <option value="Bumper Prize">Bumper Prize</option>
          </select>
        </div>
        <div className={styles.filterField}>
          <label htmlFor="pp-claim">Claim status</label>
          <select
            id="pp-claim"
            value={claimStatus}
            onChange={(e) => {
              setPage(1);
              setClaimStatus(e.target.value);
            }}
          >
            <option value="">All</option>
            <option value="CLAIM_ACTIVE">Active</option>
            <option value="CLAIM_EXPIRING">Expiring soon</option>
            <option value="CLAIM_EXPIRED">Expired</option>
          </select>
        </div>
        <div className={styles.filterField}>
          <label htmlFor="pp-from">Eligible from</label>
          <input
            id="pp-from"
            type="date"
            value={dateFrom}
            onChange={(e) => {
              setPage(1);
              setDateFrom(e.target.value);
            }}
          />
        </div>
        <div className={styles.filterField}>
          <label htmlFor="pp-to">Eligible to</label>
          <input
            id="pp-to"
            type="date"
            value={dateTo}
            onChange={(e) => {
              setPage(1);
              setDateTo(e.target.value);
            }}
          />
        </div>
      </form>

      {prizePools.isLoading && <LoadingState label="Loading prize-pool records…" />}
      {prizePools.isError && <ErrorState error={prizePools.error} onRetry={() => prizePools.refetch()} />}
      {prizePools.isSuccess && prizePools.data.items.length === 0 && (
        <EmptyState
          title="No prize-pool records match your filters"
          description="Try widening your search, or check back after the next sync."
        />
      )}
      {prizePools.isSuccess && prizePools.data.items.length > 0 && (
        <>
          <table className={styles.table}>
            <caption className="visually-hidden">Published prize-pool draws</caption>
            <thead>
              <tr>
                <th scope="col">
                  <button type="button" className={styles.sortButton} onClick={() => toggleSort("coupon_code")}>
                    Coupon code
                  </button>
                </th>
                <th scope="col">Category</th>
                <th scope="col">Fiscal year</th>
                <th scope="col">
                  <button
                    type="button"
                    className={styles.sortButton}
                    onClick={() => toggleSort("published_at")}
                  >
                    Published
                  </button>
                </th>
                <th scope="col">Eligible period</th>
                <th scope="col">Claim status</th>
              </tr>
            </thead>
            <tbody>
              {prizePools.data.items.map((item) => {
                const presentation = claimStatusPresentation(item.claim_status);
                return (
                  <tr key={item.id}>
                    <td>{item.normalized_coupon_code}</td>
                    <td>{item.category}</td>
                    <td>{item.fiscal_year}</td>
                    <td>{new Date(item.published_at).toLocaleDateString("en-US", { dateStyle: "medium" })}</td>
                    <td>
                      {item.eligible_from} – {item.eligible_to}
                    </td>
                    <td>
                      <span aria-hidden="true">{presentation.icon}</span> {presentation.label}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {totalPages > 1 && (
            <nav className={styles.pagination} aria-label="Prize pool pagination">
              <button
                type="button"
                className={styles.pageButton}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Previous
              </button>
              <span>
                Page {page} of {totalPages} ({prizePools.data.total} records)
              </span>
              <button
                type="button"
                className={styles.pageButton}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next
              </button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
