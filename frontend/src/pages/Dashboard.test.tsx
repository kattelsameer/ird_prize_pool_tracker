import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

  it("shows the last sync's record counts alongside its status", async () => {
    renderWithProviders(<Dashboard />);
    expect(await screen.findByText(/16 received, 2 new, 0 updated/i)).toBeInTheDocument();
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
          latest_run: {
            id: "sync-run-failed",
            started_at: "2026-08-15T00:00:00+05:45",
            finished_at: "2026-08-15T00:00:05+05:45",
            status: "failed",
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

  it("shows Syncing... immediately after clicking Sync now, not only while the click itself is pending", async () => {
    // Regression test: POST /api/sync returns a SyncTriggerResponse
    // ({accepted, message}), not a SyncStatus. useTriggerSync used to write
    // that response straight into the sync-status cache, corrupting
    // is_running until the next 30s poll -- so "Sync now" appeared to do
    // nothing for a while after every click, which is exactly the reported
    // bug. The fix invalidates the status query on trigger success instead,
    // so the UI reflects the real (still-running) status right away.
    let syncRunning = false;
    server.use(
      http.get("http://localhost:8000/api/sync/status", () =>
        HttpResponse.json({ is_running: syncRunning, latest_run: null })
      ),
      http.post("http://localhost:8000/api/sync", () => {
        syncRunning = true;
        return HttpResponse.json({ accepted: true, message: "Synchronization started." });
      })
    );
    const user = userEvent.setup();
    renderWithProviders(<Dashboard />);

    const syncButton = await screen.findByRole("button", { name: /sync now/i });
    await user.click(syncButton);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /syncing/i })).toBeDisabled();
    });
  });

  it("surfaces the server's message instead of silently no-op'ing when a sync is already in progress elsewhere", async () => {
    // The locally cached status hasn't caught up yet (e.g. a sync was
    // started from another tab/the daily cron a moment ago), so the button
    // is still enabled here -- but the server itself rejects the trigger.
    // Previously this response was silently discarded.
    server.use(
      http.get("http://localhost:8000/api/sync/status", () =>
        HttpResponse.json({ is_running: false, latest_run: null })
      ),
      http.post("http://localhost:8000/api/sync", () =>
        HttpResponse.json({ accepted: false, message: "A synchronization is already in progress." })
      )
    );
    const user = userEvent.setup();
    renderWithProviders(<Dashboard />);

    const syncButton = await screen.findByRole("button", { name: /sync now/i });
    await user.click(syncButton);

    expect(await screen.findByText(/a synchronization is already in progress/i)).toBeInTheDocument();
  });
});
