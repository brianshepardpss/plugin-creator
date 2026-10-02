"""CSV export of invoices for the finance team."""
import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, TextIO

COLUMNS = ["invoice_id", "customer", "due_date", "amount_due"]


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
        writer.writerow([inv.invoice_id, inv.customer,
                         inv.due_date.isoformat(), f"{inv.amount_due:.2f}"])
        rows += 1
    return rows
