import unittest

from app.domain.normalization import (
    normalize_coupon_code,
    normalize_fiscal_year,
    normalize_network_name,
)
from tests.data_normalization import (
    COUPON_CODE_CASES,
    FISCAL_YEAR_CASES,
    NETWORK_CASES,
)


class NormalizeCouponCodeTests(unittest.TestCase):
    def test_cases(self):
        for name, raw, expected in COUPON_CODE_CASES:
            with self.subTest(name=name):
                self.assertEqual(normalize_coupon_code(raw), expected)


class NormalizeFiscalYearTests(unittest.TestCase):
    def test_cases(self):
        for name, raw, expected in FISCAL_YEAR_CASES:
            with self.subTest(name=name):
                self.assertEqual(normalize_fiscal_year(raw), expected)


class NormalizeNetworkNameTests(unittest.TestCase):
    def test_cases(self):
        for name, raw, expected in NETWORK_CASES:
            with self.subTest(name=name):
                self.assertEqual(normalize_network_name(raw), expected)


if __name__ == "__main__":
    unittest.main()
