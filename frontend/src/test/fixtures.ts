// Deterministic test fixtures. Never labeled or usable as real government data (§58).
import type { Paginated } from "../api/client";
import type {
  AppNotification,
  Coupon,
  DrawPeriodStatus,
  MatchResult,
  Network,
  PrizePool,
  Settings,
  SyncStatus,
} from "../api/types";

export const fixtureCoupons: Coupon[] = [
  {
    id: "coupon-1",
    coupon_id: "2083-84-007315254493",
    coupon_code: "007315254493",
    normalized_coupon_code: "007315254493",
    transaction_date: "2026-07-20",
    fiscal_year: "2083-84",
    network: "eSewa",
    created_at: "2026-07-20T10:00:00+05:45",
    updated_at: "2026-07-20T10:00:00+05:45",
  },
  {
    id: "coupon-2",
    coupon_id: "2083-84-000000000001",
    coupon_code: "000000000001",
    normalized_coupon_code: "000000000001",
    transaction_date: "2026-07-22",
    fiscal_year: "2083-84",
    network: "Khalti",
    created_at: "2026-07-22T09:00:00+05:45",
    updated_at: "2026-07-22T09:00:00+05:45",
  },
  {
    id: "coupon-3",
    coupon_id: "2082-83-999999999999",
    coupon_code: "999999999999",
    normalized_coupon_code: "999999999999",
    transaction_date: "2026-06-01",
    fiscal_year: "2082-83",
    network: null,
    created_at: "2026-06-01T09:00:00+05:45",
    updated_at: "2026-06-01T09:00:00+05:45",
  },
];

export const fixturePrizePools: PrizePool[] = [
  {
    id: "pp-1",
    source_record_id: "draw_bumper_1",
    draw_id: "draw_bumper_1",
    draw_title_en: "Bumper Winner Consumer Selection for the period of Shrawan 1 to 15",
    draw_title_np: null,
    category: "Bumper Prize",
    prize_amount: 1_000_000,
    prize_amount_net: 750_000,
    coupon_code: "007315254493",
    normalized_coupon_code: "007315254493",
    fiscal_year: "2083-84",
    network: null,
    eligible_from: "2026-07-17",
    eligible_to: "2026-07-31",
    published_at: "2026-08-07T09:27:46+05:45",
    claim_deadline: "2026-08-22T09:27:46+05:45",
    claim_open: true,
    claim_status: "CLAIM_ACTIVE",
    source: "prize.ird.gov.np",
    created_at: "2026-08-07T09:27:46+05:45",
    updated_at: "2026-08-07T09:27:46+05:45",
  },
  {
    id: "pp-2",
    source_record_id: "draw_daily_1",
    draw_id: "draw_daily_1",
    draw_title_en: "Daily Winner Consumer Selection for the period of Shrawan 16 to 31",
    draw_title_np: null,
    category: "Daily Prize",
    prize_amount: 133_334,
    prize_amount_net: 100_000,
    coupon_code: "000000000001",
    normalized_coupon_code: "000000000001",
    fiscal_year: "2083-84",
    network: null,
    eligible_from: "2026-08-01",
    eligible_to: "2026-08-15",
    published_at: "2026-08-14T09:00:00+05:45",
    claim_deadline: "2026-08-16T09:00:00+05:45",
    claim_open: true,
    claim_status: "CLAIM_EXPIRING",
    source: "prize.ird.gov.np",
    created_at: "2026-08-14T09:00:00+05:45",
    updated_at: "2026-08-14T09:00:00+05:45",
  },
  {
    id: "pp-3",
    source_record_id: "draw_daily_0",
    draw_id: "draw_daily_0",
    draw_title_en: "Daily Winner Consumer Selection for the period of Ashadh 16 to 31, 2082",
    draw_title_np: null,
    category: "Daily Prize",
    prize_amount: 133_334,
    prize_amount_net: 100_000,
    coupon_code: "111111111111",
    normalized_coupon_code: "111111111111",
    fiscal_year: "2082-83",
    network: null,
    eligible_from: "2026-06-16",
    eligible_to: "2026-06-30",
    published_at: "2026-07-01T09:00:00+05:45",
    claim_deadline: "2026-07-16T09:00:00+05:45",
    claim_open: false,
    claim_status: "CLAIM_EXPIRED",
    source: "prize.ird.gov.np",
    created_at: "2026-07-01T09:00:00+05:45",
    updated_at: "2026-07-01T09:00:00+05:45",
  },
];

// Mirrors the backend's flat MatchRead shape (app/schemas/match.py) exactly -- no nested
// coupon/winner sub-objects, matching what /api/matches, /api/wins, /api/claims actually return.
export const fixtureMatches: MatchResult[] = [
  {
    coupon_id: fixtureCoupons[0].id,
    coupon_code: fixtureCoupons[0].coupon_code,
    draw_id: fixturePrizePools[0].draw_id,
    prize_coupon_number: fixturePrizePools[0].coupon_code,
    winner_rank: 1,
    category_title_en: fixturePrizePools[0].category,
    draw_type: "GENERAL",
    draw_title_en: fixturePrizePools[0].draw_title_en,
    fiscal_year_unconfirmed: false,
    eligible_period_warning: false,
    claim_status: "CLAIM_ACTIVE",
    claim_deadline: fixturePrizePools[0].claim_deadline,
    claim_open: fixturePrizePools[0].claim_open,
    prize_amount: fixturePrizePools[0].prize_amount,
    prize_amount_net: fixturePrizePools[0].prize_amount_net,
    eligible_from: fixturePrizePools[0].eligible_from,
    eligible_to: fixturePrizePools[0].eligible_to,
    message:
      "Your coupon matches a result published by IRD for the \"Bumper Winner Consumer Selection for the period of Shrawan 1 to 15\" draw. To claim, you must provide the original physical bill and PAN in person at an Inland Revenue Office before the claim deadline.",
  },
  {
    coupon_id: fixtureCoupons[1].id,
    coupon_code: fixtureCoupons[1].coupon_code,
    draw_id: fixturePrizePools[1].draw_id,
    prize_coupon_number: fixturePrizePools[1].coupon_code,
    winner_rank: 1,
    category_title_en: fixturePrizePools[1].category,
    draw_type: "GENERAL",
    draw_title_en: fixturePrizePools[1].draw_title_en,
    fiscal_year_unconfirmed: false,
    eligible_period_warning: false,
    claim_status: "CLAIM_EXPIRING",
    claim_deadline: fixturePrizePools[1].claim_deadline,
    claim_open: fixturePrizePools[1].claim_open,
    prize_amount: fixturePrizePools[1].prize_amount,
    prize_amount_net: fixturePrizePools[1].prize_amount_net,
    eligible_from: fixturePrizePools[1].eligible_from,
    eligible_to: fixturePrizePools[1].eligible_to,
    message:
      "Your coupon matches a result published by IRD for the \"Daily Winner Consumer Selection for the period of Shrawan 16 to 31\" draw. To claim, you must provide the original physical bill and PAN in person at an Inland Revenue Office before the claim deadline.",
  },
];

// Mirrors the backend's flat DrawPeriodStatusRead shape (app/schemas/draw_period.py) exactly --
// what GET /api/matches/draw-periods returns. coupon-1/coupon-2 already have a match (see
// fixtureMatches above) so their period entries are DRAWN; coupon-3's transaction date
// (2026-06-01) predates every synced period's window, which is a sync gap (UNKNOWN), not "not
// drawn yet".
export const fixtureDrawPeriods: DrawPeriodStatus[] = [
  {
    coupon_id: fixtureCoupons[0].id,
    state: "DRAWN",
    eligible_from: fixturePrizePools[0].eligible_from,
    eligible_to: fixturePrizePools[0].eligible_to,
    draw_id: fixturePrizePools[0].draw_id,
    draw_title_en: fixturePrizePools[0].draw_title_en,
    published_at: fixturePrizePools[0].published_at,
    estimated_publish_date: null,
    is_estimated: false,
  },
  {
    coupon_id: fixtureCoupons[1].id,
    state: "DRAWN",
    eligible_from: fixturePrizePools[1].eligible_from,
    eligible_to: fixturePrizePools[1].eligible_to,
    draw_id: fixturePrizePools[1].draw_id,
    draw_title_en: fixturePrizePools[1].draw_title_en,
    published_at: fixturePrizePools[1].published_at,
    estimated_publish_date: null,
    is_estimated: false,
  },
  {
    coupon_id: fixtureCoupons[2].id,
    state: "UNKNOWN",
    eligible_from: null,
    eligible_to: null,
    draw_id: null,
    draw_title_en: null,
    published_at: null,
    estimated_publish_date: null,
    is_estimated: false,
  },
];

export const fixtureNotifications: AppNotification[] = [
  {
    id: "notif-1",
    type: "NEW_MATCH",
    coupon_id: fixtureCoupons[0].id,
    draw_id: fixturePrizePools[0].draw_id,
    message: "Your coupon 007315254493 matches the Bumper Prize draw published on Aug 7.",
    created_at: "2026-08-07T09:30:00+05:45",
    read_at: null,
  },
  {
    id: "notif-2",
    type: "CLAIM_EXPIRING",
    coupon_id: fixtureCoupons[1].id,
    draw_id: fixturePrizePools[1].draw_id,
    message: "Your claim for coupon 000000000001 expires in less than 2 days.",
    created_at: "2026-08-14T09:05:00+05:45",
    read_at: null,
  },
  {
    id: "notif-3",
    type: "NEW_SYNC_DATA",
    coupon_id: null,
    draw_id: null,
    message: "New prize-pool data has been synced.",
    created_at: "2026-08-01T00:05:00+05:45",
    read_at: "2026-08-01T08:00:00+05:45",
  },
];

export const fixtureNetworks: Network[] = [
  { id: "network-1", name: "eSewa", active: true },
  { id: "network-2", name: "Khalti", active: true },
  { id: "network-3", name: "IME Pay", active: true },
  { id: "network-4", name: "Bank Mobile App", active: true },
  { id: "network-5", name: "Cash (manual bill)", active: true },
];

export const fixtureSettings: Settings = {
  notify_new_match: true,
  notify_claim_expiring: true,
  notify_claim_expired: true,
  notify_sync_updates: false,
  notify_sync_failures: true,
  networks: fixtureNetworks,
};

export const fixtureSyncStatus: SyncStatus = {
  is_running: false,
  latest_run: {
    id: "sync-run-1",
    started_at: "2026-08-15T00:00:00+05:45",
    finished_at: "2026-08-15T00:00:12+05:45",
    status: "success",
    records_received: 16,
    records_inserted: 2,
    records_updated: 0,
    records_skipped: 0,
    error_message: null,
  },
};

export function paginated<T>(items: T[], limit = 20, offset = 0): Paginated<T> {
  return { items, total: items.length, limit, offset };
}

export const fixtureUser = {
  id: "user-1",
  email: "test-user@example.com",
  created_at: "2026-08-01T00:00:00+05:45",
};

export const fixtureAuthResponse = {
  access_token: "fixture-token",
  token_type: "bearer",
  user: fixtureUser,
};
