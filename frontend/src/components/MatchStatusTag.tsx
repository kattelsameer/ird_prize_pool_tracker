import styles from "./MatchStatusTag.module.css";

export type MatchStatus =
  | "NOT_CHECKED"
  | "NO_MATCH"
  | "MATCHED"
  | "CLAIM_ACTIVE"
  | "CLAIM_EXPIRING"
  | "CLAIM_EXPIRED";

const CONFIG: Record<MatchStatus, { icon: string; label: string; tone: string }> = {
  NOT_CHECKED: { icon: "…", label: "Not yet checked", tone: "neutral" },
  NO_MATCH: { icon: "–", label: "No match found yet", tone: "neutral" },
  MATCHED: { icon: "🎉", label: "Matched", tone: "success" },
  CLAIM_ACTIVE: { icon: "✓", label: "Matched · claim active", tone: "success" },
  CLAIM_EXPIRING: { icon: "⚠", label: "Matched · claim expiring soon", tone: "warning" },
  CLAIM_EXPIRED: { icon: "✕", label: "Matched · claim expired", tone: "danger" },
};

export function MatchStatusTag({ status }: { status: MatchStatus }) {
  const config = CONFIG[status] ?? CONFIG.NOT_CHECKED;
  return (
    <span className={`${styles.tag} ${styles[config.tone]}`}>
      <span aria-hidden="true">{config.icon}</span> {config.label}
    </span>
  );
}
