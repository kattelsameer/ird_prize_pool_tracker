import { describe, expect, it } from "vitest";
import { drawPeriodPresentation } from "./drawPeriod";
import type { DrawPeriodStatus } from "../api/types";

describe("drawPeriodPresentation", () => {
  it("falls back to a dash when there's no status at all", () => {
    const result = drawPeriodPresentation(undefined);
    expect(result.label).toBe("—");
  });

  it("shows the real published window for a DRAWN period", () => {
    const status: DrawPeriodStatus = {
      coupon_id: "c1",
      state: "DRAWN",
      eligible_from: "2026-08-01",
      eligible_to: "2026-08-16",
      draw_id: "draw-1",
      draw_title_en: "Fortnightly Draw",
      published_at: "2026-08-17T00:00:00Z",
      estimated_publish_date: null,
      is_estimated: false,
    };
    const result = drawPeriodPresentation(status);
    expect(result.label).toBe("Aug 1, 2026 – Aug 16, 2026");
    expect(result.detail).toMatch(/published/i);
  });

  it("flags a PENDING period as estimated with an expected publish date", () => {
    const status: DrawPeriodStatus = {
      coupon_id: "c2",
      state: "PENDING",
      eligible_from: "2026-08-17",
      eligible_to: "2026-08-31",
      draw_id: null,
      draw_title_en: null,
      published_at: null,
      estimated_publish_date: "2026-09-01",
      is_estimated: true,
    };
    const result = drawPeriodPresentation(status);
    expect(result.label).toBe("Aug 17, 2026 – Aug 31, 2026 (est.)");
    expect(result.detail).toMatch(/still open/i);
    expect(result.detail).toMatch(/estimated/i);
  });

  it("keeps an UNKNOWN period honest about missing data", () => {
    const status: DrawPeriodStatus = {
      coupon_id: "c3",
      state: "UNKNOWN",
      eligible_from: null,
      eligible_to: null,
      draw_id: null,
      draw_title_en: null,
      published_at: null,
      estimated_publish_date: null,
      is_estimated: false,
    };
    const result = drawPeriodPresentation(status);
    expect(result.label).toBe("Not synced yet");
  });
});
