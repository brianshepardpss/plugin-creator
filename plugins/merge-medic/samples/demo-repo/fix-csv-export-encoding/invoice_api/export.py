"""CSV export of invoices for the finance team."""
import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
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


def export_file(invoices: Iterable[Invoice], path: Path) -> int:
    """Write the export to `path` as UTF-8 with a BOM so Excel shows accents
    in customer names (for example "Cafe Neko Fictif" with an accent)."""
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        return write_csv(invoices, fh)
