import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Settings } from "./Settings";
import { renderWithProviders } from "../test/testUtils";

describe("Settings page", () => {
  it("loads existing networks and notification preferences", async () => {
    renderWithProviders(<Settings />);

    expect(await screen.findByDisplayValue("eSewa")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Khalti")).toBeInTheDocument();
    expect(screen.getByLabelText(/notify me about new matches/i)).toBeChecked();
    expect(screen.getByLabelText(/notify me when new government data is available/i)).not.toBeChecked();
  });

  it("adds a new network and saves settings", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");

    await user.type(screen.getByLabelText(/new network name/i), "ConnectIPS");
    await user.click(screen.getByRole("button", { name: /^add$/i }));

    expect(await screen.findByDisplayValue("ConnectIPS")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /save settings/i }));

    await waitFor(() => {
      expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
    });
  });

  it("removes a network", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Settings />);

    await screen.findByDisplayValue("eSewa");
    await user.click(screen.getByRole("button", { name: /remove esewa/i }));

    expect(screen.queryByDisplayValue("eSewa")).not.toBeInTheDocument();
  });
});
