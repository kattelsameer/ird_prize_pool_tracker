import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { Dashboard } from "./Dashboard";
import { renderWithProviders } from "../test/testUtils";
import { server } from "../test/server";

describe("Dashboard page", () => {
  it("shows a loading state before data resolves, then winner cards and summary once loaded", async () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getAllByText(/loading/i).length).toBeGreaterThan(0);

    expect(await screen.findByText(/your winning coupons/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText(/IRD published data/i).length).toBeGreaterThan(0);
    });
  });

  it("shows a new-match notice banner sourced from the paginated notifications response", async () => {
    // Regression test: GET /api/notifications returns a Page[NotificationRead]
    // ({items, total, limit, offset}), not a bare array. Dashboard must read
    // notifications.data.items, not notifications.data, or this throws
    // "(n.data ?? []).filter is not a function" and the whole page crashes.
    renderWithProviders(<Dashboard />);

    expect(await screen.findByText(/new match found/i)).toBeInTheDocument();
    expect(screen.getByText(/matches the bumper prize draw/i)).toBeInTheDocument();
  });

  it("shows a sync-failed notice when the last sync failed", async () => {
    server.use(
      http.get("http://localhost:8000/api/sync/status", () =>
        HttpResponse.json({
          is_running: false,
          last_sync: {
            sync_started_at: "2026-08-15T00:00:00+05:45",
            sync_finished_at: "2026-08-15T00:00:05+05:45",
            status: "FAILED",
            records_received: 0,
            records_inserted: 0,
            records_updated: 0,
            records_skipped: 0,
            error_message: "Connection timed out",
          },
        })
      )
    );
    renderWithProviders(<Dashboard />);

    expect(await screen.findByText(/government synchronization failed/i)).toBeInTheDocument();
    expect(screen.getByText(/existing data is still available/i)).toBeInTheDocument();
  });

  it("shows the no-matches empty state (never implying no winners exist) when there are no wins", async () => {
    server.use(http.get("http://localhost:8000/api/wins", () => HttpResponse.json([])));
    renderWithProviders(<Dashboard />);

    expect(
      await screen.findByText(/no matching prize-pool result was found for your coupons yet/i)
    ).toBeInTheDocument();
  });

  it("shows a user-safe error state with retry when the wins request fails", async () => {
    server.use(http.get("http://localhost:8000/api/wins", () => HttpResponse.error()));
    renderWithProviders(<Dashboard />);

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });
});
