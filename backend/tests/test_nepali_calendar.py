import unittest

from app.domain.nepali_calendar import fiscal_year_for_gregorian_date
from tests.data_nepali_calendar import FISCAL_YEAR_BOUNDARY_CASES


class FiscalYearForGregorianDateTests(unittest.TestCase):
    def test_boundary_cases(self):
        for name, gdate, expected_fy in FISCAL_YEAR_BOUNDARY_CASES:
            with self.subTest(name=name):
                info = fiscal_year_for_gregorian_date(gdate)
                self.assertEqual(info.fiscal_year_code, expected_fy)


if __name__ == "__main__":
    unittest.main()
