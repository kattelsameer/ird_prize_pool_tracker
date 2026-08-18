// Shared domain types mirroring the backend API contract.
// Keep this file the single source of truth for shapes coming over the wire; it is the
// "adapter boundary" on the frontend side so IRD/backend-specific quirks don't leak into
// every component (mirrors CLAUDE.md §67 on the backend).

export interface Profile {
  id: string;
  display_name: string | null;
  created_at: string;
  updated_at: string;
}

// Personal-data export bundle (CLAUDE.md §10d). Notifications and government
// prize-pool records are deliberately excluded -- see app/schemas/account.py.
export interface AccountExport {
  exported_at: string;
  account_email: string;
  profile: Profile;
  coupons: Coupon[];
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Coupon {
  id: string;
  coupon_id: string; // <fiscal-year>-<coupon-code>
  coupon_code: string;
  normalized_coupon_code: string;
  transaction_date: string; // ISO date, Gregorian, as entered
  fiscal_year: string | null; // BS fiscal year, e.g. "2083-84"; may be unset
  network: string | null;
  created_at: string;
  updated_at: string;
}

export type CouponInput = {
  coupon_code: string;
  transaction_date: string;
  fiscal_year: string | null;
  network: string | null;
};

export interface PrizePool {
  id: string;
  source_record_id: string;
  draw_id: string;
  draw_title_en: string | null;
  draw_title_np: string | null;
  category: string | null; // e.g. "Daily Prize" | "Bumper Prize"
  prize_amount: number | null;
  prize_amount_net: number | null;
  coupon_code: string;
  normalized_coupon_code: string;
  fiscal_year: string;
  network: string | null; // IRD's public API does not publish network/provider per winner record
  eligible_from: string | null;
  eligible_to: string | null;
  published_at: string;
  claim_deadline: string;
  claim_open: boolean;
  claim_status: ClaimStatus;
  source: string;
  created_at: string;
  updated_at: string;
}

export type ClaimStatus = "CLAIM_ACTIVE" | "CLAIM_EXPIRING" | "CLAIM_EXPIRED";

// Mirrors the backend's flat MatchRead schema exactly (app/schemas/match.py) --
// application-derived information (CLAUDE.md §6), not a join of full Coupon/PrizePool
// records. `coupon_id` is the Coupon's id (primary key), not its human-readable coupon_id
// field (fiscal-year-prefixed code).
export interface MatchResult {
  coupon_id: string;
  coupon_code: string;
  draw_id: string;
  prize_coupon_number: string;
  winner_rank: number;
  category_title_en: string | null;
  draw_type: string | null;
  draw_title_en: string | null;
  fiscal_year_unconfirmed: boolean;
  eligible_period_warning: boolean;
  claim_status: ClaimStatus;
  claim_deadline: string;
  claim_open: boolean;
  message: string;
}

// Mirrors the backend's DrawPeriodStatusRead schema exactly
// (app/schemas/draw_period.py) -- application-derived information (CLAUDE.md
// §6), independent of whether the coupon actually matched a winner. See
// GET /api/matches/draw-periods.
export type DrawPeriodState = "DRAWN" | "PENDING" | "UNKNOWN";

export interface DrawPeriodStatus {
  coupon_id: string;
  state: DrawPeriodState;
  eligible_from: string | null;
  eligible_to: string | null;
  draw_id: string | null;
  draw_title_en: string | null;
  published_at: string | null;
  estimated_publish_date: string | null;
  is_estimated: boolean;
}

export type NotificationType =
  | "NEW_MATCH"
  | "CLAIM_EXPIRING"
  | "CLAIM_EXPIRED"
  | "NEW_SYNC_DATA"
  | "SYNC_FAILED";

export interface AppNotification {
  id: string;
  type: NotificationType;
  coupon_id: string | null;
  draw_id: string | null;
  message: string;
  created_at: string;
  read_at: string | null;
}

// Mirrors app/schemas/sync.py exactly -- status is lowercase (set verbatim by
// app/services/sync_service.py: "running" | "success" | "partial" | "failed").
export type SyncRunStatus = "running" | "success" | "partial" | "failed";

export interface SyncRun {
  id: string;
  started_at: string;
  finished_at: string | null;
  status: SyncRunStatus;
  records_received: number;
  records_inserted: number;
  records_updated: number;
  records_skipped: number;
  error_message: string | null;
}

export interface SyncStatus {
  is_running: boolean;
  latest_run: SyncRun | null;
}

// Mirrors app/schemas/sync.py's SyncTriggerResponse -- the immediate response to
// POST /api/sync, distinct from SyncStatus. The actual sync runs in a background
// thread, so `accepted` only says whether this call started (or found) a run --
// it says nothing about whether that run has finished yet.
export interface SyncTriggerResponse {
  accepted: boolean;
  message: string;
}

export interface Network {
  id: string;
  name: string;
  active: boolean;
}

// Mirrors app/schemas/settings.py's SettingsRead exactly -- notification prefs are flat
// top-level fields (not a nested `notification_prefs` object), and `networks` is not
// editable through PUT /api/settings; add/rename/deactivate go through their own
// /api/settings/networks endpoints (see api/settings.ts).
export interface Settings {
  notify_new_match: boolean;
  notify_claim_expiring: boolean;
  notify_claim_expired: boolean;
  notify_sync_updates: boolean;
  notify_sync_failures: boolean;
  networks: Network[];
}

export type SettingsUpdate = Partial<
  Omit<Settings, "networks">
>;

