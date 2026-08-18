import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { Register } from "./Register";
import { Login } from "./Login";
import { renderWithProviders } from "../test/testUtils";
import { getStoredToken } from "../api/client";
import { fixtureUser } from "../test/fixtures";

describe("Register page", () => {
  it("creates an account, does not log in, and redirects to the login page", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>,
      { route: "/register" }
    );

    await user.type(screen.getByLabelText(/email/i), "brand-new-user@example.com");
    await user.type(screen.getByLabelText(/password/i), "a-long-enough-password");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText(/account created/i)).toBeInTheDocument();
    expect(getStoredToken()).toBeFalsy();
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
