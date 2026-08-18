/**
 * Coupon code normalization and coupon_id derivation, mirroring the backend's normalization
 * rules (CLAUDE.md §25/§28) so the UI can show a live preview before submitting the form.
 * The backend remains authoritative for the persisted normalized value.
 */

export function normalizeCouponCode(raw: string): string {
  return raw.replace(/[\s-]+/g, "").toUpperCase();
}

export function deriveCouponId(fiscalYear: string | null | undefined, couponCode: string): string {
  const normalized = normalizeCouponCode(couponCode);
  if (!fiscalYear) return normalized;
  return `${fiscalYear}-${normalized}`;
}

const COUPON_CODE_PATTERN = /^[A-Z0-9]{6,20}$/;

export function isValidCouponCode(raw: string): boolean {
  return COUPON_CODE_PATTERN.test(normalizeCouponCode(raw));
}
