import { useMemo } from "react";
import { useCoupons } from "../api/coupons";
import { useWins } from "../api/matches";
import { useNotifications } from "../api/notifications";
import { usePrizePools } from "../api/prizePools";
import { useSyncStatus, useTriggerSync } from "../api/sync";
import { NoticeBanner } from "../components/NoticeBanner";
import { WinnerCard } from "../components/WinnerCard";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { DataSourceBadge } from "../components/DataSourceBadge";
import styles from "./Dashboard.module.css";

export function Dashboard() {
  const coupons = useCoupons({ page_size: 1 });
  const wins = useWins();
  const notifications = useNotifications();
  const recentUpdates = usePrizePools({ page_size: 5, sort: "-published_at" });
  const syncStatus = useSyncStatus();
  const triggerSync = useTriggerSync();

  const expiringWins = useMemo(
    () => (wins.data ?? []).filter((w) => w.claim_status === "CLAIM_EXPIRING"),
    [wins.data]
  );
  const newMatchNotifications = useMemo(
    () => (notifications.data?.items ?? []).filter((n) => n.type === "NEW_MATCH" && !n.read_at),
    [notifications.data]
  );
  const syncFailed = syncStatus.data?.latest_run?.status === "failed";

  const hasAnyNotice = expiringWins.length > 0 || newMatchNotifications.length > 0 || syncFailed;

  return (
    <div className={styles.page}>
      <section className={styles.section} aria-label="Notices requiring attention">
        <h2 className={styles.sectionTitle}>Needs your attention</h2>
        <div className={styles.notices}>
          {syncFailed && (
            <NoticeBanner tone="urgent" title="Government synchronization failed">
              Government data could not be updated. Existing data is still available.
              {syncStatus.data?.latest_run?.error_message && (
                <> Details: {syncStatus.data.latest_run.error_message}</>
              )}
            </NoticeBanner>
          )}
          {expiringWins.map((win) => (
            <NoticeBanner
              key={`${win.coupon_id}-${win.draw_id}`}
              tone="warning"
              title={`Claim deadline approaching for coupon ${win.coupon_code}`}
            >
              Your claim window closes soon. Visit an Inland Revenue Office in person with your
              original bill, photo ID, PAN, and bank details before the deadline.
            </NoticeBanner>
          ))}
          {newMatchNotifications.map((notification) => (
            <NoticeBanner key={notification.id} tone="success" title="New match found">
              {notification.message}
            </NoticeBanner>
          ))}
          {!hasAnyNotice && (
            <NoticeBanner tone="info" title="Nothing urgent right now">
              We'll let you know immediately if a coupon matches or a claim deadline is
              approaching.
            </NoticeBanner>
          )}
        </div>
      </section>

      <section className={styles.section} aria-label="Winning coupons">
        <h2 className={styles.sectionTitle}>Your winning coupons</h2>
        {wins.isLoading && <LoadingState label="Checking your coupons against published results…" />}
        {wins.isError && <ErrorState error={wins.error} onRetry={() => wins.refetch()} />}
        {wins.isSuccess && wins.data.length === 0 && (
          <EmptyState
            icon="🔍"
            title="No matching prize-pool result was found for your coupons yet"
            description="This means none of your coupons match published results so far — new draws are announced every 1st and 16th."
          />
        )}
        {wins.isSuccess && wins.data.length > 0 && (
          <div className={styles.winners}>
            {wins.data.map((match) => (
              <WinnerCard key={`${match.coupon_id}-${match.draw_id}`} match={match} />
            ))}
          </div>
        )}
      </section>

      <section className={styles.section} aria-label="Summary">
        <h2 className={styles.sectionTitle}>Summary</h2>
        <div className={styles.summaryGrid}>
          <div className={styles.summaryCard}>
            <p className={styles.summaryValue}>{coupons.data?.total ?? (coupons.isLoading ? "…" : "—")}</p>
            <p className={styles.summaryLabel}>Coupons tracked</p>
          </div>
          <div className={styles.summaryCard}>
            <p className={styles.summaryValue}>{wins.data?.length ?? (wins.isLoading ? "…" : "—")}</p>
            <p className={styles.summaryLabel}>Matches found</p>
          </div>
          <div className={styles.summaryCard}>
            <p className={styles.summaryValue}>{expiringWins.length}</p>
            <p className={styles.summaryLabel}>Claims expiring soon</p>
          </div>
        </div>
      </section>

      <section className={styles.section} aria-label="Recent government updates">
        <h2 className={styles.sectionTitle}>Recent prize-pool updates</h2>
        <DataSourceBadge source="government">Published draws from prize.ird.gov.np</DataSourceBadge>
        {recentUpdates.isLoading && <LoadingState label="Loading recent updates…" />}
        {recentUpdates.isError && <ErrorState error={recentUpdates.error} onRetry={() => recentUpdates.refetch()} />}
        {recentUpdates.isSuccess && recentUpdates.data.items.length === 0 && (
          <EmptyState title="No government data yet" description="Run a sync to fetch the latest published draws." />
        )}
        {recentUpdates.isSuccess && recentUpdates.data.items.length > 0 && (
          <ul className={styles.updatesList}>
            {recentUpdates.data.items.map((item) => (
              <li key={item.id} className={styles.updateItem}>
                <strong>{item.draw_title_en}</strong> — {item.category}, published{" "}
                {new Date(item.published_at).toLocaleDateString("en-US", { dateStyle: "medium" })}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className={styles.section} aria-label="Synchronization status">
        <h2 className={styles.sectionTitle}>Sync status</h2>
        <div className={styles.syncRow}>
          {syncStatus.isLoading && <LoadingState label="Checking sync status…" />}
          {syncStatus.isSuccess && (
            <div>
              <DataSourceBadge source="app">
                {syncStatus.data.is_running
                  ? "Sync in progress…"
                  : syncStatus.data.latest_run
                  ? `Last synced ${new Date(
                      syncStatus.data.latest_run.finished_at ?? syncStatus.data.latest_run.started_at
                    ).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })} (${
                      syncStatus.data.latest_run.status
                    })`
                  : "Never synced yet"}
              </DataSourceBadge>
            </div>
          )}
          <button
            type="button"
            className={styles.syncButton}
            onClick={() => triggerSync.mutate()}
            disabled={triggerSync.isPending || syncStatus.data?.is_running}
          >
            {triggerSync.isPending ? "Syncing…" : "Sync now"}
          </button>
          {triggerSync.isError && <ErrorState error={triggerSync.error} />}
        </div>
      </section>
    </div>
  );
}
