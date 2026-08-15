import type { ReactNode } from "react";
import styles from "./NoticeBanner.module.css";

export type NoticeTone = "urgent" | "warning" | "info" | "success";

export interface NoticeBannerProps {
  tone: NoticeTone;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}

const ICONS: Record<NoticeTone, string> = {
  urgent: "⚠",
  warning: "⏰",
  info: "ℹ",
  success: "✓",
};

/** A prominent, non-color-only notice for the dashboard's attention area (§32). */
export function NoticeBanner({ tone, title, children, action }: NoticeBannerProps) {
  return (
    <div className={`${styles.banner} ${styles[tone]}`} role={tone === "urgent" ? "alert" : "status"}>
      <span aria-hidden="true" className={styles.icon}>
        {ICONS[tone]}
      </span>
      <div className={styles.body}>
        <p className={styles.title}>{title}</p>
        {children && <div className={styles.content}>{children}</div>}
      </div>
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
