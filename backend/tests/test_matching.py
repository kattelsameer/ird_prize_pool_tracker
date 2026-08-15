import unittest

from app.domain.matching import CouponInput, WinnerInput, match_coupons
from tests.data_matching import (
    COUPONS,
    DEFAULT_WINNER_KWARGS,
    DUPLICATE_GOVERNMENT_RECORD_SCENARIO,
    DUPLICATE_USER_COUPON_SCENARIO,
    NOW,
    SCENARIOS,
    WINNERS,
)


def _build_coupon(key: str) -> CouponInput:
    coupon_id, code, fy, txn_date = COUPONS[key]
    return CouponInput(
        coupon_id=coupon_id, coupon_code=code, fiscal_year=fy, transaction_date=txn_date
    )


def _build_winner(key: str) -> WinnerInput:
    kwargs = {**DEFAULT_WINNER_KWARGS, **WINNERS[key]}
    return WinnerInput(**kwargs)


class MatchCouponsScenarioTests(unittest.TestCase):
    def test_scenarios(self):
        for scenario in SCENARIOS:
            with self.subTest(name=scenario["name"]):
                coupon = _build_coupon(scenario["coupon_key"])
                winners = [_build_winner(k) for k in scenario["winner_keys"]]
                results = match_coupons([coupon], winners, now=NOW)
                self.assertEqual(len(results), scenario["expect_match_count"])
                if scenario["expect_match_count"] == 1:
                    result = results[0]
                    for field, expected_value in scenario["checks"].items():
                        actual = getattr(result, field)
                        if field == "claim_status":
                            actual = actual.value
                        self.assertEqual(
                            actual, expected_value, f"field={field}"
                        )

    def test_duplicate_user_coupon_entries_each_produce_independent_matches(self):
        scenario = DUPLICATE_USER_COUPON_SCENARIO
        coupons = [_build_coupon(k) for k in scenario["coupon_keys"]]
        winners = [_build_winner(k) for k in scenario["winner_keys"]]
        results = match_coupons(coupons, winners, now=NOW)
        self.assertEqual(len(results), scenario["expected_total_matches"])
        coupon_ids = {r.coupon_id for r in results}
        self.assertEqual(coupon_ids, {c.coupon_id for c in coupons})

    def test_duplicate_government_record_surfaces_both_defensively(self):
        scenario = DUPLICATE_GOVERNMENT_RECORD_SCENARIO
        coupon = _build_coupon(scenario["coupon_key"])
        winner = _build_winner(scenario["duplicated_winner_key"])
        # Simulate an accidental duplicate reaching the matching engine (the
        # real de-dup contract lives at the persistence layer's unique key on
        # (draw_id, prize_coupon_number); this test documents the matching
        # engine's own defensive behavior if that ever fails).
        results = match_coupons([coupon], [winner, winner], now=NOW)
        self.assertEqual(len(results), scenario["expected_total_matches"])

    def test_no_coupons_returns_empty(self):
        winners = [_build_winner("primary")]
        self.assertEqual(match_coupons([], winners, now=NOW), [])

    def test_no_winners_returns_empty(self):
        coupon = _build_coupon("exact_winner")
        self.assertEqual(match_coupons([coupon], [], now=NOW), [])


if __name__ == "__main__":
    unittest.main()
