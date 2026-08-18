import unittest

from app.domain.prize_tiers import prize_amounts_for_category


class PrizeAmountsForCategoryTests(unittest.TestCase):
    def test_daily_prize(self):
        self.assertEqual(prize_amounts_for_category("Daily Prize"), (133_334, 100_000))

    def test_bumper_prize(self):
        self.assertEqual(prize_amounts_for_category("Bumper Prize"), (1_000_000, 750_000))

    def test_unknown_category_returns_none_rather_than_guessing(self):
        self.assertEqual(prize_amounts_for_category("Some New Category"), (None, None))

    def test_none_category_returns_none(self):
        self.assertEqual(prize_amounts_for_category(None), (None, None))


if __name__ == "__main__":
    unittest.main()
