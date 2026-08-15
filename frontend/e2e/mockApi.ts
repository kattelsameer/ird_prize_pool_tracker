import type { Page } from "@playwright/test";
import {
  fixtureCoupons,
  fixtureMatches,
  fixtureNotifications,
  fixturePrizePools,
  fixtureSettings,
  fixtureSyncStatus,
  fixtureUser,
} from "../src/test/fixtures";
import type { Coupon, CouponInput } from "../src/api/types";

export const E2E_TEST_PASSWORD = "test-password-123";

/**
 * Deterministic in-process mock backend for E2E, wired via Playwright route interception.
 * Never hits the live IRD service or requires the real Python backend (§54).
 */
export async function installMockApi(page: Page) {
  let coupons: Coupon[] = [...fixtureCoupons];
  let notifications = [...fixtureNotifications];

  const token = "e2e-fixture-token";

  await page.route("**/api/auth/register", async (route) => {
    await route.fulfill({ status: 201, json: { access_token: token, token_type: "bearer", user: fixtureUser } });
  });
  await page.route("**/api/auth/login", async (route) => {
    const body = route.request().postDataJSON() as { email: string; password: string };
    if (body.email === fixtureUser.email && body.password === E2E_TEST_PASSWORD) {
      await route.fulfill({ json: { access_token: token, token_type: "bearer", user: fixtureUser } });
      return;
    }
    await route.fulfill({ status: 401, json: { detail: "Incorrect email or password" } });
  });
  await page.route("**/api/auth/me", async (route) => {
    const auth = route.request().headers()["authorization"] ?? "";
    if (auth === `Bearer ${token}`) {
      await route.fulfill({ json: fixtureUser });
      return;
    }
    await route.fulfill({ status: 401, json: { detail: "Not authenticated" } });
  });

  await page.route("**/api/coupons**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());

    if (request.method() === "GET") {
      const search = url.searchParams.get("search")?.toLowerCase() ?? "";
      const filtered = search
        ? coupons.filter((c) => c.coupon_code.toLowerCase().includes(search))
        : coupons;
      const limit = Number(url.searchParams.get("limit") ?? 20);
      const offset = Number(url.searchParams.get("offset") ?? 0);
      await route.fulfill({
        json: {
          items: filtered.slice(offset, offset + limit),
          total: filtered.length,
          limit,
          offset,
        },
      });
      return;
    }

    if (request.method() === "POST") {
      const body = request.postDataJSON() as CouponInput;
      const created: Coupon = {
        id: `coupon-e2e-${coupons.length + 1}`,
        coupon_id: `${body.fiscal_year ?? "unknown"}-${body.coupon_code.replace(/\s/g, "")}`,
        coupon_code: body.coupon_code,
        normalized_coupon_code: body.coupon_code.replace(/[\s-]/g, "").toUpperCase(),
        transaction_date: body.transaction_date,
        fiscal_year: body.fiscal_year,
        network: body.network,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      coupons = [created, ...coupons];
      await route.fulfill({ status: 201, json: created });
      return;
    }

    await route.continue();
  });

  await page.route("**/api/coupons/*", async (route) => {
    const request = route.request();
    const id = new URL(request.url()).pathname.split("/").pop();

    if (request.method() === "GET") {
      const coupon = coupons.find((c) => c.id === id);
      if (!coupon) {
        await route.fulfill({ status: 404 });
        return;
      }
      await route.fulfill({ json: coupon });
      return;
    }

    if (request.method() === "DELETE") {
      coupons = coupons.filter((c) => c.id !== id);
      await route.fulfill({ status: 204 });
      return;
    }

    await route.continue();
  });

  await page.route("**/api/prize-pools**", async (route) => {
    await route.fulfill({
      json: { items: fixturePrizePools, total: fixturePrizePools.length, limit: 20, offset: 0 },
    });
  });

  await page.route("**/api/matches", async (route) => {
    await route.fulfill({ json: fixtureMatches });
  });
  await page.route("**/api/wins", async (route) => {
    await route.fulfill({ json: fixtureMatches });
  });
  await page.route("**/api/claims", async (route) => {
    await route.fulfill({ json: fixtureMatches });
  });

  await page.route("**/api/notifications**", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        json: { items: notifications, total: notifications.length, limit: 50, offset: 0 },
      });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/notifications/*/read", async (route) => {
    const id = new URL(route.request().url()).pathname.split("/")[3];
    notifications = notifications.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n));
    await route.fulfill({ status: 204 });
  });
  await page.route("**/api/notifications/read-all", async (route) => {
    notifications = notifications.map((n) => ({ ...n, read_at: n.read_at ?? new Date().toISOString() }));
    await route.fulfill({ status: 204 });
  });

  let settings = { ...fixtureSettings };
  let networks = [...fixtureSettings.networks];

  await page.route("**/api/settings", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ json: { ...settings, networks } });
      return;
    }
    settings = { ...settings, ...route.request().postDataJSON() };
    await route.fulfill({ json: { ...settings, networks } });
  });

  await page.route("**/api/settings/networks", async (route) => {
    const body = route.request().postDataJSON() as { name: string };
    const created = { id: `network-e2e-${networks.length + 1}`, name: body.name, active: true };
    networks = [...networks, created];
    await route.fulfill({ status: 201, json: created });
  });

  await page.route("**/api/settings/networks/*", async (route) => {
    const id = new URL(route.request().url()).pathname.split("/").pop();
    const body = route.request().postDataJSON() as { name?: string; active?: boolean };
    const index = networks.findIndex((n) => n.id === id);
    if (index === -1) {
      await route.fulfill({ status: 404 });
      return;
    }
    networks[index] = { ...networks[index], ...body };
    await route.fulfill({ json: networks[index] });
  });

  let syncTriggered = false;
  await page.route("**/api/sync/status", async (route) => {
    await route.fulfill({ json: syncTriggered ? fixtureSyncStatus : fixtureSyncStatus });
  });
  await page.route("**/api/sync", async (route) => {
    if (route.request().method() === "POST") {
      syncTriggered = true;
      await route.fulfill({ json: fixtureSyncStatus });
      return;
    }
    await route.continue();
  });

  await page.route("**/api/profile", async (route) => {
    await route.fulfill({
      json: {
        id: "profile-1",
        display_name: "Nepal Consumer",
        created_at: "2026-08-01T00:00:00+05:45",
        updated_at: "2026-08-01T00:00:00+05:45",
      },
    });
  });
}
