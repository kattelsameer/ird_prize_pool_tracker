import unittest

from app.domain.claim_status import ClaimStatus, compute_claim_status
from tests.data_claim_status import CLAIM_STATUS_CASES, NAIVE_DATETIME_CASES


class ComputeClaimStatusTests(unittest.TestCase):
    def test_cases(self):
        for name, now, deadline, claim_open, expected in CLAIM_STATUS_CASES:
            with self.subTest(name=name):
                result = compute_claim_status(
                    now=now, claim_deadline=deadline, claim_open=claim_open
                )
                self.assertEqual(result, ClaimStatus(expected))

    def test_naive_datetimes_raise(self):
        for name, now, deadline in NAIVE_DATETIME_CASES:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    compute_claim_status(now=now, claim_deadline=deadline, claim_open=True)


if __name__ == "__main__":
    unittest.main()
