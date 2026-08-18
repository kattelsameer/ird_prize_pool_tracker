/**
 * Human-readable summary of which draw period governs a coupon's transaction
 * date, and whether that draw has actually happened yet (CLAUDE.md §6/§65 --
 * this is application-derived context, never a claim about whether the
 * coupon won; pair with the coupon's match status for that). The backend
 * (`app.domain.draw_period`) is the sole authority on the DRAWN/PENDING/
 * UNKNOWN classification and any estimated dates -- this module only formats
 * what it already computed.
 */
import type { DrawPeriodStatus } from "../api/types";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export interface DrawPeriodPresentation {
  label: string;
  detail: string;
}

/** Icon + pill tone for a draw-period state, so it gets the same visual language as
 * match status (§45: never color alone) instead of being bare, unstyled text. */
export function drawPeriodPillProps(status: DrawPeriodStatus | undefined): {
  icon: string;
  tone: "neutral" | "estimate" | "warning";
} {
  switch (status?.state) {
    case "DRAWN":
      return { icon: "✓", tone: "neutral" };
    case "PENDING":
      return { icon: "…", tone: "estimate" };
    case "UNKNOWN":
    default:
      return { icon: "?", tone: "warning" };
  }
}

export function drawPeriodPresentation(status: DrawPeriodStatus | undefined): DrawPeriodPresentation {
  if (!status) {
    return { label: "—", detail: "No transaction date on file for this coupon." };
  }

  const from = status.eligible_from ? formatDate(status.eligible_from) : null;
  const to = status.eligible_to ? formatDate(status.eligible_to) : null;

  switch (status.state) {
    case "DRAWN":
      return {
        label: `${from} – ${to}`,
        detail: status.published_at
          ? `Draw published ${formatDate(status.published_at)}.`
          : "Draw already published.",
      };
    case "PENDING": {
      const estimate = status.estimated_publish_date ? formatDate(status.estimated_publish_date) : null;
      return {
        label: `${from} – ${to} (est.)`,
        detail: estimate
          ? `Period still open. Results expected around ${estimate} (estimated -- not yet published by IRD).`
          : "Period still open. No draw yet.",
      };
    }
    case "UNKNOWN":
    default:
      return { label: "Not synced yet", detail: "We don't yet have draw data covering this date." };
  }
}
