#!/usr/bin/env python3
"""12-month sphere-of-influence touch calendar. Standard library only.

Usage:
  python3 nurture.py contacts.csv [--start 2026-11] [--months 12]
                     [--out plan.md] [--csv-out calendar.csv]

Rules (edit TIERS / THEMES below to change them):
  Tier A: a touch every month; a phone call in plan months 1, 4, 7, 10.
  Tier B: a touch in plan months 1, 3, 5, 7, 9, 11.
  Tier C: a touch in plan months 1, 4, 7, 10 (email only).
  Missing tier -> C. Plus, for every tier:
    - home-anniversary note in the month of Home Purchase Date
    - birthday note in Birthday Month (A and B only)
  Channel: email if Email OK = Y and an email exists; text if Text OK = Y and
  a phone exists; call if a phone exists (calls are personal, manual dials).
  If no channel is allowed: "mail or in person".
  Touch date: contacts are spread across the month by row order
  (day 1 + 7 x (row index mod 4), moved to the next Monday if it is a weekend);
  anniversary notes use the anniversary day; birthday notes go 3 days after
  the regular touch day (max the 28th). Weekend dates move to Monday, or to
  the Friday before when Monday would fall in the next month.
  Contacts last reached more than 180 days before the start date are flagged
  "reconnect first" (a personal note before any market email).
"""
import argparse
import csv
import re
from datetime import date, datetime, timedelta
from pathlib import Path

THEMES = {1: "year-in-review market recap (facts from your MLS stats)", 2: "homeowner records checklist (no tax advice)",
          3: "spring maintenance checklist", 4: "spring market update", 5: "home value check-in offer",
          6: "client appreciation event invite", 7: "mid-year market update", 8: "summer maintenance tips",
          9: "fall maintenance checklist", 10: "home value check-in offer", 11: "thank-you note",
          12: "season's greetings card"}
TIERS = {"A": set(range(1, 13)), "B": {1, 3, 5, 7, 9, 11}, "C": {1, 4, 7, 10}}
CALL_MONTHS = {1, 4, 7, 10}
COLS = {"name": ["name", "full name", "contact"], "email": ["email", "e-mail"], "phone": ["phone", "mobile", "cell"],
        "tier": ["tier", "grade", "priority", "abc"], "rel": ["relationship", "source", "type"],
        "purchase": ["home purchase date", "closing date", "purchase date", "close date"],
        "bmonth": ["birthday month", "birth month"], "last": ["last contact", "last touch", "last contacted"],
        "email_ok": ["email ok", "email opt in", "email consent"], "text_ok": ["text ok", "sms ok", "text consent", "consent to text"]}


def n(s):
    return re.sub(r"[^a-z0-9]", " ", (s or "").lower()).strip()


def yes(v):
    return n(v) in {"y", "yes", "true", "1"}


def weekday_fix(d):
    """Weekend -> next Monday, unless that leaves the month; then the Friday before."""
    e = d
    while e.weekday() >= 5:
        e += timedelta(days=1)
    if e.month != d.month:
        e = d
        while e.weekday() >= 5:
            e -= timedelta(days=1)
    return e


def add_months(y, m, k):
    t = (y * 12 + m - 1) + k
    return t // 12, t % 12 + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--start", help="YYYY-MM, default next month")
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--out")
    ap.add_argument("--csv-out")
    a = ap.parse_args()
    if a.start:
        sy, sm = map(int, a.start.split("-"))
    else:
        t = date.today()
        sy, sm = add_months(t.year, t.month, 1)
    start = date(sy, sm, 1)
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        hm = {}
        for k, al in COLS.items():
            for h in rd.fieldnames or []:
                if n(h) in al and k not in hm:
                    hm[k] = h
        rows = [{k: (r.get(h) or "").strip() for k, h in hm.items()} for r in rd]
    rows = [r for r in rows if r.get("name")]
    events, flags = [], []
    for idx, r in enumerate(rows):
        tier = (r.get("tier") or "C").upper()[:1]
        tier = tier if tier in TIERS else "C"
        ch = []
        if r.get("email") and yes(r.get("email_ok")):
            ch.append("email")
        if r.get("phone") and yes(r.get("text_ok")):
            ch.append("text")
        last = r.get("last")
        if last:
            try:
                ld = datetime.strptime(last, "%Y-%m-%d").date()
                if (start - ld).days > 180:
                    flags.append((r["name"], f"last contact {last} ({(start - ld).days} days before plan start): reconnect first"))
            except ValueError:
                flags.append((r["name"], f"unreadable last contact {last!r}"))
        else:
            flags.append((r["name"], "no last-contact date: reconnect first"))
        pdt = None
        if r.get("purchase"):
            try:
                pdt = datetime.strptime(r["purchase"], "%Y-%m-%d").date()
            except ValueError:
                flags.append((r["name"], f"unreadable purchase date {r['purchase']!r}"))
        bm = int(r["bmonth"]) if (r.get("bmonth") or "").isdigit() else None
        for k in range(a.months):
            y, m = add_months(sy, sm, k)
            pm = k + 1
            day = weekday_fix(date(y, m, 1 + 7 * (idx % 4)))
            if pm in TIERS[tier]:
                if tier == "A" and pm in CALL_MONTHS and r.get("phone"):
                    events.append((day, r["name"], tier, "call", "personal check-in call"))
                else:
                    c = (ch[:1] if tier != "C" else [x for x in ch if x == "email"]) or ["mail or in person"]
                    events.append((day, r["name"], tier, c[0], THEMES[m]))
            if pdt and pdt.month == m and pdt.year < y:
                try:
                    ad = date(y, m, pdt.day)
                except ValueError:
                    ad = date(y, m, 28)
                events.append((weekday_fix(ad), r["name"], tier, (ch[:1] or ["mail or in person"])[0],
                               f"home anniversary ({y - pdt.year} years) note"))
            if bm == m and tier in ("A", "B"):
                bday = weekday_fix(date(y, m, min(28, day.day + 3)))  # a few days after the regular touch
                events.append((bday, r["name"], tier, (ch[:1] or ["mail or in person"])[0], "birthday note"))
    events.sort()
    end_y, end_m = add_months(sy, sm, a.months - 1)
    L = [f"# Sphere nurture plan: {start:%B %Y} to {date(end_y, end_m, 1):%B %Y}", "",
         f"Contacts: {len(rows)} (A {sum(1 for r in rows if (r.get('tier') or 'C')[:1].upper() == 'A')}, "
         f"B {sum(1 for r in rows if (r.get('tier') or 'C')[:1].upper() == 'B')}, "
         f"C/other {sum(1 for r in rows if (r.get('tier') or 'C')[:1].upper() not in 'AB')}). Touches: {len(events)}.", ""]
    if flags:
        L += ["## Reconnect first", ""] + [f"- {nm}: {why}" for nm, why in flags] + [""]
    L += ["## Touches per month", "", "| Month | Touches | Calls | Emails | Texts | Mail/in person | Theme |", "|---|---|---|---|---|---|---|"]
    for k in range(a.months):
        y, m = add_months(sy, sm, k)
        ev = [e for e in events if e[0].year == y and e[0].month == m]
        c = lambda x: sum(1 for e in ev if e[3] == x)
        L.append(f"| {date(y, m, 1):%b %Y} | {len(ev)} | {c('call')} | {c('email')} | {c('text')} | {c('mail or in person')} | {THEMES[m]} |")
    L += ["", "## Calendar", "", "| Date | Contact | Tier | Channel | Touch |", "|---|---|---|---|---|"]
    L += [f"| {d.isoformat()} | {nm} | {t} | {c} | {w} |" for d, nm, t, c, w in events]
    L += ["", "Drafts only: review and send each touch yourself. Email touches include an unsubscribe line; "
          "texts go only to contacts marked Text OK = Y and include \"Reply STOP to opt out\".", ""]
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    if a.csv_out:
        with open(a.csv_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Contact", "Tier", "Channel", "Touch"])
            w.writerows([(d.isoformat(), nm, t, c, x) for d, nm, t, c, x in events])
    print(text)


if __name__ == "__main__":
    main()
