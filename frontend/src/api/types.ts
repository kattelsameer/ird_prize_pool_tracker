// Shared domain types mirroring the backend API contract.
// Keep this file the single source of truth for shapes coming over the wire; it is the
// "adapter boundary" on the frontend side so IRD/backend-specific quirks don't leak into
// every component (mirrors CLAUDE.md §67 on the backend).

export interface Profile {
  id: string;
  display_name: string;
  created_at: string;
  updated_at: string;
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

export type NotificationType =
  | "NEW_MATCH"
  | "CLAIM_EXPIRING"
  | "CLAIM_EXPIRED"
  | "NEW_SYNC_DATA"
  | "SYNC_FAILED";

export interface AppNotification {
  id: string;
  type: NotificationType;
  message: string;
  created_at: string;
  read_at: string | null;
}

export interface SyncRun {
  sync_started_at: string;
  sync_finished_at: string | null;
  status: "SUCCESS" | "FAILED" | "RUNNING";
  records_received: number;
  records_inserted: number;
  records_updated: number;
  records_skipped: number;
  error_message: string | null;
}

export interface SyncStatus {
  last_sync: SyncRun | null;
  is_running: boolean;
}

export interface Settings {
  networks: string[];
  notification_prefs: {
    new_match: boolean;
    claim_expiring: boolean;
    claim_expired: boolean;
    new_sync_data: boolean;
    sync_failed: boolean;
  };
}

