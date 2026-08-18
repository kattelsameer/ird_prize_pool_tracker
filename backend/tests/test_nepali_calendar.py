import unittest

from app.domain.nepali_calendar import bs_half_month_period_for_date, fiscal_year_for_gregorian_date
from tests.data_nepali_calendar import FISCAL_YEAR_BOUNDARY_CASES, HALF_MONTH_PERIOD_CASES


class FiscalYearForGregorianDateTests(unittest.TestCase):
    def test_boundary_cases(self):
        for name, gdate, expected_fy in FISCAL_YEAR_BOUNDARY_CASES:
            with self.subTest(name=name):
                info = fiscal_year_for_gregorian_date(gdate)
                self.assertEqual(info.fiscal_year_code, expected_fy)


class BsHalfMonthPeriodForDateTests(unittest.TestCase):
    def test_boundary_cases(self):
        for name, gdate, expected_start, expected_end, expected_publish in HALF_MONTH_PERIOD_CASES:
            with self.subTest(name=name):
                period = bs_half_month_period_for_date(gdate)
                self.assertEqual(period.period_start, expected_start)
                self.assertEqual(period.period_end, expected_end)
                self.assertEqual(period.expected_publish_date, expected_publish)


if __name__ == "__main__":
    unittest.main()
