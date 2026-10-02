"""CSV export of invoices for the finance team."""
import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, TextIO

from invoice_api.late_fees import late_fee

COLUMNS = ["invoice_id", "customer", "due_date", "amount_due", "late_fee"]


@dataclass
class Invoice:
    invoice_id: str
    customer: str
    due_date: date
    amount_due: Decimal


def write_csv(invoices: Iterable[Invoice], out: TextIO) -> int:
    """Write invoices as CSV rows to `out`. Returns the number of rows."""
    writer = csv.writer(out)
    writer.writerow(COLUMNS)
    rows = 0
    for inv in invoices:
        days_late = (date.today() - inv.due_date).days
        fee = late_fee(inv.amount_due, days_late)
        writer.writerow([inv.invoice_id, inv.customer,
                         inv.due_date.isoformat(), f"{inv.amount_due:.2f}",
                         "%.2f" % float(fee)])
        rows += 1
    return rows
