import { test, expect } from "@playwright/test";
import { installMockApi, E2E_TEST_PASSWORD } from "./mockApi";
import { fixtureUser } from "../src/test/fixtures";

test.describe("Consumer journey", () => {
  test.beforeEach(async ({ page }) => {
    await installMockApi(page);
  });

  test("open app, manage a coupon, sync, explore prize pool, see a winner, and read a notification", async ({
    page,
  }) => {
    // 1. Log in -> redirected to the dashboard.
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(fixtureUser.email);
    await page.getByLabel(/password/i).fill(E2E_TEST_PASSWORD);
    await page.getByRole("button", { name: /^log in$/i }).click();
    await expect(page.getByRole("heading", { name: /needs your attention/i })).toBeVisible();

    // 2. Add a coupon.
    await page.getByRole("link", { name: /my coupons/i }).click();
    await expect(page.getByRole("heading", { name: /my coupons/i })).toBeVisible();
    await page.getByRole("button", { name: /add coupon/i }).click();

    const dialog = page.getByRole("dialog", { name: /add a coupon/i });
    await expect(dialog).toBeVisible();
    await dialog.getByLabel(/coupon code/i).fill("555566667777");
    await dialog.getByLabel(/transaction date/i).fill("2026-08-10");
    await dialog.getByLabel(/fiscal year/i).selectOption("2083-84");
    await dialog.getByRole("button", { name: /save coupon/i }).click();

    // 3. Verify it appears in the list.
    await expect(dialog).toBeHidden();
    await expect(page.getByText("555566667777")).toBeVisible();

    // 4. Search/filter the coupon list.
    await page.getByLabel(/search by code/i).fill("555566667777");
    await expect(page.getByText("007315254493")).toBeHidden();
    await expect(page.getByText("555566667777")).toBeVisible();
    await page.getByLabel(/search by code/i).fill("");

    // 5. Trigger a (mocked) sync from the dashboard.
    await page.getByRole("link", { name: /dashboard/i }).click();
    await page.getByRole("button", { name: /sync now/i }).click();
    await expect(page.getByText(/last synced/i)).toBeVisible();

    // 6. View the prize pool explorer (all published draws, not just the user's own).
    await page.getByRole("link", { name: /prize pool explorer/i }).click();
    await expect(page.getByRole("heading", { name: /prize pool explorer/i })).toBeVisible();
    await expect(page.getByText("007315254493")).toBeVisible();

    // 7. Back on the dashboard, see a matched/winning coupon with all three data-source
    // labels and a claim deadline.
    await page.getByRole("link", { name: /dashboard/i }).click();
    const winnerCard = page.getByRole("article", { name: /coupon matches a published/i }).first();
    await expect(winnerCard).toBeVisible();
    await expect(winnerCard.getByText(/IRD published data/i)).toBeVisible();
    await expect(winnerCard.getByText(/Your entry/i)).toBeVisible();
    await expect(winnerCard.getByText(/App-calculated/i)).toBeVisible();
    await expect(winnerCard.getByText(/remaining to claim|claim window expired/i)).toBeVisible();

    // 8. Open notifications, see one, and mark it read.
    await page.getByRole("button", { name: /notifications/i }).click();
    const panel = page.getByRole("dialog", { name: /notifications/i });
    await expect(panel).toBeVisible();
    await expect(panel.getByText(/matches the bumper prize draw/i)).toBeVisible();
    await panel.getByRole("button", { name: /mark read/i }).first().click();
    await page.keyboard.press("Escape");

    // 9. Refresh the page and verify the added coupon persisted (mock backend keeps state
    // in-process for the life of the page's route handlers within this test).
    await page.getByRole("link", { name: /my coupons/i }).click();
    await page.reload();
    await expect(page.getByText("555566667777")).toBeVisible();
  });

  test("registers a new account, logs out, then logs back in", async ({ page }) => {
    // Register.
    await page.goto("/register");
    await page.getByLabel(/email/i).fill("new-e2e-user@example.com");
    await page.getByLabel(/password/i).fill("a-long-enough-password");
    await page.getByRole("button", { name: /create account/i }).click();
    await expect(page.getByRole("heading", { name: /needs your attention/i })).toBeVisible();

    // Log out -> redirected to login, protected routes no longer reachable.
    await page.getByRole("button", { name: /log out/i }).click();
    await expect(page).toHaveURL(/\/login$/);
    await page.goto("/coupons");
    await expect(page).toHaveURL(/\/login$/);

    // Log back in with the seeded fixture account.
    await page.getByLabel(/email/i).fill(fixtureUser.email);
    await page.getByLabel(/password/i).fill(E2E_TEST_PASSWORD);
    await page.getByRole("button", { name: /^log in$/i }).click();
    await expect(page.getByRole("heading", { name: /needs your attention/i })).toBeVisible();
  });
});
