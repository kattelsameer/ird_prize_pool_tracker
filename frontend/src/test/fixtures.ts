// Deterministic test fixtures. Never labeled or usable as real government data (§58).
import type {
  AppNotification,
  Coupon,
  MatchResult,
  Paginated,
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

export const fixtureMatches: MatchResult[] = [
  {
    coupon: fixtureCoupons[0],
    winner: fixturePrizePools[0],
    claim_status: "CLAIM_ACTIVE",
    fiscal_year_unconfirmed: false,
  },
  {
    coupon: fixtureCoupons[1],
    winner: fixturePrizePools[1],
    claim_status: "CLAIM_EXPIRING",
    fiscal_year_unconfirmed: false,
  },
];

export const fixtureNotifications: AppNotification[] = [
  {
    id: "notif-1",
    type: "NEW_MATCH",
    message: "Your coupon 007315254493 matches the Bumper Prize draw published on Aug 7.",
    created_at: "2026-08-07T09:30:00+05:45",
    read_at: null,
  },
  {
    id: "notif-2",
    type: "CLAIM_EXPIRING",
    message: "Your claim for coupon 000000000001 expires in less than 2 days.",
    created_at: "2026-08-14T09:05:00+05:45",
    read_at: null,
  },
  {
    id: "notif-3",
    type: "NEW_SYNC_DATA",
    message: "New prize-pool data has been synced.",
    created_at: "2026-08-01T00:05:00+05:45",
    read_at: "2026-08-01T08:00:00+05:45",
  },
];

export const fixtureSettings: Settings = {
  networks: ["eSewa", "Khalti", "IME Pay", "Bank Mobile App", "Cash (manual bill)"],
  notification_prefs: {
    new_match: true,
    claim_expiring: true,
    claim_expired: true,
    new_sync_data: false,
    sync_failed: true,
  },
};

export const fixtureSyncStatus: SyncStatus = {
  is_running: false,
  last_sync: {
    sync_started_at: "2026-08-15T00:00:00+05:45",
    sync_finished_at: "2026-08-15T00:00:12+05:45",
    status: "SUCCESS",
    records_received: 16,
    records_inserted: 2,
    records_updated: 0,
    records_skipped: 0,
    error_message: null,
  },
};

export function paginated<T>(items: T[], page = 1, page_size = 20): Paginated<T> {
  return { items, total: items.length, page, page_size };
}
