#!/usr/bin/env python3
"""Price a change order request with the working shown. Standard library only.

Usage:
  python3 co_calc.py \
    --labor "Painter/Journeyman:3:8:2"          # trade[/class]:workers:hours_per_day:days (rate from --rates)
    --labor "Carpenter:1:4:1@78.00"             # or give the hourly rate after @
    --rates rates.csv                            # columns trade, classification, rate_per_hour
    --material "Paint and sundries=1240.00"      # repeatable
    --equipment "Scissor lift, 2 days=350.00"    # repeatable
    --sub "Electrical sub quote Q-118=2150.00"   # repeatable (subcontract quotes)
    --tax 8.25                                   # % sales tax on material only (optional)
    --oh 10 --fee 5 [--fee-base cost+oh|cost]    # markups in %, default fee on cost + OH
    [--sub-markup 5]                             # % markup on subcontract total instead of OH/fee
    [--bond 1.0]                                 # % bond on the final subtotal (optional)

Formulas (Decimal, each money line rounded half-up to the cent):
  labor line      = workers x hours/day x days x rate
  material tax    = material subtotal x tax%
  direct cost     = labor + material + tax + equipment
  overhead        = direct cost x OH%
  fee             = (direct cost + overhead) x fee%   (or direct cost x fee% with --fee-base cost)
  subcontracts    = sum of quotes, + sub markup% if given
  subtotal        = direct cost + overhead + fee + subcontracts (+ markup)
  bond            = subtotal x bond%
  total           = subtotal + bond
Markup rates are whatever the user's contract allows; this script does not
know them and does not check them.
"""
import argparse
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP

C = Decimal("0.01")


def money(x):
    return x.quantize(C, rounding=ROUND_HALF_UP)


def fmt(x):
    return f"${money(x):,.2f}"


def load_rates(path):
    rates = {}
    if not path:
        return rates
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            t = (r.get("trade") or "").strip().lower()
            c = (r.get("classification") or "").strip().lower()
            rates[(t, c)] = Decimal(r["rate_per_hour"])
            rates.setdefault((t, ""), Decimal(r["rate_per_hour"]))
    return rates


def kv(s):
    name, _, amt = s.rpartition("=")
    return name.strip(), Decimal(amt.replace("$", "").replace(",", ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--labor", action="append", default=[])
    ap.add_argument("--rates")
    ap.add_argument("--material", action="append", default=[])
    ap.add_argument("--equipment", action="append", default=[])
    ap.add_argument("--sub", action="append", default=[])
    ap.add_argument("--tax", type=Decimal, default=Decimal(0))
    ap.add_argument("--oh", type=Decimal, default=Decimal(0))
    ap.add_argument("--fee", type=Decimal, default=Decimal(0))
    ap.add_argument("--fee-base", choices=["cost+oh", "cost"], default="cost+oh")
    ap.add_argument("--sub-markup", type=Decimal, default=Decimal(0))
    ap.add_argument("--bond", type=Decimal, default=Decimal(0))
    a = ap.parse_args()
    rates = load_rates(a.rates)

    print("COST BACKUP (computed by co_calc.py; verify rates and markups against your contract)\n")
    print("Labor")
    print("| Trade | Workers | Hrs/day | Days | Hours | Rate | Amount |")
    print("|---|---|---|---|---|---|---|")
    labor = Decimal(0)
    for l in a.labor:
        spec, _, rate = l.partition("@")
        trade, w, hpd, days = spec.split(":")
        t, _, cls = trade.partition("/")
        if rate:
            r, src = Decimal(rate), "given"
        else:
            r = rates.get((t.strip().lower(), cls.strip().lower()))
            src = "rates file"
            if r is None:
                sys.exit(f"no rate for {trade!r}; add it to the rates file or use @RATE")
        hours = Decimal(w) * Decimal(hpd) * Decimal(days)
        amt = money(hours * r)
        labor += amt
        print(f"| {trade} | {w} | {hpd} | {days} | {hours} | {fmt(r)}/h ({src}) | {fmt(amt)} |")
        print(f"|  | working: {w} x {hpd} h x {days} d = {hours} h x {fmt(r)} = {fmt(amt)} | | | | | |")
    print(f"| **Labor subtotal** | | | | | | **{fmt(labor)}** |\n")

    def section(title, items):
        tot = Decimal(0)
        if items:
            print(title)
            print("| Item | Amount |\n|---|---|")
            for s in items:
                n, v = kv(s)
                tot += money(v)
                print(f"| {n} | {fmt(v)} |")
            print(f"| **{title} subtotal** | **{fmt(tot)}** |\n")
        return tot

    mat = section("Material", a.material)
    tax = money(mat * a.tax / 100)
    eq = section("Equipment", a.equipment)
    subs = section("Subcontract", a.sub)

    direct = labor + mat + tax + eq
    oh = money(direct * a.oh / 100)
    fee_base = direct + oh if a.fee_base == "cost+oh" else direct
    fee = money(fee_base * a.fee / 100)
    smk = money(subs * a.sub_markup / 100)
    subtotal = direct + oh + fee + subs + smk
    bond = money(subtotal * a.bond / 100)
    total = subtotal + bond

    print("Summary")
    print("| Line | Working | Amount |\n|---|---|---|")
    print(f"| Labor | | {fmt(labor)} |")
    if mat:
        print(f"| Material | | {fmt(mat)} |")
    if tax:
        print(f"| Sales tax on material | {fmt(mat)} x {a.tax}% | {fmt(tax)} |")
    if eq:
        print(f"| Equipment | | {fmt(eq)} |")
    print(f"| Direct cost | labor + material + tax + equipment | {fmt(direct)} |")
    if a.oh:
        print(f"| Overhead | {fmt(direct)} x {a.oh}% | {fmt(oh)} |")
    if a.fee:
        print(f"| Fee | {fmt(fee_base)} x {a.fee}% ({'cost + OH' if a.fee_base == 'cost+oh' else 'cost'}) | {fmt(fee)} |")
    if subs:
        print(f"| Subcontracts | quotes | {fmt(subs)} |")
    if smk:
        print(f"| Markup on subcontracts | {fmt(subs)} x {a.sub_markup}% | {fmt(smk)} |")
    if a.bond:
        print(f"| Subtotal | | {fmt(subtotal)} |")
        print(f"| Bond | {fmt(subtotal)} x {a.bond}% | {fmt(bond)} |")
    print(f"| **TOTAL REQUESTED** | | **{fmt(total)}** |")


if __name__ == "__main__":
    main()
