import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Login } from "./Login";
import { renderWithProviders } from "../test/testUtils";
import { getStoredToken } from "../api/client";
import { fixtureUser } from "../test/fixtures";
import { TEST_USER_PASSWORD } from "../test/handlers";

describe("Login page", () => {
  it("logs in with the correct password and stores the access token", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Login />, { route: "/login" });

    await user.type(screen.getByLabelText(/email/i), fixtureUser.email);
    await user.type(screen.getByLabelText(/password/i), TEST_USER_PASSWORD);
    await user.click(screen.getByRole("button", { name: /^log in$/i }));

    await waitFor(() => {
      expect(getStoredToken()).toBeTruthy();
    });
  });

  it("shows an error and does not store a token on the wrong password", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Login />, { route: "/login" });

    await user.type(screen.getByLabelText(/email/i), fixtureUser.email);
    await user.type(screen.getByLabelText(/password/i), "wrong-password");
    await user.click(screen.getByRole("button", { name: /^log in$/i }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(getStoredToken()).toBeFalsy();
  });

  it("links to the register page", () => {
    renderWithProviders(<Login />, { route: "/login" });
    expect(screen.getByRole("link", { name: /create one/i })).toHaveAttribute("href", "/register");
  });
});
