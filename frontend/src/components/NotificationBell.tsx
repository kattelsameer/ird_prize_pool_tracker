import { useEffect, useRef, useState } from "react";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "../api/notifications";
import type { AppNotification, NotificationType } from "../api/types";
import styles from "./NotificationBell.module.css";

const TYPE_ICON: Record<NotificationType, string> = {
  NEW_MATCH: "🎉",
  CLAIM_EXPIRING: "⏰",
  CLAIM_EXPIRED: "⛔",
  NEW_SYNC_DATA: "🔄",
  SYNC_FAILED: "⚠",
};

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { data, isLoading, isError } = useNotifications();
  const notifications = data?.items ?? [];
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div className={styles.container} ref={containerRef}>
      <button
        type="button"
        className={styles.bellButton}
        aria-haspopup="true"
        aria-expanded={open}
        aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
        onClick={() => setOpen((v) => !v)}
      >
        <span aria-hidden="true">🔔</span>
        {unreadCount > 0 && <span className={styles.badge}>{unreadCount > 9 ? "9+" : unreadCount}</span>}
      </button>

      {open && (
        <div className={styles.panel} role="dialog" aria-label="Notifications">
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle}>Notifications</h2>
            {unreadCount > 0 && (
              <button
                type="button"
                className={styles.markAllButton}
                onClick={() => markAllRead.mutate()}
              >
                Mark all read
              </button>
            )}
          </div>

          <div aria-live="polite" className={styles.list}>
            {isLoading && <p className={styles.empty}>Loading notifications…</p>}
            {isError && <p className={styles.empty}>Notifications couldn't be loaded right now.</p>}
            {!isLoading && !isError && notifications.length === 0 && (
              <p className={styles.empty}>You have no notifications yet.</p>
            )}
            {notifications.map((notification: AppNotification) => (
              <div
                key={notification.id}
                className={`${styles.item} ${notification.read_at ? "" : styles.unread}`}
              >
                <span aria-hidden="true" className={styles.itemIcon}>
                  {TYPE_ICON[notification.type]}
                </span>
                <div className={styles.itemBody}>
                  <p className={styles.itemMessage}>{notification.message}</p>
                  <p className={styles.itemMeta}>
                    {new Date(notification.created_at).toLocaleString("en-US", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </p>
                </div>
                {!notification.read_at && (
                  <button
                    type="button"
                    className={styles.readButton}
                    onClick={() => markRead.mutate(notification.id)}
                  >
                    Mark read
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
