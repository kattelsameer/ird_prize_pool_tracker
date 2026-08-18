/**
 * Bikram Sambat fiscal year helpers for the frontend dropdown.
 *
 * The backend is authoritative for which fiscal years actually have data (via
 * /api/prize-pools and /api/settings), but the coupon form needs a reasonable static list of
 * selectable BS fiscal years (format YYYY-YY, e.g. "2083-84") so a user can log a coupon even
 * before the corresponding prize-pool data has synced. Nepal FY runs Shrawan 1 -> Ashadh 31
 * (mid-July to mid-July); see CLAUDE.md §10b.
 */

export const CURRENT_FISCAL_YEAR = "2083-84";

/** Generate a small window of BS fiscal-year labels around the current one, most recent first. */
export function generateFiscalYearOptions(centerYear = 2083, span = 3): string[] {
  const years: string[] = [];
  for (let offset = 1; offset >= -span; offset--) {
    const start = centerYear + offset;
    const endShort = String((start + 1) % 100).padStart(2, "0");
    years.push(`${start}-${endShort}`);
  }
  return years;
}

export const DEFAULT_NETWORKS = ["eSewa", "Khalti", "IME Pay", "Bank Mobile App", "Cash (manual bill)"];
