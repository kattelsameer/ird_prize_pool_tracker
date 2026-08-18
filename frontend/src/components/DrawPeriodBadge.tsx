import { StatusPill } from "./StatusPill";
import { drawPeriodPillProps, drawPeriodPresentation } from "../lib/drawPeriod";
import type { DrawPeriodStatus } from "../api/types";

export interface DrawPeriodBadgeProps {
  status: DrawPeriodStatus | undefined;
}

/** Compact pill for "which draw period covers this coupon, and has it been drawn yet."
 * A tooltip carries the fuller detail sentence for pointer users; the visible label alone
 * (date range, or "(est.)"/"Not synced yet") is enough to understand the state at a glance. */
export function DrawPeriodBadge({ status }: DrawPeriodBadgeProps) {
  const presentation = drawPeriodPresentation(status);
  const { icon, tone } = drawPeriodPillProps(status);
  return (
    <span title={presentation.detail}>
      <StatusPill tone={tone} icon={icon} label={presentation.label} />
    </span>
  );
}
