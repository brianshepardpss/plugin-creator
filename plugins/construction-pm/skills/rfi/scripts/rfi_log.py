#!/usr/bin/env python3
"""Maintain an RFI log CSV. Standard library only.

Usage:
  python3 rfi_log.py report --log rfis.csv [--as-of YYYY-MM-DD]
  python3 rfi_log.py add --log rfis.csv --subject "..." --spec-ref "08 71 00 / 3.4.C" \
      [--drawing-ref A-601] [--sent YYYY-MM-DD] [--response-days 7 | --due YYYY-MM-DD] \
      [--ball Architect] [--cost-impact TBD] [--schedule-impact TBD]
  python3 rfi_log.py close --log rfis.csv --rfi RFI-003 --date YYYY-MM-DD [--answer "..."]

Rules (calendar days throughout):
  next number   = highest existing RFI-NNN + 1 (blank rows ignored)
  response due  = date sent + response days (default 7), unless --due is given
  days open     = (date answered or as-of date) - date sent
  days past due = as-of date - response due, for open RFIs past due
If the log does not exist, `add` creates it with the standard columns.
Dates in the log may be 2026-10-05, 10/5/2026 or 10/5/26; new rows use ISO.
"""
import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

COLS = ["RFI No", "Subject", "Spec Ref", "Drawing Ref", "Date Sent", "Response Due", "Ball In Court",
        "Status", "Date Answered", "Cost Impact", "Schedule Impact", "Answer Summary"]


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%y", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def safe(v):
    v = "" if v is None else str(v)
    return "'" + v if v[:1] in ("=", "+", "@") else v


def load(path):
    p = Path(path)
    if not p.exists():
        return list(COLS), []
    with open(p, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        rows = [r for r in rd if any((v or "").strip() for v in r.values())]
        return rd.fieldnames, rows


def col(fields, want):
    """Find the log's column for a standard name (case/spacing tolerant)."""
    key = re.sub(r"[^a-z]", "", want.lower())
    for f in fields:
        if re.sub(r"[^a-z]", "", (f or "").lower()) == key:
            return f
    return want


def save(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: safe(r.get(k, "")) for k in fields})


def num(s):
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else 0


def report(a):
    fields, rows = load(a.log)
    C = {k: col(fields, k) for k in COLS}
    as_of = parse_date(a.as_of) if a.as_of else dt.date.today()
    print(f"RFI log as of {as_of} (calendar days)\n")
    print("| RFI | Subject | Ball in court | Status | Sent | Due | Days open | Past due |")
    print("|---|---|---|---|---|---|---|---|")
    n_open = n_late = 0
    for r in rows:
        sent, due, ans = (parse_date(r.get(C[k])) for k in ("Date Sent", "Response Due", "Date Answered"))
        closed = (r.get(C["Status"]) or "").lower().startswith(("closed", "answered")) or ans is not None
        end = ans if (closed and ans) else as_of
        days_open = (end - sent).days if sent else "?"
        past = ""
        if not closed:
            n_open += 1
            if due and as_of > due:
                past = f"{(as_of - due).days}d"
                n_late += 1
        print(f"| {r.get(C['RFI No'])} | {r.get(C['Subject'])} | {r.get(C['Ball In Court'])} | "
              f"{'Closed' if closed else 'Open'} | {sent or '?'} | {due or '?'} | {days_open} | {past} |")
    print(f"\n{len(rows)} RFIs, {n_open} open, {n_late} past due.")


def add(a):
    fields, rows = load(a.log)
    C = {k: col(fields, k) for k in COLS}
    nxt = max([num(r.get(C["RFI No"])) for r in rows] + [0]) + 1
    width = max([len(re.sub(r"\D", "", r.get(C["RFI No"]) or "")) for r in rows] + [3])
    sent = parse_date(a.sent) if a.sent else dt.date.today()
    if a.sent and not sent:
        sys.exit(f"cannot read --sent {a.sent!r}; use YYYY-MM-DD")
    due = parse_date(a.due) if a.due else sent + dt.timedelta(days=a.response_days)
    row = {C["RFI No"]: f"RFI-{nxt:0{width}d}", C["Subject"]: a.subject, C["Spec Ref"]: a.spec_ref,
           C["Drawing Ref"]: a.drawing_ref, C["Date Sent"]: sent.isoformat(), C["Response Due"]: due.isoformat(),
           C["Ball In Court"]: a.ball, C["Status"]: "Open", C["Date Answered"]: "",
           C["Cost Impact"]: a.cost_impact, C["Schedule Impact"]: a.schedule_impact, C["Answer Summary"]: ""}
    rows.append(row)
    save(a.log, fields, rows)
    how = "given" if a.due else f"{sent} + {a.response_days}d"
    print(f"Added {row[C['RFI No']]} to {a.log}: sent {sent}, response due {due} ({how}), ball in court {a.ball}.")


def close(a):
    fields, rows = load(a.log)
    C = {k: col(fields, k) for k in COLS}
    d = parse_date(a.date)
    if not d:
        sys.exit(f"cannot read --date {a.date!r}")
    for r in rows:
        if num(r.get(C["RFI No"])) == num(a.rfi):
            r[C["Status"]], r[C["Date Answered"]], r[C["Ball In Court"]] = "Closed", d.isoformat(), "GC"
            if a.answer:
                r[C["Answer Summary"]] = a.answer
            sent = parse_date(r.get(C["Date Sent"]))
            save(a.log, fields, rows)
            print(f"Closed {r[C['RFI No']]} on {d}" + (f" after {(d - sent).days} days." if sent else "."))
            return
    sys.exit(f"{a.rfi} not found in {a.log}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("report")
    r.add_argument("--log", required=True)
    r.add_argument("--as-of")
    x = sp.add_parser("add")
    x.add_argument("--log", required=True)
    x.add_argument("--subject", required=True)
    x.add_argument("--spec-ref", default="")
    x.add_argument("--drawing-ref", default="")
    x.add_argument("--sent")
    x.add_argument("--response-days", type=int, default=7)
    x.add_argument("--due")
    x.add_argument("--ball", default="Architect")
    x.add_argument("--cost-impact", default="TBD")
    x.add_argument("--schedule-impact", default="TBD")
    c = sp.add_parser("close")
    c.add_argument("--log", required=True)
    c.add_argument("--rfi", required=True)
    c.add_argument("--date", required=True)
    c.add_argument("--answer")
    a = ap.parse_args()
    {"report": report, "add": add, "close": close}[a.cmd](a)


if __name__ == "__main__":
    main()
