import io
import unittest
from datetime import date
from decimal import Decimal

from invoice_api.export import Invoice, write_csv


class ExportTests(unittest.TestCase):
    def test_header_and_row(self):
        buf = io.StringIO()
        n = write_csv([Invoice("INV-1001", "Acme Fake Foods", date.today(),
                               Decimal("250.00"))], buf)
        self.assertEqual(n, 1)
        lines = buf.getvalue().splitlines()
        self.assertEqual(lines[0], "invoice_id,customer,due_date,amount_due,late_fee")
        self.assertTrue(lines[1].endswith(",250.00,0.00"))


if __name__ == "__main__":
    unittest.main()
