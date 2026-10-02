import io
import unittest
from datetime import date
from decimal import Decimal

from invoice_api.export import Invoice, write_csv


class ExportTests(unittest.TestCase):
    def test_header_and_row(self):
        buf = io.StringIO()
        n = write_csv([Invoice("INV-1001", "Acme Fake Foods", date(2026, 9, 1),
                               Decimal("250.00"))], buf)
        self.assertEqual(n, 1)
        lines = buf.getvalue().splitlines()
        self.assertEqual(lines[0], "invoice_id,customer,due_date,amount_due")
        self.assertEqual(lines[1], "INV-1001,Acme Fake Foods,2026-09-01,250.00")


if __name__ == "__main__":
    unittest.main()
