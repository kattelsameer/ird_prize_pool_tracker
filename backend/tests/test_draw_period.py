import unittest
from datetime import date

from app.domain.draw_period import classify_period
from tests.data_draw_period import BHADRA_1_15, KNOWN_PERIODS, SHRAWAN_16_31


class ClassifyPeriodTests(unittest.TestCase):
    def test_transaction_within_a_known_period_is_drawn(self):
        status = classify_period(date(2026, 8, 10), KNOWN_PERIODS)
        self.assertEqual(status.state, "DRAWN")
        self.assertEqual(status.draw_id, SHRAWAN_16_31.draw_id)
        self.assertEqual(status.eligible_from, SHRAWAN_16_31.eligible_from)
        self.assertEqual(status.eligible_to, SHRAWAN_16_31.eligible_to)
        self.assertEqual(status.published_at, SHRAWAN_16_31.published_at)
        self.assertFalse(status.is_estimated)
        self.assertIsNone(status.estimated_publish_date)

    def test_transaction_on_a_known_period_boundary_is_drawn(self):
        status = classify_period(date(2026, 8, 17), KNOWN_PERIODS)
        self.assertEqual(status.state, "DRAWN")
        self.assertEqual(status.draw_id, BHADRA_1_15.draw_id)

    def test_transaction_newer_than_every_known_period_is_pending(self):
        # 2026-09-05 falls after BHADRA_1_15's eligible_to (2026-08-31) --
        # nothing synced covers it yet.
        status = classify_period(date(2026, 9, 5), KNOWN_PERIODS)
        self.assertEqual(status.state, "PENDING")
        self.assertTrue(status.is_estimated)
        self.assertIsNone(status.draw_id)
        self.assertIsNotNone(status.eligible_from)
        self.assertIsNotNone(status.eligible_to)
        self.assertIsNotNone(status.estimated_publish_date)

    def test_transaction_in_a_gap_between_known_periods_is_unknown(self):
        # A transaction predating everything we've synced (e.g. before the
        # earliest known eligible_from) is a sync gap, not "not drawn yet".
        status = classify_period(date(2026, 7, 20), KNOWN_PERIODS)
        self.assertEqual(status.state, "UNKNOWN")
        self.assertFalse(status.is_estimated)
        self.assertIsNone(status.eligible_from)
        self.assertIsNone(status.draw_id)

    def test_no_known_periods_at_all_is_pending(self):
        # A fresh install with nothing synced yet should never claim a gap --
        # every transaction date is trivially "newer than nothing we know of".
        status = classify_period(date(2026, 8, 10), [])
        self.assertEqual(status.state, "PENDING")
        self.assertTrue(status.is_estimated)

    def test_no_transaction_date_returns_none(self):
        self.assertIsNone(classify_period(None, KNOWN_PERIODS))


if __name__ == "__main__":
    unittest.main()
