import unittest
from decimal import Decimal

from invoice_api.late_fees import late_fee


class LateFeeTests(unittest.TestCase):
    def test_no_fee_inside_grace_period(self):
        self.assertEqual(late_fee(Decimal("1000.00"), 5), Decimal("0.00"))

    def test_fee_accrues_daily(self):
        # 15 days late = 10 billable days * 0.05% * 1000.00
        self.assertEqual(late_fee(Decimal("1000.00"), 15), Decimal("5.00"))

    def test_fee_is_capped(self):
        # 400 days late would be 197.50, but the cap is 10% = 100.00
        self.assertEqual(late_fee(Decimal("1000.00"), 400), Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
