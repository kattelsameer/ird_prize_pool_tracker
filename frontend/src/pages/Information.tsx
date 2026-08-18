import { DataSourceBadge } from "../components/DataSourceBadge";
import { ClaimInstructions } from "../components/ClaimInstructions";
import styles from "./Information.module.css";

export function Information() {
  return (
    <div className={styles.page}>
      <h1>About the Taxpayer Incentive Gift Program</h1>

      <div className={styles.disclosure} role="note">
        <strong>CouponSathi is an independent, unofficial consumer tool.</strong> It is not built,
        operated, or endorsed by the Nepal Inland Revenue Department (IRD) or the Government of
        Nepal. We read publicly published data from{" "}
        <a href="https://prize.ird.gov.np" target="_blank" rel="noreferrer">
          prize.ird.gov.np
        </a>{" "}
        and compare it against coupons you enter yourself. For official information, claims, or
        support, always use the official IRD website and offices.
      </div>

      <section className={styles.section}>
        <h2>What is the program?</h2>
        <p>
          The Taxpayer Incentive Gift Program (करदाता प्रोत्साहन उपहार कार्यक्रम) is run by the
          Inland Revenue Department under Nepal's Ministry of Finance. It rewards consumers for
          demanding formal bills/invoices, or transacting through supported digital payment
          methods, by entering their purchases into a coupon draw.{" "}
          <span className={styles.sourceNote}>(Described in official program materials — not
          confirmed live via the API.)</span>
        </p>
      </section>

      <section className={styles.section}>
        <h2>Draw schedule and prizes</h2>
        <p>
          Draws happen every <strong>1st and 16th of the Nepali calendar month</strong>. Each draw
          selects 15 daily-prize winners and 1 bumper-prize winner.{" "}
          <span className={styles.sourceNote}>(Program materials.)</span>
        </p>
        <table className={styles.table}>
          <caption className="visually-hidden">Prize tiers</caption>
          <thead>
            <tr>
              <th scope="col">Category</th>
              <th scope="col">Prize amount</th>
              <th scope="col">Net after 25% tax</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Daily Prize</td>
              <td>Rs 133,334</td>
              <td>Rs 100,000</td>
            </tr>
            <tr>
              <td>Bumper Prize</td>
              <td>Rs 1,000,000</td>
              <td>Rs 750,000</td>
            </tr>
          </tbody>
        </table>
        <p>
          Purchase amount does not affect your odds — a Rs 100 bill has the same winning chance as
          a Rs 50,000 bill. <span className={styles.sourceNote}>(Program materials.)</span>
        </p>
        <DataSourceBadge source="app">
          Your dashboard confirms live, from the IRD API, which of your specific coupons matched
          a published draw
        </DataSourceBadge>
      </section>

      <section className={styles.section}>
        <h2>Two ways a purchase becomes a coupon</h2>
        <p>
          <strong>1. Digital transactions (automatic).</strong> Paying via QR code, mobile wallet,
          or bank transfer through eSewa, Khalti, IME Pay, or a bank's mobile app automatically
          generates a coupon — no action needed from you.
        </p>
        <p>
          <strong>2. Cash purchases (manual entry).</strong> For a cash purchase of Rs 100 or more,
          keep your original paper bill and manually register it yourself at{" "}
          <a href="https://prize.ird.gov.np" target="_blank" rel="noreferrer">
            prize.ird.gov.np
          </a>
          . <span className={styles.sourceNote}>(Program materials.)</span>
        </p>
      </section>

      <section className={styles.section}>
        <h2>How to claim a prize</h2>
        <ClaimInstructions />
        <p>
          Miss the 15-day deadline and the prize is permanently forfeited to the Prime Minister's
          Disaster Relief Fund — it cannot be reclaimed.{" "}
          <span className={styles.sourceNote}>(Program materials.)</span>
        </p>
      </section>

      <section className={styles.section}>
        <h2>Your privacy</h2>
        <p>
          We only store the coupon details you choose to enter (code, transaction date, fiscal
          year, network) on this application. We never ask for or transmit your PAN or bank
          details — those are only ever needed in person, at claim time, directly with IRD. You
          can edit or delete any coupon you've entered at any time from My Coupons.
        </p>
      </section>
    </div>
  );
}
