import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Register } from "./Register";
import { renderWithProviders } from "../test/testUtils";
import { getStoredToken } from "../api/client";
import { fixtureUser } from "../test/fixtures";

describe("Register page", () => {
  it("creates an account and stores the access token", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Register />, { route: "/register" });

    await user.type(screen.getByLabelText(/email/i), "brand-new-user@example.com");
    await user.type(screen.getByLabelText(/password/i), "a-long-enough-password");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => {
      expect(getStoredToken()).toBeTruthy();
    });
  });

  it("shows a validation error for a too-short password without submitting", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Register />, { route: "/register" });

    await user.type(screen.getByLabelText(/email/i), "short@example.com");
    await user.type(screen.getByLabelText(/password/i), "short1");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    expect(getStoredToken()).toBeFalsy();
  });

  it("shows an error when the email is already registered", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Register />, { route: "/register" });

    await user.type(screen.getByLabelText(/email/i), fixtureUser.email);
    await user.type(screen.getByLabelText(/password/i), "a-long-enough-password");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("links to the login page", () => {
    renderWithProviders(<Register />, { route: "/register" });
    expect(screen.getByRole("link", { name: /log in/i })).toHaveAttribute("href", "/login");
  });
});
