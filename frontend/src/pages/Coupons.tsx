import { useState } from "react";
import { useCoupons, useCreateCoupon, useDeleteCoupon } from "../api/coupons";
import { useMatches } from "../api/matches";
import { useSettings } from "../api/settings";
import { CouponList } from "../components/CouponList";
import { CouponForm } from "../components/CouponForm";
import { Modal } from "../components/Modal";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { generateFiscalYearOptions } from "../lib/fiscalYears";
import type { Coupon, CouponInput } from "../api/types";
import styles from "./Coupons.module.css";

const FISCAL_YEAR_OPTIONS = generateFiscalYearOptions();

export function Coupons() {
  const [search, setSearch] = useState("");
  const [fiscalYear, setFiscalYear] = useState("");
  const [network, setNetwork] = useState("");
  const [page, setPage] = useState(1);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<Coupon | null>(null);

  const filters = { search, fiscal_year: fiscalYear, network, page, page_size: 20 };
  const coupons = useCoupons(filters);
  const matches = useMatches();
  const settings = useSettings();
  const createCoupon = useCreateCoupon();
  const deleteCoupon = useDeleteCoupon();

  function handleCreate(input: CouponInput) {
    createCoupon.mutate(input, {
      onSuccess: () => setIsAddOpen(false),
    });
  }

  function handleConfirmDelete() {
    if (!pendingDelete) return;
    deleteCoupon.mutate(pendingDelete.id, {
      onSuccess: () => setPendingDelete(null),
    });
  }

  const totalPages = coupons.data ? Math.max(1, Math.ceil(coupons.data.total / coupons.data.limit)) : 1;

  return (
    <div className={styles.page}>
      <div className={styles.headerRow}>
        <h1 className={styles.title}>My Coupons</h1>
        <button type="button" className={styles.addButton} onClick={() => setIsAddOpen(true)}>
          + Add coupon
        </button>
      </div>

      <form
        className={styles.filters}
        role="search"
        aria-label="Filter coupons"
        onSubmit={(e) => e.preventDefault()}
      >
        <div className={styles.filterField}>
          <label htmlFor="coupon-search">Search by code</label>
          <input
            id="coupon-search"
            type="search"
            value={search}
            onChange={(e) => {
              setPage(1);
              setSearch(e.target.value);
            }}
            placeholder="Coupon code"
          />
        </div>
        <div className={styles.filterField}>
          <label htmlFor="coupon-fy-filter">Fiscal year</label>
          <select
            id="coupon-fy-filter"
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
          <label htmlFor="coupon-network-filter">Network</label>
          <select
            id="coupon-network-filter"
            value={network}
            onChange={(e) => {
              setPage(1);
              setNetwork(e.target.value);
            }}
          >
            <option value="">All</option>
            {(settings.data?.networks ?? []).map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
      </form>

      {coupons.isLoading && <LoadingState label="Loading your coupons…" />}
      {coupons.isError && <ErrorState error={coupons.error} onRetry={() => coupons.refetch()} />}
      {coupons.isSuccess && (
        <>
          <CouponList coupons={coupons.data.items} matches={matches.data ?? []} onDelete={setPendingDelete} />
          {totalPages > 1 && (
            <nav className={styles.pagination} aria-label="Coupon list pagination">
              <button
                type="button"
                className={styles.pageButton}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Previous
              </button>
              <span>
                Page {page} of {totalPages}
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

      {isAddOpen && (
        <Modal title="Add a coupon" onClose={() => setIsAddOpen(false)}>
          <CouponForm
            networks={settings.data?.networks}
            onSubmit={handleCreate}
            onCancel={() => setIsAddOpen(false)}
            isSubmitting={createCoupon.isPending}
            submitError={createCoupon.isError ? "We couldn't save this coupon. Please try again." : null}
          />
        </Modal>
      )}

      {pendingDelete && (
        <Modal title="Delete coupon?" onClose={() => setPendingDelete(null)}>
          <p>
            Are you sure you want to delete coupon <strong>{pendingDelete.coupon_code}</strong>? This
            only removes it from your tracker; it does not affect anything with IRD.
          </p>
          <div style={{ display: "flex", gap: "12px", marginTop: "16px" }}>
            <button
              type="button"
              className={styles.addButton}
              onClick={handleConfirmDelete}
              disabled={deleteCoupon.isPending}
            >
              {deleteCoupon.isPending ? "Deleting…" : "Delete"}
            </button>
            <button type="button" onClick={() => setPendingDelete(null)}>
              Cancel
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
