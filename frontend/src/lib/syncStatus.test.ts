import { describe, expect, it } from "vitest";
import { formatSyncRunCounts } from "./syncStatus";
import type { SyncRun } from "../api/types";

const baseRun: SyncRun = {
  id: "run-1",
  started_at: "2026-08-19T00:00:00Z",
  finished_at: "2026-08-19T00:00:05Z",
  status: "success",
  records_received: 15,
  records_inserted: 12,
  records_updated: 3,
  records_skipped: 0,
  error_message: null,
};

describe("formatSyncRunCounts", () => {
  it("summarizes received/new/updated counts", () => {
    expect(formatSyncRunCounts(baseRun)).toBe("15 received, 12 new, 3 updated");
  });
});
