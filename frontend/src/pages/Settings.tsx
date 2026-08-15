import { useEffect, useState } from "react";
import { useSettings, useUpdateSettings } from "../api/settings";
import { useSyncStatus, useTriggerSync } from "../api/sync";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import type { Settings as SettingsType } from "../api/types";
import styles from "./Settings.module.css";

export function Settings() {
  const settings = useSettings();
  const updateSettings = useUpdateSettings();
  const syncStatus = useSyncStatus();
  const triggerSync = useTriggerSync();

  const [draft, setDraft] = useState<SettingsType | null>(null);
  const [newNetwork, setNewNetwork] = useState("");

  useEffect(() => {
    if (settings.data && !draft) setDraft(settings.data);
  }, [settings.data, draft]);

  if (settings.isLoading) return <LoadingState label="Loading settings…" />;
  if (settings.isError) return <ErrorState error={settings.error} onRetry={() => settings.refetch()} />;
  if (!draft) return null;

  function updateNetwork(index: number, value: string) {
    setDraft((d) => (d ? { ...d, networks: d.networks.map((n, i) => (i === index ? value : n)) } : d));
  }

  function removeNetwork(index: number) {
    setDraft((d) => (d ? { ...d, networks: d.networks.filter((_, i) => i !== index) } : d));
  }

  function addNetwork() {
    if (!newNetwork.trim()) return;
    setDraft((d) => (d ? { ...d, networks: [...d.networks, newNetwork.trim()] } : d));
    setNewNetwork("");
  }

  function toggleNotificationPref(key: keyof SettingsType["notification_prefs"]) {
    setDraft((d) =>
      d
        ? {
            ...d,
            notification_prefs: { ...d.notification_prefs, [key]: !d.notification_prefs[key] },
          }
        : d
    );
  }

  function handleSave() {
    if (draft) updateSettings.mutate(draft);
  }

  return (
    <div className={styles.page}>
      <h1>Settings</h1>

      <section className={styles.section} aria-label="Networks">
        <h2>Networks / payment methods</h2>
        <p>Manage the payment method options available when logging a coupon.</p>
        {draft.networks.map((network, index) => (
          <div className={styles.networkRow} key={index}>
            <label className="visually-hidden" htmlFor={`network-${index}`}>
              Network {index + 1}
            </label>
            <input
              id={`network-${index}`}
              className={styles.networkInput}
              value={network}
              onChange={(e) => updateNetwork(index, e.target.value)}
            />
            <button
              type="button"
              className={styles.removeButton}
              onClick={() => removeNetwork(index)}
              aria-label={`Remove ${network}`}
            >
              Remove
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
          <button type="button" onClick={addNetwork}>
            Add
          </button>
        </div>
      </section>

      <section className={styles.section} aria-label="Notification preferences">
        <h2>Notifications</h2>
        <div className={styles.checkboxRow}>
          <input
            id="notif-new-match"
            type="checkbox"
            checked={draft.notification_prefs.new_match}
            onChange={() => toggleNotificationPref("new_match")}
          />
          <label htmlFor="notif-new-match">Notify me about new matches</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-claim-expiring"
            type="checkbox"
            checked={draft.notification_prefs.claim_expiring}
            onChange={() => toggleNotificationPref("claim_expiring")}
          />
          <label htmlFor="notif-claim-expiring">Notify me when a claim deadline is approaching</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-claim-expired"
            type="checkbox"
            checked={draft.notification_prefs.claim_expired}
            onChange={() => toggleNotificationPref("claim_expired")}
          />
          <label htmlFor="notif-claim-expired">Notify me when a claim has expired</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-new-sync"
            type="checkbox"
            checked={draft.notification_prefs.new_sync_data}
            onChange={() => toggleNotificationPref("new_sync_data")}
          />
          <label htmlFor="notif-new-sync">Notify me when new government data is available</label>
        </div>
        <div className={styles.checkboxRow}>
          <input
            id="notif-sync-failed"
            type="checkbox"
            checked={draft.notification_prefs.sync_failed}
            onChange={() => toggleNotificationPref("sync_failed")}
          />
          <label htmlFor="notif-sync-failed">Notify me if synchronization fails</label>
        </div>
      </section>

      <section className={styles.section} aria-label="Synchronization">
        <h2>Synchronization</h2>
        {syncStatus.isSuccess && (
          <p>
            {syncStatus.data.is_running
              ? "A sync is currently running."
              : syncStatus.data.last_sync
              ? `Last sync: ${syncStatus.data.last_sync.status} at ${new Date(
                  syncStatus.data.last_sync.sync_finished_at ?? syncStatus.data.last_sync.sync_started_at
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

      {updateSettings.isError && <ErrorState error={updateSettings.error} />}
      <button type="button" className={styles.saveButton} onClick={handleSave} disabled={updateSettings.isPending}>
        {updateSettings.isPending ? "Saving…" : "Save settings"}
      </button>
      {updateSettings.isSuccess && <p role="status">Settings saved.</p>}
    </div>
  );
}
