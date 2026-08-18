import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAddNetwork, useSettings, useUpdateNetwork, useUpdateSettings } from "../api/settings";
import { useSyncStatus, useTriggerSync } from "../api/sync";
import { useCurrentUser, useLogout } from "../api/auth";
import { useDeleteAccount, useExportAccountData, useProfile, useUpdateProfile } from "../api/profile";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { Modal } from "../components/Modal";
import type { SettingsUpdate } from "../api/types";
import styles from "./Settings.module.css";

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function AccountSection() {
  const currentUser = useCurrentUser();
  const profile = useProfile();
  const updateProfile = useUpdateProfile();
  const exportData = useExportAccountData();
  const deleteAccount = useDeleteAccount();
  const logout = useLogout();
  const navigate = useNavigate();

  const [displayName, setDisplayName] = useState("");
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  // Seed the editable field from the server value once it arrives -- an
  // in-render adjustment (not an effect) so a later refetch never clobbers
  // an in-progress edit once the initial sync has happened.
  const [syncedDisplayName, setSyncedDisplayName] = useState<string | null>(null);
  if (profile.data && profile.data.display_name !== syncedDisplayName) {
    setSyncedDisplayName(profile.data.display_name);
    setDisplayName(profile.data.display_name ?? "");
  }

  function handleSaveDisplayName(event: FormEvent) {
    event.preventDefault();
    updateProfile.mutate({ display_name: displayName.trim() || null });
  }

  function handleExport() {
    exportData.mutate(undefined, {
      onSuccess: (data) => downloadJson(`couponsathi-my-data-${data.exported_at.slice(0, 10)}.json`, data),
    });
  }

  function handleConfirmDelete() {
    deleteAccount.mutate(undefined, {
      onSuccess: () => {
        logout();
        navigate("/login", { replace: true });
      },
    });
  }

  return (
    <section className={styles.section} aria-label="Account">
      <h2>Account</h2>
      {currentUser.data && (
        <p>
          Signed in as <strong>{currentUser.data.email}</strong>
        </p>
      )}

      <form onSubmit={handleSaveDisplayName} className={styles.accountForm}>
        <label htmlFor="display-name">Display name</label>
        <input
          id="display-name"
          className={styles.networkInput}
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="e.g. Ram Bahadur"
        />
        <button type="submit" className={styles.saveButton} disabled={updateProfile.isPending}>
          {updateProfile.isPending ? "Saving…" : "Save name"}
        </button>
      </form>
      {updateProfile.isSuccess && <p role="status">Display name saved.</p>}
      {updateProfile.isError && <ErrorState error={updateProfile.error} />}

      <div>
        <h3>Your data</h3>
        <p>
          Download a copy of everything you've entered (your profile and coupons), or permanently
          delete your account and all associated data.
        </p>
        <div className={styles.addNetworkRow}>
          <button type="button" onClick={handleExport} disabled={exportData.isPending}>
            {exportData.isPending ? "Preparing…" : "Download my data"}
          </button>
          <button type="button" className={styles.removeButton} onClick={() => setConfirmingDelete(true)}>
            Delete my account
          </button>
        </div>
        {exportData.isError && <ErrorState error={exportData.error} />}
      </div>

      {confirmingDelete && (
        <Modal title="Delete your account?" onClose={() => setConfirmingDelete(false)}>
          <p>
            This permanently deletes your account, profile, and every coupon you've entered. This
            cannot be undone.
          </p>
          {deleteAccount.isError && <ErrorState error={deleteAccount.error} />}
          <div className={styles.addNetworkRow}>
            <button
              type="button"
              className={styles.removeButton}
              onClick={handleConfirmDelete}
              disabled={deleteAccount.isPending}
            >
              {deleteAccount.isPending ? "Deleting…" : "Yes, delete my account"}
            </button>
            <button type="button" onClick={() => setConfirmingDelete(false)}>
              Cancel
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}

export function Settings() {
  const settings = useSettings();
  const updateSettings = useUpdateSettings();
  const addNetwork = useAddNetwork();
  const updateNetwork = useUpdateNetwork();
  const syncStatus = useSyncStatus();
  const triggerSync = useTriggerSync();

  const [notifyDraft, setNotifyDraft] = useState<SettingsUpdate | null>(null);
  const [newNetwork, setNewNetwork] = useState("");

  // In-render initialization (not an effect): seeds the draft once from the
  // first successful fetch, guarded so it never overwrites in-progress edits.
  if (settings.data && !notifyDraft) {
    setNotifyDraft({
      notify_new_match: settings.data.notify_new_match,
      notify_claim_expiring: settings.data.notify_claim_expiring,
      notify_claim_expired: settings.data.notify_claim_expired,
      notify_sync_updates: settings.data.notify_sync_updates,
      notify_sync_failures: settings.data.notify_sync_failures,
    });
  }

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

      <AccountSection />

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
              className={styles.secondaryButton}
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
          className={styles.saveButton}
          onClick={() => triggerSync.mutate()}
          disabled={triggerSync.isPending || syncStatus.data?.is_running}
        >
          {triggerSync.isPending || syncStatus.data?.is_running ? "Syncing…" : "Sync now"}
        </button>
        {triggerSync.data && !triggerSync.data.accepted && (
          <p role="status">{triggerSync.data.message}</p>
        )}
        {triggerSync.isError && <ErrorState error={triggerSync.error} />}
      </section>
    </div>
  );
}
