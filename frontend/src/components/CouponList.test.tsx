import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { CouponList, deriveMatchStatus } from "./CouponList";
import { renderWithProviders } from "../test/testUtils";
import { fixtureCoupons, fixtureDrawPeriods, fixtureMatches } from "../test/fixtures";
import type { DrawPeriodStatus } from "../api/types";

describe("CouponList", () => {
  it("shows the empty state when there are no coupons", () => {
    renderWithProviders(<CouponList coupons={[]} matches={[]} onDelete={vi.fn()} />);
    expect(screen.getByText(/add your first coupon to start tracking/i)).toBeInTheDocument();
  });

  it("renders each coupon with its match status", () => {
    renderWithProviders(<CouponList coupons={fixtureCoupons} matches={fixtureMatches} onDelete={vi.fn()} />);

    expect(screen.getByText("007315254493")).toBeInTheDocument();
    expect(screen.getByText(/claim active/i)).toBeInTheDocument();
    expect(screen.getByText(/claim expiring soon/i)).toBeInTheDocument();
    // coupon-3 has no match.
    expect(screen.getByText(/no match found yet/i)).toBeInTheDocument();
  });

  it("shows the draw period window for coupons that are matched", () => {
    renderWithProviders(
      <CouponList
        coupons={fixtureCoupons}
        matches={fixtureMatches}
        drawPeriods={fixtureDrawPeriods}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("Jul 17, 2026 – Jul 31, 2026")).toBeInTheDocument();
  });

  it("shows 'not yet checked' instead of 'no match' when the draw hasn't happened yet", () => {
    const pendingPeriod: DrawPeriodStatus = {
      coupon_id: fixtureCoupons[2].id,
      state: "PENDING",
      eligible_from: "2026-08-17",
      eligible_to: "2026-08-31",
      draw_id: null,
      draw_title_en: null,
      published_at: null,
      estimated_publish_date: "2026-09-01",
      is_estimated: true,
    };
    renderWithProviders(
      <CouponList
        coupons={fixtureCoupons}
        matches={[]}
        drawPeriods={[pendingPeriod]}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText(/not yet checked/i)).toBeInTheDocument();
    expect(screen.getByText("Aug 17, 2026 – Aug 31, 2026 (est.)")).toBeInTheDocument();
  });

  it("calls onDelete with the right coupon when Delete is clicked", async () => {
    const onDelete = vi.fn();
    renderWithProviders(<CouponList coupons={fixtureCoupons} matches={[]} onDelete={onDelete} />);
    const deleteButtons = screen.getAllByRole("button", { name: /delete coupon/i });
    deleteButtons[0].click();
    expect(onDelete).toHaveBeenCalledWith(fixtureCoupons[0]);
  });
});

describe("deriveMatchStatus", () => {
  it("returns the match's claim status when matched", () => {
    expect(deriveMatchStatus(fixtureCoupons[0], fixtureMatches)).toBe("CLAIM_ACTIVE");
  });

  it("returns NO_MATCH when the covering draw has already happened", () => {
    const drawn: DrawPeriodStatus = {
      coupon_id: fixtureCoupons[2].id,
      state: "DRAWN",
      eligible_from: "2026-06-16",
      eligible_to: "2026-06-30",
      draw_id: "draw_daily_0",
      draw_title_en: null,
      published_at: "2026-07-01T09:00:00+05:45",
      estimated_publish_date: null,
      is_estimated: false,
    };
    expect(deriveMatchStatus(fixtureCoupons[2], [], [drawn])).toBe("NO_MATCH");
  });

  it("returns NOT_CHECKED when the draw period isn't drawn yet", () => {
    const pending: DrawPeriodStatus = {
      coupon_id: fixtureCoupons[2].id,
      state: "PENDING",
      eligible_from: "2026-08-17",
      eligible_to: "2026-08-31",
      draw_id: null,
      draw_title_en: null,
      published_at: null,
      estimated_publish_date: "2026-09-01",
      is_estimated: true,
    };
    expect(deriveMatchStatus(fixtureCoupons[2], [], [pending])).toBe("NOT_CHECKED");
  });

  it("returns NO_MATCH with no draw-period data at all", () => {
    expect(deriveMatchStatus(fixtureCoupons[2], [])).toBe("NO_MATCH");
  });
});
