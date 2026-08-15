import type { ReactNode } from "react";
import styles from "./DataSourceBadge.module.css";

export type DataSource = "government" | "user" | "app";

const CONFIG: Record<DataSource, { icon: string; label: string }> = {
  government: { icon: "🏛", label: "IRD published data" },
  user: { icon: "🧾", label: "Your entry" },
  app: { icon: "⚙", label: "App-calculated" },
};

export interface DataSourceBadgeProps {
  source: DataSource;
  /** Override the default label, e.g. to add specifics. The source category label is always shown too. */
  children?: ReactNode;
}

/**
 * Always renders an icon glyph *and* a text label naming the data-source category, per
 * CLAUDE.md §10d/§65: never rely on color alone, and never blur the line between government
 * data, user data, and application-derived conclusions.
 */
export function DataSourceBadge({ source, children }: DataSourceBadgeProps) {
  const config = CONFIG[source];
  return (
    <span className={`${styles.badge} ${styles[source]}`} data-source={source}>
      <span aria-hidden="true" className={styles.icon}>
        {config.icon}
      </span>
      <span className={styles.label}>
        {config.label}
        {children ? <>: {children}</> : null}
      </span>
    </span>
  );
}
