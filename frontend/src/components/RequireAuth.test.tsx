import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { RequireAuth } from "./RequireAuth";
import { createTestQueryClient } from "../test/testUtils";
import { setStoredToken } from "../api/client";

function renderProtectedApp(initialEntry: string) {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route element={<RequireAuth />}>
            <Route path="/" element={<div>Protected dashboard</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("RequireAuth", () => {
  it("redirects to /login when there is no stored token", async () => {
    renderProtectedApp("/");
    expect(await screen.findByText(/login page/i)).toBeInTheDocument();
  });

  it("renders the protected route when a valid token is present", async () => {
    setStoredToken("fixture-token");
    renderProtectedApp("/");
    expect(await screen.findByText(/protected dashboard/i)).toBeInTheDocument();
  });

  it("redirects to /login when the stored token is invalid", async () => {
    setStoredToken("not-a-real-token");
    renderProtectedApp("/");
    expect(await screen.findByText(/login page/i)).toBeInTheDocument();
  });
});
