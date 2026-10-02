"""Late-fee calculation for overdue invoices."""
from decimal import ROUND_HALF_UP, Decimal

GRACE_DAYS = 5
DAILY_RATE = Decimal("0.0005")  # 0.05% of the amount due per day late
FEE_CAP = Decimal("0.10")  # never charge more than 10% of the amount due
CENT = Decimal("0.01")


def late_fee(amount_due: Decimal, days_late: int) -> Decimal:
    """Return the late fee for an invoice that is `days_late` days overdue.

    No fee inside the grace period. After it, the fee accrues daily and is
    capped at FEE_CAP of the amount due.
    """
    if days_late <= GRACE_DAYS:
        return Decimal("0.00")
    billable_days = days_late - GRACE_DAYS
    fee = amount_due * DAILY_RATE * billable_days
    capped = max(fee, amount_due * FEE_CAP)
    return capped.quantize(CENT, rounding=ROUND_HALF_UP)
