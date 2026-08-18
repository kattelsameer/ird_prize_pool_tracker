import { describe, expect, it } from "vitest";
import { recentDrawLabel, summarizeRecentDraws } from "./recentDraws";
import { fixturePrizePools } from "../test/fixtures";
import type { PrizePool } from "../api/types";

function winner(overrides: Partial<PrizePool>): PrizePool {
  return { ...fixturePrizePools[0], id: `pp-${Math.random()}`, ...overrides };
}

describe("summarizeRecentDraws", () => {
  it("groups multiple winner records from the same draw into one summary", () => {
    const items = [
      winner({ draw_id: "draw_1", category: "Daily Prize", published_at: "2026-08-17T09:00:00+05:45" }),
      winner({ draw_id: "draw_1", category: "Daily Prize", published_at: "2026-08-17T09:00:00+05:45" }),
      winner({ draw_id: "draw_1", category: "Daily Prize", published_at: "2026-08-17T09:00:00+05:45" }),
      winner({ draw_id: "draw_1", category: "Bumper Prize", published_at: "2026-08-17T09:00:00+05:45" }),
    ];

    const summaries = summarizeRecentDraws(items);

    expect(summaries).toHaveLength(1);
    expect(summaries[0].draw_id).toBe("draw_1");
    expect(summaries[0].categoryCounts).toEqual(
      expect.arrayContaining([
        { category: "Daily Prize", count: 3 },
        { category: "Bumper Prize", count: 1 },
      ])
    );
  });

  it("keeps separate draws as separate summaries, most recently published first", () => {
    const items = [
      winner({ draw_id: "draw_old", category: "Daily Prize", published_at: "2026-08-01T09:00:00+05:45" }),
      winner({ draw_id: "draw_new", category: "Daily Prize", published_at: "2026-08-17T09:00:00+05:45" }),
    ];

    const summaries = summarizeRecentDraws(items);

    expect(summaries.map((s) => s.draw_id)).toEqual(["draw_new", "draw_old"]);
  });

  it("never claims a total beyond what was actually passed in", () => {
    // Only 2 daily-prize records were fetched, even though a real draw has 15 --
    // the summary must reflect exactly what it was given, not the real-world total.
    const items = [
      winner({ draw_id: "draw_1", category: "Daily Prize" }),
      winner({ draw_id: "draw_1", category: "Daily Prize" }),
    ];
    const summaries = summarizeRecentDraws(items);
    expect(summaries[0].categoryCounts).toEqual([{ category: "Daily Prize", count: 2 }]);
  });
});

describe("recentDrawLabel", () => {
  it("renders category counts, publish date, and eligible period", () => {
    const [summary] = summarizeRecentDraws([
      winner({
        draw_id: "draw_1",
        category: "Daily Prize",
        published_at: "2026-08-17T09:00:00+05:45",
        eligible_from: "2026-08-01",
        eligible_to: "2026-08-16",
      }),
    ]);
    expect(recentDrawLabel(summary)).toBe("1 Daily Prize — published Aug 17, 2026 (for Aug 1, 2026 – Aug 16, 2026)");
  });
});
