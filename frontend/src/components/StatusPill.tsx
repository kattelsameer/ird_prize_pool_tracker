import styles from "./StatusPill.module.css";

export type PillTone = "neutral" | "success" | "warning" | "danger" | "estimate";

export interface StatusPillProps {
  tone: PillTone;
  icon: string;
  label: string;
}

/**
 * Small icon+text status chip. Shared by MatchStatusTag and the draw-period badge so the
 * two status concepts a coupon can have (did it match, has its draw even happened yet)
 * get the same visual language instead of one having a pill and the other bare text.
 * Never color alone (§45): icon and label are always both present.
 */
export function StatusPill({ tone, icon, label }: StatusPillProps) {
  return (
    <span className={`${styles.pill} ${styles[tone]}`}>
      <span aria-hidden="true">{icon}</span> {label}
    </span>
  );
}
