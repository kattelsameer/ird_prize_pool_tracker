import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Coupons } from "./Coupons";
import { renderWithProviders } from "../test/testUtils";

describe("Coupons page", () => {
  it("lists coupons from the mock API and filters by search", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Coupons />);

    expect(await screen.findByText("007315254493")).toBeInTheDocument();
    expect(screen.getByText("000000000001")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/search by code/i), "007315254493");

    await waitFor(() => {
      expect(screen.queryByText("000000000001")).not.toBeInTheDocument();
    });
    expect(screen.getByText("007315254493")).toBeInTheDocument();
  });

  it("opens the add-coupon modal and adds a new coupon that then appears in the list", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Coupons />);

    await screen.findByText("007315254493");

    await user.click(screen.getByRole("button", { name: /add coupon/i }));
    const dialog = await screen.findByRole("dialog", { name: /add a coupon/i });

    await user.type(screen.getByLabelText(/coupon code/i), "123456789012");
    await user.type(screen.getByLabelText(/transaction date/i), "2026-08-01");
    await user.click(screen.getByRole("button", { name: /save coupon/i }));

    await waitFor(() => expect(dialog).not.toBeInTheDocument());
    expect(await screen.findByText("123456789012")).toBeInTheDocument();
  });
});
