#!/usr/bin/env python3
"""Grant deadline tracker: a CSV you own plus a calendar (.ics) file.

Usage:
  python3 tracker.py add --tracker grants/tracker.csv --funder "Cedar Mill Family Foundation" \
      --item "Letter of inquiry" --type application --due "2026-10-30" --time "17:00 CT" \
      [--amount 25000] [--source "sample-rfp.md: Key dates"] [--notes "..."]
  python3 tracker.py add-json --tracker grants/tracker.csv items.json
  python3 tracker.py list --tracker grants/tracker.csv [--within 90] [--today 2026-10-02]
  python3 tracker.py done --tracker grants/tracker.csv --id 3

--due accepts:
  2026-10-30 | 10/30/2026 | October 30, 2026 | Oct 30 2026
  "<date> +N days|weeks|months|years" (chainable, minus allowed)
     e.g. "2026-10-01 +6 months"; grant end for a 12-month period starting
     2026-10-01 is "2026-10-01 +12 months -1 day"
  (relative deadlines from award letters: "6 months after the start date")

items.json is a list of objects with keys funder, item, type, due, time,
amount, source, notes.

Formulas:
  +N months   = same day N calendar months later, clamped to the month's last day
  days_left   = due_date - today (calendar days; negative = overdue)
  remind_1    = due_date - 14 days ; remind_2 = due_date - 3 days
Rows are de-duplicated on (funder, item, due_date). Every add rewrites
<tracker dir>/deadlines.ics (all-day events with alarms 14 and 3 days before)
so it can be imported into Google Calendar, Outlook or Apple Calendar.
"""
import argparse
import calendar
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

COLS = ["id", "funder", "item", "type", "due_date", "due_time", "remind_1", "remind_2",
        "amount", "status", "source", "notes", "added_on"]
TYPES = {"application", "loi", "report", "agreement", "payment", "other"}


def add_months(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def parse_date(s):
    s = s.strip()
    rel = re.match(r"^(.*?)\s*([+-])\s*(\d+)\s*(day|week|month|year)s?$", s, re.I)
    if rel:
        base = parse_date(rel.group(1))
        n = int(rel.group(3)) * (1 if rel.group(2) == "+" else -1)
        unit = rel.group(4).lower()
        if unit == "day":
            return base + dt.timedelta(days=n)
        if unit == "week":
            return base + dt.timedelta(weeks=n)
        if unit == "month":
            return add_months(base, n)
        return add_months(base, 12 * n)
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    sys.exit(f"ERROR: cannot read date {s!r}. Use YYYY-MM-DD or '<date> +N months'.")


def load(path):
    p = Path(path)
    if not p.exists():
        return []
    with p.open(newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def save(path, rows):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda r: (r["due_date"], r["funder"]))
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLS})
    write_ics(p.parent / "deadlines.ics", rows)


def esc(s):
    return re.sub(r"([,;\\])", r"\\\1", s or "").replace("\n", "\\n")


def write_ics(path, rows):
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Grant Desk//Deadlines//EN", "CALSCALE:GREGORIAN"]
    for r in rows:
        if r.get("status") == "done":
            continue
        d = dt.date.fromisoformat(r["due_date"])
        uid = re.sub(r"[^a-z0-9]+", "-", f"{r['funder']}-{r['item']}-{r['due_date']}".lower())
        out += ["BEGIN:VEVENT", f"UID:{uid}@grant-desk", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{(d + dt.timedelta(days=1)).strftime('%Y%m%d')}",
                f"SUMMARY:{esc('DUE: ' + r['funder'] + ' - ' + r['item'])}",
                f"DESCRIPTION:{esc('Type: ' + r['type'] + '. Time: ' + (r.get('due_time') or 'not stated') + '. Source: ' + (r.get('source') or '') + '. ' + (r.get('notes') or ''))}"]
        for days in (14, 3):
            out += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(r['item'])} due in {days} days",
                    f"TRIGGER:-P{days}D", "END:VALARM"]
        out.append("END:VEVENT")
    out.append("END:VCALENDAR")
    path.write_text("\r\n".join(fold(x) for x in out) + "\r\n")


def fold(line):
    """RFC 5545: lines longer than 75 octets continue on the next line after a space."""
    parts = []
    while len(line.encode()) > 75:
        parts.append(line[:73])
        line = " " + line[73:]
    return "\r\n".join(parts + [line])


def add_rows(tracker, items, today):
    rows = load(tracker)
    nxt = max([int(r["id"]) for r in rows if r.get("id", "").isdigit()] or [0]) + 1
    added = []
    for it in items:
        due = parse_date(str(it["due"]))
        typ = (it.get("type") or "other").lower()
        if typ not in TYPES:
            typ = "other"
        key = (it["funder"].strip().lower(), it["item"].strip().lower(), due.isoformat())
        if any((r["funder"].lower(), r["item"].lower(), r["due_date"]) == key for r in rows):
            print(f"skip (already tracked): {it['funder']} - {it['item']} {due}")
            continue
        r = {"id": str(nxt), "funder": it["funder"].strip(), "item": it["item"].strip(), "type": typ,
             "due_date": due.isoformat(), "due_time": it.get("time", ""),
             "remind_1": (due - dt.timedelta(days=14)).isoformat(),
             "remind_2": (due - dt.timedelta(days=3)).isoformat(),
             "amount": str(it.get("amount", "") or ""), "status": "open",
             "source": it.get("source", ""), "notes": it.get("notes", ""), "added_on": today.isoformat()}
        rows.append(r)
        added.append(r)
        nxt += 1
    save(tracker, rows)
    print(f"Added {len(added)} item(s) to {tracker}; calendar file: {Path(tracker).parent / 'deadlines.ics'}")
    show(rows, today, None)


def show(rows, today, within):
    print(f"\n| ID | Funder | Item | Type | Due | Time | Days left | Remind | Status |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: r["due_date"]):
        left = (dt.date.fromisoformat(r["due_date"]) - today).days
        if within is not None and (left > within or r["status"] == "done"):
            continue
        flag = "OVERDUE" if left < 0 and r["status"] != "done" else str(left)
        print(f"| {r['id']} | {r['funder']} | {r['item']} | {r['type']} | {r['due_date']} | "
              f"{r.get('due_time') or ''} | {flag} | {r['remind_1']}, {r['remind_2']} | {r['status']} |")
    print(f"\n(today = {today}; days left = due date - today)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--tracker", default="grants/tracker.csv")
    common.add_argument("--today")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("add", parents=[common])
    for k in ("funder", "item", "due"):
        a1.add_argument("--" + k, required=True)
    a1.add_argument("--type", default="other")
    a1.add_argument("--time", default="")
    a1.add_argument("--amount", default="")
    a1.add_argument("--source", default="")
    a1.add_argument("--notes", default="")
    a2 = sub.add_parser("add-json", parents=[common])
    a2.add_argument("file")
    a3 = sub.add_parser("list", parents=[common])
    a3.add_argument("--within", type=int)
    a4 = sub.add_parser("done", parents=[common])
    a4.add_argument("--id", required=True)
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    if a.cmd == "add":
        add_rows(a.tracker, [{"funder": a.funder, "item": a.item, "due": a.due, "type": a.type,
                              "time": a.time, "amount": a.amount, "source": a.source, "notes": a.notes}], today)
    elif a.cmd == "add-json":
        add_rows(a.tracker, json.loads(Path(a.file).read_text()), today)
    elif a.cmd == "list":
        show(load(a.tracker), today, a.within)
    else:
        rows = load(a.tracker)
        if not any(r["id"] == a.id for r in rows):
            sys.exit(f"ERROR: no tracker row with id {a.id}. Run `tracker.py list` to see ids.")
        for r in rows:
            if r["id"] == a.id:
                r["status"] = "done"
        save(a.tracker, rows)
        print(f"Marked {a.id} done.")


if __name__ == "__main__":
    main()
