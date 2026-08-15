import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Settings } from "./Settings";
import { renderWithProviders, createTestQueryClient } from "../test/testUtils";
import { getStoredToken, setStoredToken } from "../api/client";

function renderSettingsWithRouting() {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter initialEntries={["/settings"]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Settings page", () => {
  beforeEach(() => {
    // jsdom doesn't implement the Blob-download APIs the "download my data"
    // button uses; patch just those two methods (not the whole URL global,
    // which MSW/fetch also rely on) so the click handler runs without throwing.
    URL.createObjectURL = vi.fn(() => "blob:mock");
    URL.revokeObjectURL = vi.fn();
    HTMLAnchorElement.prototype.click = vi.fn();
  });


  it("loads existing networks and notification preferences", async () => {
    renderWithProviders(<Settings />);

    expect(await screen.findByDisplayValue("eSewa")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Khalti")).toBeInTheDocument();
    expect(screen.getByLabelText(/notify me about new matches/i)).toBeChecked();
    expect(screen.getByLabelText(/notify me when new government data is available/i)).not.toBeChecked();
  });

  it("adds a new network", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");

    await user.type(screen.getByLabelText(/new network name/i), "ConnectIPS");
    await user.click(screen.getByRole("button", { name: /^add$/i }));

    expect(await screen.findByDisplayValue("ConnectIPS")).toBeInTheDocument();
  });

  it("saves notification preference changes", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByLabelText(/notify me when new government data is available/i));
    await user.click(screen.getByRole("button", { name: /save settings/i }));

    await waitFor(() => {
      expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
    });
  });

  it("deactivates a network rather than deleting it", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByRole("button", { name: /deactivate esewa/i }));

    // Deactivating keeps the row (network history/coupons may still reference it) but
    // disables editing and flips the action to "Reactivate".
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /reactivate esewa/i })).toBeInTheDocument();
    });
    expect(screen.getByDisplayValue("eSewa")).toBeDisabled();
  });

  it("saves a display name via the Account section", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.type(screen.getByLabelText(/display name/i), "Ram Bahadur");
    await user.click(screen.getByRole("button", { name: /save name/i }));

    await waitFor(() => {
      expect(screen.getByText(/display name saved/i)).toBeInTheDocument();
    });
  });

  it("downloads a personal-data export bundle", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByRole("button", { name: /download my data/i }));

    await waitFor(() => {
      expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
    });
  });

  it("requires confirmation before deleting the account, then logs out on confirm", async () => {
    const user = userEvent.setup();
    setStoredToken("fixture-token");
    renderSettingsWithRouting();

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByRole("button", { name: /delete my account/i }));

    const dialog = await screen.findByRole("dialog", { name: /delete your account/i });
    await user.click(screen.getByRole("button", { name: /yes, delete my account/i }));

    await waitFor(() => {
      expect(screen.getByText(/login page/i)).toBeInTheDocument();
    });
    expect(getStoredToken()).toBeFalsy();
    expect(dialog).not.toBeInTheDocument();
  });

  it("cancels account deletion without deleting anything", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByRole("button", { name: /delete my account/i }));
    await screen.findByRole("dialog", { name: /delete your account/i });
    await user.click(screen.getByRole("button", { name: /^cancel$/i }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });
});
