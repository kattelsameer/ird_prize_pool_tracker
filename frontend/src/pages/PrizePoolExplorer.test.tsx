import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { PrizePoolExplorer } from "./PrizePoolExplorer";
import { renderWithProviders } from "../test/testUtils";
import { server } from "../test/server";

describe("PrizePoolExplorer page", () => {
  it("shows a loading state, then the fixture draws", async () => {
    renderWithProviders(<PrizePoolExplorer />);
    expect(screen.getAllByText(/loading/i).length).toBeGreaterThan(0);
    expect(await screen.findByText("007315254493")).toBeInTheDocument();
  });

  it("shows an empty state when no records match the filters", async () => {
    server.use(
      http.get("http://localhost:8000/api/prize-pools", () =>
        HttpResponse.json({ items: [], total: 0, limit: 20, offset: 0 })
      )
    );
    renderWithProviders(<PrizePoolExplorer />);
    expect(await screen.findByText(/no prize-pool records match your filters/i)).toBeInTheDocument();
  });

  it("shows a user-safe error state on failure", async () => {
    server.use(http.get("http://localhost:8000/api/prize-pools", () => HttpResponse.error()));
    renderWithProviders(<PrizePoolExplorer />);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
