import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { CouponList } from "./CouponList";
import { renderWithProviders } from "../test/testUtils";
import { fixtureCoupons, fixtureMatches } from "../test/fixtures";

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

  it("calls onDelete with the right coupon when Delete is clicked", async () => {
    const onDelete = vi.fn();
    renderWithProviders(<CouponList coupons={fixtureCoupons} matches={[]} onDelete={onDelete} />);
    const deleteButtons = screen.getAllByRole("button", { name: /delete coupon/i });
    deleteButtons[0].click();
    expect(onDelete).toHaveBeenCalledWith(fixtureCoupons[0]);
  });
});
