import styles from "./ClaimInstructions.module.css";

/**
 * The one canonical copy of "how to claim a prize" (§10a claim process), reused by
 * CouponDetail and the Information page instead of two independently hand-written
 * (and slowly drifting) copies of the same six steps.
 */
export function ClaimInstructions() {
  return (
    <ol className={styles.list}>
      <li>Visit an Inland Revenue Office in person — online claims are not accepted.</li>
      <li>Bring your original physical bill (photocopies are not accepted).</li>
      <li>Bring a government photo ID (citizenship, national ID, passport, or driving license).</li>
      <li>Bring your PAN (Personal Account Number) — mandatory.</li>
      <li>Bring your bank account details for the prize deposit.</li>
      <li>Claim within 15 calendar days of the announcement, or the prize is permanently forfeited.</li>
    </ol>
  );
}
