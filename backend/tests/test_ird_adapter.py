import unittest

from app.integrations.ird.adapter import IrdResponseValidationError, adapt_winners_response
from tests.data_ird_adapter import (
    DUPLICATE_WINNER_IN_PAGE_PAYLOAD,
    EMPTY_PAGE_PAYLOAD,
    MALFORMED_PAYLOADS,
    MISSING_OPTIONAL_FIELDS_PAYLOAD,
    PARTIAL_DATA_PAYLOAD,
    VALID_PAGE_PAYLOAD,
)


class AdaptWinnersResponseTests(unittest.TestCase):
    def test_valid_page_produces_expected_normalized_record(self):
        page = adapt_winners_response(VALID_PAGE_PAYLOAD)
        self.assertEqual(page.limit, 6)
        self.assertEqual(page.offset, 0)
        self.assertFalse(page.has_more)
        self.assertEqual(len(page.winners), 1)
        record = page.winners[0]
        self.assertEqual(record.draw_id, "draw_3dcfe8001afc31a805736567ea3ea74f")
        self.assertEqual(record.prize_coupon_number, "007315254493")
        self.assertEqual(record.normalized_coupon_code, "007315254493")
        self.assertEqual(record.prize_fiscal_year_code, "2083-84")
        self.assertEqual(record.winner_rank, 1)
        self.assertTrue(record.claim_open)
        self.assertEqual(
            record.source_record_id, "draw_3dcfe8001afc31a805736567ea3ea74f:007315254493"
        )
        self.assertIn("winners", record.raw_draw_json)

    def test_partial_data_skips_invalid_winner_but_keeps_valid_one(self):
        page = adapt_winners_response(PARTIAL_DATA_PAYLOAD)
        self.assertEqual(len(page.winners), 1)
        self.assertEqual(page.winners[0].prize_coupon_number, "007315254493")

    def test_missing_optional_fields_do_not_raise(self):
        page = adapt_winners_response(MISSING_OPTIONAL_FIELDS_PAYLOAD)
        self.assertEqual(len(page.winners), 1)
        record = page.winners[0]
        self.assertIsNone(record.category_title_en)
        self.assertIsNone(record.draw_title_en)

    def test_empty_page_produces_zero_winners(self):
        page = adapt_winners_response(EMPTY_PAGE_PAYLOAD)
        self.assertEqual(page.winners, [])
        self.assertFalse(page.has_more)

    def test_duplicate_winner_entries_within_a_page_both_pass_through(self):
        # De-duplication is the persistence layer's responsibility (unique key
        # on draw_id+coupon); the adapter itself is a faithful pass-through.
        page = adapt_winners_response(DUPLICATE_WINNER_IN_PAGE_PAYLOAD)
        self.assertEqual(len(page.winners), 2)
        self.assertEqual(page.winners[0].source_record_id, page.winners[1].source_record_id)

    def test_malformed_payloads_raise_validation_error(self):
        for name, payload in MALFORMED_PAYLOADS:
            with self.subTest(name=name):
                with self.assertRaises(IrdResponseValidationError):
                    adapt_winners_response(payload)


if __name__ == "__main__":
    unittest.main()
