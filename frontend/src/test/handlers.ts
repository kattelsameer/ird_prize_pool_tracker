import { http, HttpResponse } from "msw";
import {
  fixtureCoupons,
  fixtureMatches,
  fixtureNetworks,
  fixtureNotifications,
  fixturePrizePools,
  fixtureSettings,
  fixtureSyncStatus,
  fixtureUser,
} from "./fixtures";
import type { Coupon, CouponInput, Network, User } from "../api/types";

const BASE = "http://localhost:8000";

export const TEST_USER_PASSWORD = "test-password-123";

// Mutable in-memory copies so create/update/delete tests can observe changes within a test file.
let coupons: Coupon[] = [...fixtureCoupons];
let notifications = [...fixtureNotifications];
let networks: Network[] = [...fixtureNetworks];
let settings = { ...fixtureSettings };

type RegisteredUser = { email: string; password: string; user: User };
let registeredUsers: RegisteredUser[] = [
  { email: fixtureUser.email, password: TEST_USER_PASSWORD, user: fixtureUser },
];
let issuedTokens: Record<string, User> = { "fixture-token": fixtureUser };

export function resetMockData() {
  coupons = [...fixtureCoupons];
  notifications = [...fixtureNotifications];
  networks = [...fixtureNetworks];
  settings = { ...fixtureSettings };
  registeredUsers = [{ email: fixtureUser.email, password: TEST_USER_PASSWORD, user: fixtureUser }];
  issuedTokens = { "fixture-token": fixtureUser };
}

export const handlers = [
  http.get(`${BASE}/api/coupons`, ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get("search")?.toLowerCase() ?? "";
    const fiscalYear = url.searchParams.get("fiscal_year") ?? "";
    const network = url.searchParams.get("network") ?? "";
    const limit = Number(url.searchParams.get("limit") ?? 20);
    const offset = Number(url.searchParams.get("offset") ?? 0);

    let filtered = coupons;
    if (search) filtered = filtered.filter((c) => c.coupon_code.toLowerCase().includes(search));
    if (fiscalYear) filtered = filtered.filter((c) => c.fiscal_year === fiscalYear);
    if (network) filtered = filtered.filter((c) => c.network === network);

    const total = filtered.length;
    const page = filtered.slice(offset, offset + limit);
    return HttpResponse.json({ items: page, total, limit, offset });
  }),

  http.post(`${BASE}/api/coupons`, async ({ request }) => {
    const body = (await request.json()) as CouponInput;
    const newCoupon: Coupon = {
      id: `coupon-${coupons.length + 1}`,
      coupon_id: `${body.fiscal_year ?? "unknown"}-${body.coupon_code.replace(/\s/g, "")}`,
      coupon_code: body.coupon_code,
      normalized_coupon_code: body.coupon_code.replace(/[\s-]/g, "").toUpperCase(),
      transaction_date: body.transaction_date,
      fiscal_year: body.fiscal_year,
      network: body.network,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    coupons = [newCoupon, ...coupons];
    return HttpResponse.json(newCoupon, { status: 201 });
  }),

  http.get(`${BASE}/api/coupons/:id`, ({ params }) => {
    const coupon = coupons.find((c) => c.id === params.id);
    if (!coupon) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(coupon);
  }),

  http.put(`${BASE}/api/coupons/:id`, async ({ params, request }) => {
    const body = (await request.json()) as CouponInput;
    const index = coupons.findIndex((c) => c.id === params.id);
    if (index === -1) return new HttpResponse(null, { status: 404 });
    coupons[index] = { ...coupons[index], ...body, updated_at: new Date().toISOString() };
    return HttpResponse.json(coupons[index]);
  }),

  http.delete(`${BASE}/api/coupons/:id`, ({ params }) => {
    coupons = coupons.filter((c) => c.id !== params.id);
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${BASE}/api/prize-pools`, ({ request }) => {
    const url = new URL(request.url);
    const fiscalYear = url.searchParams.get("fiscal_year") ?? "";
    const category = url.searchParams.get("category") ?? "";
    const claimStatus = url.searchParams.get("claim_status") ?? "";
    const couponCode = url.searchParams.get("coupon_code")?.toLowerCase() ?? "";
    const limit = Number(url.searchParams.get("limit") ?? 20);
    const offset = Number(url.searchParams.get("offset") ?? 0);

    let filtered = fixturePrizePools;
    if (fiscalYear) filtered = filtered.filter((p) => p.fiscal_year === fiscalYear);
    if (category) filtered = filtered.filter((p) => p.category === category);
    if (claimStatus) filtered = filtered.filter((p) => p.claim_status === claimStatus);
    if (couponCode) {
      filtered = filtered.filter((p) => p.normalized_coupon_code.toLowerCase().includes(couponCode));
    }

    const total = filtered.length;
    const page = filtered.slice(offset, offset + limit);
    return HttpResponse.json({ items: page, total, limit, offset });
  }),

  http.get(`${BASE}/api/prize-pools/:id`, ({ params }) => {
    const record = fixturePrizePools.find((p) => p.id === params.id);
    if (!record) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(record);
  }),

  http.get(`${BASE}/api/matches`, () => HttpResponse.json(fixtureMatches)),
  http.get(`${BASE}/api/wins`, () => HttpResponse.json(fixtureMatches)),
  http.get(`${BASE}/api/claims`, () => HttpResponse.json(fixtureMatches)),

  http.get(`${BASE}/api/notifications`, () =>
    HttpResponse.json({ items: notifications, total: notifications.length, limit: 50, offset: 0 })
  ),
  http.post(`${BASE}/api/notifications/:id/read`, ({ params }) => {
    notifications = notifications.map((n) =>
      n.id === params.id ? { ...n, read_at: new Date().toISOString() } : n
    );
    return new HttpResponse(null, { status: 204 });
  }),
  http.post(`${BASE}/api/notifications/read-all`, () => {
    notifications = notifications.map((n) => ({ ...n, read_at: n.read_at ?? new Date().toISOString() }));
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${BASE}/api/settings`, () => HttpResponse.json({ ...settings, networks })),
  http.put(`${BASE}/api/settings`, async ({ request }) => {
    const body = (await request.json()) as Partial<typeof settings>;
    settings = { ...settings, ...body };
    return HttpResponse.json({ ...settings, networks });
  }),
  http.post(`${BASE}/api/settings/networks`, async ({ request }) => {
    const body = (await request.json()) as { name: string };
    const created: Network = { id: `network-${networks.length + 1}`, name: body.name, active: true };
    networks = [...networks, created];
    return HttpResponse.json(created, { status: 201 });
  }),
  http.patch(`${BASE}/api/settings/networks/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Partial<Pick<Network, "name" | "active">>;
    const index = networks.findIndex((n) => n.id === params.id);
    if (index === -1) return new HttpResponse(null, { status: 404 });
    networks[index] = { ...networks[index], ...body };
    return HttpResponse.json(networks[index]);
  }),

  http.get(`${BASE}/api/sync/status`, () => HttpResponse.json(fixtureSyncStatus)),
  http.post(`${BASE}/api/sync`, () => HttpResponse.json(fixtureSyncStatus)),

  http.post(`${BASE}/api/auth/register`, async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };
    const email = body.email.trim().toLowerCase();
    if (registeredUsers.some((u) => u.email === email)) {
      return HttpResponse.json(
        { detail: "An account with this email already exists" },
        { status: 409 }
      );
    }
    const user: User = {
      id: `user-${registeredUsers.length + 1}`,
      email,
      created_at: new Date().toISOString(),
    };
    const token = `token-${user.id}`;
    registeredUsers = [...registeredUsers, { email, password: body.password, user }];
    issuedTokens = { ...issuedTokens, [token]: user };
    return HttpResponse.json({ access_token: token, token_type: "bearer", user }, { status: 201 });
  }),

  http.post(`${BASE}/api/auth/login`, async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };
    const email = body.email.trim().toLowerCase();
    const match = registeredUsers.find((u) => u.email === email && u.password === body.password);
    if (!match) {
      return HttpResponse.json({ detail: "Incorrect email or password" }, { status: 401 });
    }
    const token = `token-${match.user.id}`;
    issuedTokens = { ...issuedTokens, [token]: match.user };
    return HttpResponse.json({ access_token: token, token_type: "bearer", user: match.user });
  }),

  http.get(`${BASE}/api/auth/me`, ({ request }) => {
    const authHeader = request.headers.get("Authorization") ?? "";
    const token = authHeader.replace(/^Bearer\s+/i, "");
    const user = issuedTokens[token];
    if (!user) {
      return HttpResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }
    return HttpResponse.json(user);
  }),

  http.get(`${BASE}/api/profile`, () =>
    HttpResponse.json({
      id: "profile-1",
      display_name: "Nepal Consumer",
      created_at: "2026-08-01T00:00:00+05:45",
      updated_at: "2026-08-01T00:00:00+05:45",
    })
  ),
];
