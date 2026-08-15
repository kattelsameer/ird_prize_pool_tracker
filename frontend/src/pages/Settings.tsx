import { useEffect, useState } from "react";
import { useAddNetwork, useSettings, useUpdateNetwork, useUpdateSettings } from "../api/settings";
import { useSyncStatus, useTriggerSync } from "../api/sync";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import type { SettingsUpdate } from "../api/types";
import styles from "./Settings.module.css";

export function Settings() {
  const settings = useSettings();
  const updateSettings = useUpdateSettings();
  const addNetwork = useAddNetwork();
  const updateNetwork = useUpdateNetwork();
  const syncStatus = useSyncStatus();
  const triggerSync = useTriggerSync();

  const [notifyDraft, setNotifyDraft] = useState<SettingsUpdate | null>(null);
  const [newNetwork, setNewNetwork] = useState("");

  useEffect(() => {
    if (settings.data && !notifyDraft) {
      setNotifyDraft({
        notify_new_match: settings.data.notify_new_match,
        notify_claim_expiring: settings.data.notify_claim_expiring,
        notify_claim_expired: settings.data.notify_claim_expired,
        notify_sync_updates: settings.data.notify_sync_updates,
        notify_sync_failures: settings.data.notify_sync_failures,
      });
    }
  }, [settings.data, notifyDraft]);

  if (settings.isLoading) return <LoadingState label="Loading settings…" />;
  if (settings.isError) return <ErrorState error={settings.error} onRetry={() => settings.refetch()} />;
  if (!settings.data || !notifyDraft) return null;

  function toggleNotificationPref(key: keyof SettingsUpdate) {
    setNotifyDraft((d) => (d ? { ...d, [key]: !d[key] } : d));
  }

  function handleSaveNotifications() {
    if (notifyDraft) updateSettings.mutate(notifyDraft);
  }

  function handleAddNetwork() {
    if (!newNetwork.trim()) return;
    addNetwork.mutate(newNetwork.trim(), { onSuccess: () => setNewNetwork("") });
  }

  return (
    <div className={styles.page}>
      <h1>Settings</h1>

      <section className={styles.section} aria-label="Networks">
        <h2>Networks / payment methods</h2>
        <p>Manage the payment method options available when logging a coupon.</p>
        {settings.data.networks.map((network) => (
          <div className={styles.networkRow} key={network.id}>
            <label className="visually-hidden" htmlFor={`network-${network.id}`}>
              {network.name}
            </label>
            <input
              id={`network-${network.id}`}
              className={styles.networkInput}
              defaultValue={network.name}
              disabled={!network.active}
              onBlur={(e) => {
                const name = e.target.value.trim();
                if (name && name !== network.name) {
                  updateNetwork.mutate({ id: network.id, name });
                }
              }}
            />
            <button
              type="button"
              className={styles.removeButton}
              onClick={() => updateNetwork.mutate({ id: network.id, active: !network.active })}
              aria-label={`${network.active ? "Deactivate" : "Reactivate"} ${network.name}`}
            >
              {network.active ? "Deactivate" : "Reactivate"}
            </button>
          </div>
        ))}
        <div className={styles.addNetworkRow}>
          <label className="visually-hidden" htmlFor="new-network">
            New network name
          </label>
          <input
            id="new-network"
            className={styles.networkInput}
            value={newNetwork}
            onChange={(e) => setNewNetwork(e.target.value)}
            placeholder="Add a network, e.g. ConnectIPS"
          />
          <button type="button" onClick={handleAddNetwork} disabled={addNetwork.isPending}>
            {addNetwork.isPending ? "Adding…" : "Add"}
          </button>
        </div>
      </section>

      <section className={styles.section} aria-label="Notification preferences">
        <h2>Notifications</h2>
        <div className={styles.checkboxRow}>
          <input
            id="notif-new-match"
            type="checkbox"
            checked={notifyDraft.notify_new_match ?? false}
            onChange={() => toggleNotificationPref("notify_new_match")}
          />
          <label htmlFor="notif-new-match">Notify me about new matches</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-claim-expiring"
            type="checkbox"
            checked={notifyDraft.notify_claim_expiring ?? false}
            onChange={() => toggleNotificationPref("notify_claim_expiring")}
          />
          <label htmlFor="notif-claim-expiring">Notify me when a claim deadline is approaching</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-claim-expired"
            type="checkbox"
            checked={notifyDraft.notify_claim_expired ?? false}
            onChange={() => toggleNotificationPref("notify_claim_expired")}
          />
          <label htmlFor="notif-claim-expired">Notify me when a claim has expired</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-new-sync"
            type="checkbox"
            checked={notifyDraft.notify_sync_updates ?? false}
            onChange={() => toggleNotificationPref("notify_sync_updates")}
          />
          <label htmlFor="notif-new-sync">Notify me when new government data is available</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-sync-failed"
            type="checkbox"
            checked={notifyDraft.notify_sync_failures ?? false}
            onChange={() => toggleNotificationPref("notify_sync_failures")}
          />
          <label htmlFor="notif-sync-failed">Notify me if synchronization fails</label>
        </div>
        <button
          type="button"
          className={styles.saveButton}
          onClick={handleSaveNotifications}
          disabled={updateSettings.isPending}
        >
          {updateSettings.isPending ? "Saving…" : "Save settings"}
        </button>
        {updateSettings.isError && <ErrorState error={updateSettings.error} />}
        {updateSettings.isSuccess && <p role="status">Settings saved.</p>}
      </section>

      <section className={styles.section} aria-label="Synchronization">
        <h2>Synchronization</h2>
        {syncStatus.isSuccess && (
          <p>
            {syncStatus.data.is_running
              ? "A sync is currently running."
              : syncStatus.data.latest_run
              ? `Last sync: ${syncStatus.data.latest_run.status} at ${new Date(
                  syncStatus.data.latest_run.finished_at ?? syncStatus.data.latest_run.started_at
                ).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })}`
              : "Never synced yet."}
          </p>
        )}
        <button
          type="button"
          onClick={() => triggerSync.mutate()}
          disabled={triggerSync.isPending || syncStatus.data?.is_running}
        >
          {triggerSync.isPending ? "Syncing…" : "Sync now"}
        </button>
      </section>
    </div>
  );
}
