import { describe, expect, it } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NotificationBell } from "./NotificationBell";
import { renderWithProviders } from "../test/testUtils";

describe("NotificationBell", () => {
  it("shows an unread count badge and opens a panel listing notifications", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    // Two unread fixtures (NEW_MATCH, CLAIM_EXPIRING).
    await waitFor(() => {
      expect(screen.getByLabelText(/notifications, 2 unread/i)).toBeInTheDocument();
    });

    await user.click(screen.getByLabelText(/notifications, 2 unread/i));

    const panel = await screen.findByRole("dialog", { name: /notifications/i });
    expect(panel).toHaveTextContent(/matches the bumper prize draw/i);
    expect(panel).toHaveTextContent(/expires in less than 2 days/i);
  });

  it("marks a single notification as read", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    await user.click(await screen.findByLabelText(/notifications, 2 unread/i));
    const readButtons = await screen.findAllByRole("button", { name: /mark read/i });
    await user.click(readButtons[0]);

    await waitFor(() => {
      expect(screen.getByLabelText(/notifications, 1 unread/i)).toBeInTheDocument();
    });
  });

  it("marks all notifications as read", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    await user.click(await screen.findByLabelText(/notifications, 2 unread/i));
    await user.click(screen.getByRole("button", { name: /mark all read/i }));

    await waitFor(() => {
      expect(screen.getByLabelText(/^notifications$/i)).toBeInTheDocument();
    });
  });
});
