import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NavBar } from "./NavBar";
import { renderWithProviders } from "../test/testUtils";

// The hamburger button is only shown via a max-width media query (mobile), which jsdom's
// default viewport never matches, so testing-library's accessible-name computation treats it
// as inaccessible even with `hidden: true` (that option only affects role inclusion, not name
// computation for CSS-hidden elements). Read the raw aria-label instead of relying on
// getByRole's name matcher for this specific button.
function getMenuButton() {
  return screen
    .getAllByRole("button", { hidden: true })
    .find((button) => /(open|close) menu/i.test(button.getAttribute("aria-label") ?? ""))!;
}

describe("NavBar", () => {
  it("renders all primary links, always in the DOM (CSS handles the mobile collapse)", () => {
    renderWithProviders(<NavBar />);
    expect(screen.getByRole("link", { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /my coupons/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /prize pool explorer/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /settings/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /about the program/i })).toBeInTheDocument();
  });

  it("toggles the mobile menu button's expanded state and label on click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NavBar />);

    expect(getMenuButton()).toHaveAttribute("aria-expanded", "false");
    expect(getMenuButton()).toHaveAttribute("aria-label", "Open menu");

    await user.click(getMenuButton());
    expect(getMenuButton()).toHaveAttribute("aria-expanded", "true");
    expect(getMenuButton()).toHaveAttribute("aria-label", "Close menu");

    await user.click(getMenuButton());
    expect(getMenuButton()).toHaveAttribute("aria-expanded", "false");
  });

  it("closes the mobile menu on Escape", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NavBar />);

    await user.click(getMenuButton());
    expect(getMenuButton()).toHaveAttribute("aria-expanded", "true");

    await user.keyboard("{Escape}");
    expect(getMenuButton()).toHaveAttribute("aria-expanded", "false");
  });

  it("closes the mobile menu after navigating to a link", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NavBar />);

    await user.click(getMenuButton());
    await user.click(screen.getByRole("link", { name: /my coupons/i }));

    expect(getMenuButton()).toHaveAttribute("aria-expanded", "false");
  });
});
