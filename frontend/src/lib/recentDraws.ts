/**
 * Groups the Dashboard's "recent prize-pool updates" feed by draw so the UI shows one
 * summarized line per draw event instead of one near-identical line per individual winner
 * record. This only rolls up records the API already returned (a small "recent" page) --
 * it never claims a total winner count beyond what was actually fetched (CLAUDE.md §66:
 * never fabricate data), so the label always describes exactly what's summarized.
 */
import type { PrizePool } from "../api/types";

export interface RecentDrawSummary {
  draw_id: string;
  published_at: string;
  eligible_from: string | null;
  eligible_to: string | null;
  categoryCounts: { category: string; count: number }[];
}

export function summarizeRecentDraws(items: PrizePool[]): RecentDrawSummary[] {
  const order: string[] = [];
  const byDraw = new Map<string, PrizePool[]>();
  for (const item of items) {
    if (!byDraw.has(item.draw_id)) order.push(item.draw_id);
    const list = byDraw.get(item.draw_id) ?? [];
    list.push(item);
    byDraw.set(item.draw_id, list);
  }

  return order
    .map((drawId) => {
      const drawItems = byDraw.get(drawId)!;
      const counts = new Map<string, number>();
      for (const item of drawItems) {
        const key = item.category ?? "Prize";
        counts.set(key, (counts.get(key) ?? 0) + 1);
      }
      const first = drawItems[0];
      return {
        draw_id: drawId,
        published_at: first.published_at,
        eligible_from: first.eligible_from,
        eligible_to: first.eligible_to,
        categoryCounts: Array.from(counts.entries()).map(([category, count]) => ({ category, count })),
      };
    })
    .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime());
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function recentDrawLabel(summary: RecentDrawSummary): string {
  const counts = summary.categoryCounts.map((c) => `${c.count} ${c.category}`).join(", ");
  const published = formatDate(summary.published_at);
  const period =
    summary.eligible_from && summary.eligible_to
      ? ` (for ${formatDate(summary.eligible_from)} – ${formatDate(summary.eligible_to)})`
      : "";
  return `${counts} — published ${published}${period}`;
}
