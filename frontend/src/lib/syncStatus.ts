import type { SyncRun } from "../api/types";

/** Short "records received/inserted/updated" summary for a completed sync run
 * (CLAUDE.md §40 sync observability) -- shared by Dashboard and Settings so the
 * two pages don't drift on wording. */
export function formatSyncRunCounts(run: SyncRun): string {
  return `${run.records_received} received, ${run.records_inserted} new, ${run.records_updated} updated`;
}
