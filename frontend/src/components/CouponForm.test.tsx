import { describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CouponForm } from "./CouponForm";
import { renderWithProviders } from "../test/testUtils";

describe("CouponForm", () => {
  it("shows validation errors when submitted empty", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<CouponForm onSubmit={onSubmit} />);

    await user.click(screen.getByRole("button", { name: /save coupon/i }));

    expect(await screen.findByText(/coupon code is required/i)).toBeInTheDocument();
    expect(screen.getByText(/transaction date is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits normalized values when the form is valid", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<CouponForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/coupon code/i), "007 315 254 493");
    await user.type(screen.getByLabelText(/transaction date/i), "2026-07-20");
    await user.selectOptions(screen.getByLabelText(/fiscal year/i), "2083-84");

    await user.click(screen.getByRole("button", { name: /save coupon/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        coupon_code: "007 315 254 493",
        transaction_date: "2026-07-20",
        fiscal_year: "2083-84",
      })
    );
  });

  it("shows a submit error message when provided", () => {
    renderWithProviders(<CouponForm onSubmit={vi.fn()} submitError="We couldn't save this coupon." />);
    expect(screen.getByRole("alert")).toHaveTextContent(/couldn't save this coupon/i);
  });
});
