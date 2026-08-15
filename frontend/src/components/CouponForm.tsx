import { useId, useState, type FormEvent } from "react";
import { deriveCouponId, isValidCouponCode, normalizeCouponCode } from "../lib/coupon";
import { generateFiscalYearOptions, DEFAULT_NETWORKS } from "../lib/fiscalYears";
import type { CouponInput } from "../api/types";
import styles from "./CouponForm.module.css";

export interface CouponFormProps {
  initialValue?: Partial<CouponInput>;
  networks?: string[];
  submitLabel?: string;
  onSubmit: (input: CouponInput) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
  submitError?: string | null;
}

const FISCAL_YEAR_OPTIONS = generateFiscalYearOptions();

export function CouponForm({
  initialValue,
  networks = DEFAULT_NETWORKS,
  submitLabel = "Save coupon",
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitError = null,
}: CouponFormProps) {
  const [couponCode, setCouponCode] = useState(initialValue?.coupon_code ?? "");
  const [transactionDate, setTransactionDate] = useState(initialValue?.transaction_date ?? "");
  const [fiscalYear, setFiscalYear] = useState(initialValue?.fiscal_year ?? "");
  const [network, setNetwork] = useState(initialValue?.network ?? "");
  const [touched, setTouched] = useState(false);

  const formId = useId();

  const couponCodeError =
    touched && couponCode.trim() !== "" && !isValidCouponCode(couponCode)
      ? "Enter the 12-digit (or similar) coupon code exactly as printed on your bill or SMS receipt."
      : touched && couponCode.trim() === ""
      ? "Coupon code is required."
      : null;

  const dateError = touched && !transactionDate ? "Transaction date is required." : null;

  const isValid = !couponCodeError && !dateError && couponCode.trim() !== "" && Boolean(transactionDate);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setTouched(true);
    if (!isValid) return;
    onSubmit({
      coupon_code: couponCode.trim(),
      transaction_date: transactionDate,
      fiscal_year: fiscalYear || null,
      network: network || null,
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {submitError && (
        <p className={styles.formError} role="alert">
          {submitError}
        </p>
      )}

      <div className={styles.field}>
        <label htmlFor={`${formId}-code`}>Coupon code</label>
        <input
          id={`${formId}-code`}
          name="coupon_code"
          type="text"
          value={couponCode}
          onChange={(e) => setCouponCode(e.target.value)}
          placeholder="e.g. 007 315 254 493"
          aria-invalid={Boolean(couponCodeError)}
          aria-describedby={couponCodeError ? `${formId}-code-error` : `${formId}-code-hint`}
        />
        <p id={`${formId}-code-hint`} className={styles.hint}>
          {couponCode.trim()
            ? `Will be stored as: ${deriveCouponId(fiscalYear || null, couponCode)}`
            : "Copy the code exactly as it appears; spaces are fine, we'll normalize it."}
        </p>
        {couponCodeError && (
          <p id={`${formId}-code-error`} className={styles.error}>
            {couponCodeError}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor={`${formId}-date`}>Transaction date</label>
        <input
          id={`${formId}-date`}
          name="transaction_date"
          type="date"
          value={transactionDate}
          onChange={(e) => setTransactionDate(e.target.value)}
          aria-invalid={Boolean(dateError)}
          aria-describedby={dateError ? `${formId}-date-error` : undefined}
        />
        {dateError && (
          <p id={`${formId}-date-error`} className={styles.error}>
            {dateError}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor={`${formId}-fy`}>Fiscal year (optional but recommended)</label>
        <select id={`${formId}-fy`} name="fiscal_year" value={fiscalYear} onChange={(e) => setFiscalYear(e.target.value)}>
          <option value="">Not sure / unspecified</option>
          {FISCAL_YEAR_OPTIONS.map((fy) => (
            <option key={fy} value={fy}>
              FY {fy}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.field}>
        <label htmlFor={`${formId}-network`}>Network / payment method (optional)</label>
        <select id={`${formId}-network`} name="network" value={network} onChange={(e) => setNetwork(e.target.value)}>
          <option value="">Unspecified</option>
          {networks.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.actions}>
        <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
          {isSubmitting ? "Saving…" : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className={styles.cancelButton} onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export function previewNormalizedCode(code: string): string {
  return normalizeCouponCode(code);
}
