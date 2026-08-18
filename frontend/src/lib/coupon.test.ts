import { describe, expect, it } from "vitest";
import { deriveCouponId, isValidCouponCode, normalizeCouponCode } from "./coupon";

describe("normalizeCouponCode", () => {
  it("strips whitespace and hyphens and upper-cases", () => {
    expect(normalizeCouponCode("007 315 254 493")).toBe("007315254493");
    expect(normalizeCouponCode("abc-123")).toBe("ABC123");
  });
});

describe("deriveCouponId", () => {
  it("prefixes the normalized code with the fiscal year", () => {
    expect(deriveCouponId("2083-84", "007 315 254 493")).toBe("2083-84-007315254493");
  });

  it("falls back to just the normalized code when fiscal year is missing", () => {
    expect(deriveCouponId(null, "abc 123")).toBe("ABC123");
  });
});

describe("isValidCouponCode", () => {
  it("accepts a plausible alphanumeric code", () => {
    expect(isValidCouponCode("007315254493")).toBe(true);
  });

  it("rejects an empty or too-short code", () => {
    expect(isValidCouponCode("")).toBe(false);
    expect(isValidCouponCode("AB1")).toBe(false);
  });
});
