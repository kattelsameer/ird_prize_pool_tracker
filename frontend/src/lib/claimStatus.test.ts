import { describe, expect, it } from "vitest";
import { computeClaimCountdown, claimStatusPresentation, EXPIRING_THRESHOLD_MS } from "./claimStatus";

describe("computeClaimCountdown", () => {
  const now = new Date("2026-08-15T00:00:00+05:45");

  it("reports an active claim with days remaining when far from the deadline", () => {
    const deadline = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000).toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpired).toBe(false);
    expect(result.isExpiring).toBe(false);
    expect(result.days).toBe(5);
    expect(result.label).toContain("5 days remaining");
  });

  it("flags expiring exactly at the 2-day threshold boundary (just under)", () => {
    const deadline = new Date(now.getTime() + EXPIRING_THRESHOLD_MS - 1000).toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpired).toBe(false);
    expect(result.isExpiring).toBe(true);
  });

  it("does not flag expiring exactly at the 2-day threshold boundary (exactly at)", () => {
    const deadline = new Date(now.getTime() + EXPIRING_THRESHOLD_MS).toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpiring).toBe(false);
  });

  it("reports expired when the deadline is in the past", () => {
    const deadline = new Date(now.getTime() - 60 * 1000).toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpired).toBe(true);
    expect(result.label).toBe("Claim window expired");
  });

  it("reports expired at exactly the deadline instant (boundary)", () => {
    const deadline = now.toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpired).toBe(true);
  });

  it("falls back to a minutes label when less than an hour remains", () => {
    const deadline = new Date(now.getTime() + 30 * 60 * 1000).toISOString();
    const result = computeClaimCountdown(deadline, now);
    expect(result.isExpiring).toBe(true);
    expect(result.label).toContain("minute");
  });
});

describe("claimStatusPresentation", () => {
  it("maps CLAIM_ACTIVE to an active tone with a distinct icon and label", () => {
    const presentation = claimStatusPresentation("CLAIM_ACTIVE");
    expect(presentation.tone).toBe("active");
    expect(presentation.icon).not.toBe("");
    expect(presentation.label.toLowerCase()).toContain("active");
  });

  it("maps CLAIM_EXPIRING to a warning tone", () => {
    expect(claimStatusPresentation("CLAIM_EXPIRING").tone).toBe("expiring");
  });

  it("maps CLAIM_EXPIRED to an expired tone", () => {
    expect(claimStatusPresentation("CLAIM_EXPIRED").tone).toBe("expired");
  });
});
