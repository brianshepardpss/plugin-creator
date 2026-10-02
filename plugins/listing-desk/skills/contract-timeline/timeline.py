#!/usr/bin/env python3
"""Contract deadline calculator and .ics writer. Standard library only.

Usage:
  python3 timeline.py terms.json [--out timeline.md] [--ics deadlines.ics]
                      [--extra-holidays 2026-11-27,2026-12-24]

terms.json (written by the contract-timeline skill from the contract):
  {
    "property": "26 Larkspur Dr, Cedar Hollow, TX 75999",
    "effective_date": "2026-10-09",
    "rollover": true,          # contract: deadline on Sat/Sun/holiday moves to next business day
    "deadline_time": "5:00 p.m. local time",
    "terms": [["Sales price", "$405,000", "Para 3"], ...],      # optional key-terms table
    "deadlines": [
      {"id": "earnest", "name": "Earnest money due", "days": 3, "unit": "business",
       "from": "effective", "source": "Para 5", "owner": "Buyer"},
      {"id": "closing", "name": "Closing", "date": "2026-11-13", "source": "Para 13"},
      {"id": "walk", "name": "Final walk-through", "days": 1, "unit": "calendar",
       "before": "closing", "source": "Para 14", "owner": "Buyer"}
    ]
  }
  "from"/"before" name "effective" or another deadline's id (chains are fine).

Rules (printed with every date so the working can be audited):
  - Day counting starts the day AFTER the base date (the base date is not
    counted), unless "count_base_day": true.
  - calendar: date = base + N days. If rollover is true and that date is a
    Saturday, Sunday or federal holiday, it moves forward to the next business day.
  - business: step forward one day at a time, counting only Mon-Fri days that
    are not federal holidays, until N are counted.
  - before: date = base - N calendar days (or N business days). It is never
    moved; if it lands on a weekend or holiday it is flagged VERIFY.
  - fixed "date": used as written; flagged if it is not a business day.
  - Federal holidays: 5 USC 6103 (New Year, MLK, Washington's Birthday,
    Memorial, Juneteenth, Independence, Labor, Columbus, Veterans,
    Thanksgiving, Christmas), with Saturday -> Friday and Sunday -> Monday
    observed dates. State and local holidays are NOT included; add them with
    --extra-holidays or the "extra_holidays" list. Your contract's own
    definition of "business day" always governs.
Every date is a checklist item to verify against the executed contract.
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def nth_weekday(y, m, weekday, n):
    d = date(y, m, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def last_weekday(y, m, weekday):
    d = date(y, m + 1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def observed(d):
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def federal_holidays(y):
    h = {
        observed(date(y, 1, 1)): "New Year's Day",
        nth_weekday(y, 1, 0, 3): "Martin Luther King Jr. Day",
        nth_weekday(y, 2, 0, 3): "Washington's Birthday",
        last_weekday(y, 5, 0): "Memorial Day",
        observed(date(y, 7, 4)): "Independence Day",
        nth_weekday(y, 9, 0, 1): "Labor Day",
        nth_weekday(y, 10, 0, 2): "Columbus Day",
        observed(date(y, 11, 11)): "Veterans Day",
        nth_weekday(y, 11, 3, 4): "Thanksgiving Day",
        observed(date(y, 12, 25)): "Christmas Day",
    }
    if y >= 2021:
        h[observed(date(y, 6, 19))] = "Juneteenth"
    return h


class Cal:
    def __init__(self, extra):
        self.extra = {d: "extra holiday (user supplied)" for d in extra}
        self.cache = {}

    def holiday(self, d):
        for y in (d.year, d.year + 1):  # New Year's on a Saturday is observed Dec 31
            if y not in self.cache:
                self.cache[y] = federal_holidays(y)
            if d in self.cache[y]:
                return self.cache[y][d]
        return self.extra.get(d)

    def business(self, d):
        return d.weekday() < 5 and not self.holiday(d)

    def why_not(self, d):
        if d.weekday() >= 5:
            return DOW[d.weekday()]
        return self.holiday(d)


def pd(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def ds(d):
    return f"{DOW[d.weekday()]} {d.isoformat()}"


def compute(t, cal):
    eff = pd(t["effective_date"])
    rollover = t.get("rollover", True)
    known = {"effective": eff}
    out = []
    pending = list(t["deadlines"])
    guard = 0
    while pending and guard < 1000:
        guard += 1
        dl = pending.pop(0)
        base_id = dl.get("from") or dl.get("before")
        if "date" not in dl and base_id not in known:
            pending.append(dl)
            continue
        flags, steps = [], []
        if "date" in dl:
            d = pd(dl["date"])
            steps.append(f"fixed date in contract: {ds(d)}")
            if not cal.business(d):
                flags.append(f"falls on {cal.why_not(d)}; confirm with the parties")
        else:
            base = known[base_id]
            n, unit = int(dl["days"]), dl.get("unit", "calendar")
            if unit not in ("calendar", "business"):
                sys.exit(f"{dl.get('id', dl['name'])}: unit must be 'calendar' or 'business', got {unit!r}")
            start = base - timedelta(days=1) if dl.get("count_base_day") else base
            base_label = "Effective Date" if base_id == "effective" else base_id
            if "before" in dl:
                if unit == "business":
                    d, k = base, 0
                    while k < n:
                        d -= timedelta(days=1)
                        if cal.business(d):
                            k += 1
                else:
                    d = base - timedelta(days=n)
                steps.append(f"{base_label} {ds(base)} - {n} {unit} days = {ds(d)}")
                if not cal.business(d):
                    flags.append(f"lands on {cal.why_not(d)}; contract may intend the prior business day")
            elif unit == "business":
                d, k, skipped = start, 0, []
                while k < n:
                    d += timedelta(days=1)
                    if cal.business(d):
                        k += 1
                    elif cal.holiday(d):
                        skipped.append(f"{d.isoformat()} {cal.holiday(d)}")
                steps.append(f"{base_label} {ds(base)} + {n} business days = {ds(d)}")
                if skipped:
                    steps.append("skipped holiday: " + ", ".join(skipped))
            else:
                d = start + timedelta(days=n)
                steps.append(f"{base_label} {ds(base)} + {n} calendar days = {ds(d)}")
                if not cal.business(d):
                    if rollover:
                        why = cal.why_not(d)
                        while not cal.business(d):
                            d += timedelta(days=1)
                        steps.append(f"falls on {why}; rolls to next business day {ds(d)}")
                    else:
                        flags.append(f"falls on {cal.why_not(d)}; contract has no rollover clause")
        known[dl.get("id", dl["name"])] = d
        out.append({**dl, "due": d, "working": "; ".join(steps), "flags": flags})
    if pending:
        sys.exit("could not resolve base for: " + ", ".join(p.get("id", p["name"]) for p in pending))
    closing = next((o["due"] for o in out if o.get("id") == "closing"), None)
    for o in out:
        if closing and o["due"] > closing and o.get("id") != "closing":
            o["flags"].append("after the closing date")
    out.sort(key=lambda o: o["due"])
    return eff, out


def ics_escape(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    b = line.encode()
    if len(b) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        e = ch.encode()
        if len(cur) + len(e) > (75 if not parts else 74):
            parts.append(cur.decode())
            cur = b""
        cur += e
    parts.append(cur.decode())
    return "\r\n ".join(parts)


def write_ics(path, prop, items, time_note):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Listing Desk//contract-timeline//EN",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    slug = "".join(c for c in prop.lower() if c.isalnum())[:24] or "contract"
    for o in items:
        d = o["due"]
        uid = f"{slug}-{o.get('id', o['name']).replace(' ', '-').lower()}-{d.strftime('%Y%m%d')}@listing-desk"
        desc = (f"{o['name']} ({o.get('source', '')}). Due {time_note}. Working: {o['working']}. "
                + (("Flags: " + "; ".join(o["flags"]) + ". ") if o["flags"] else "")
                + "VERIFY against the executed contract with your broker, TC or attorney.")
        L += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
              f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
              f"DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime('%Y%m%d')}",
              fold("SUMMARY:" + ics_escape(f"[VERIFY] {o['name']} - {prop}")),
              fold("DESCRIPTION:" + ics_escape(desc)),
              "TRANSP:TRANSPARENT",
              "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT15H",
              fold("DESCRIPTION:" + ics_escape(f"Tomorrow: {o['name']}")), "END:VALARM",
              "END:VEVENT"]
    L.append("END:VCALENDAR")
    Path(path).write_text("\r\n".join(L) + "\r\n", newline="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("terms")
    ap.add_argument("--out")
    ap.add_argument("--ics")
    ap.add_argument("--extra-holidays", default="")
    a = ap.parse_args()
    t = json.loads(Path(a.terms).read_text())
    extra = [pd(x) for x in (a.extra_holidays.split(",") if a.extra_holidays else []) + t.get("extra_holidays", [])]
    cal = Cal(extra)
    eff, items = compute(t, cal)
    prop = t.get("property", "")
    time_note = t.get("deadline_time", "time per contract")

    L = [f"# Contract timeline: {prop}", "",
         "**Every date below is a checklist to VERIFY against the executed contract "
         "with your broker, transaction coordinator or attorney. Not legal advice.**", "",
         f"Effective Date: {ds(eff)}. Deadlines end: {time_note}. "
         f"Weekend/holiday rollover clause: {'yes' if t.get('rollover', True) else 'no'}.", ""]
    if t.get("terms"):
        L += ["## Key terms", "", "| Term | Value | Where in contract |", "|---|---|---|"]
        L += [f"| {a_} | {b} | {c} |" for a_, b, c in t["terms"]]
        L.append("")
    L += ["## Deadlines", "", "| # | Due | Deadline | Who | Rule | Working | Flags |", "|---|---|---|---|---|---|---|"]
    for n, o in enumerate(items, 1):
        rule = ("fixed date" if "date" in o else
                f"{o['days']} {o.get('unit', 'calendar')} days {'before' if 'before' in o else 'after'} "
                f"{o.get('before') or o.get('from')}")
        L.append(f"| {n} | {ds(o['due'])} | {o['name']} ({o.get('source', '')}) | {o.get('owner', '')} | {rule} | "
                 f"{o['working']} | {'VERIFY: ' + '; '.join(o['flags']) if o['flags'] else ''} |")
    hol = sorted({d for d in (eff + timedelta(days=i) for i in range((items[-1]['due'] - eff).days + 1)) if cal.holiday(d)})
    L += ["", "Holidays inside this timeline: " + (", ".join(f"{ds(d)} {cal.holiday(d)}" for d in hol) or "none") + ".",
          "Federal holidays only (5 USC 6103, observed dates). Add state/local holidays if your contract counts them.", "",
          "## Checklist", ""]
    for o in items:
        L.append(f"- [ ] {o['due'].isoformat()} -- {o['name']}{' (' + o['owner'] + ')' if o.get('owner') else ''}")
    L.append("")
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    if a.ics:
        write_ics(a.ics, prop, items, time_note)
        text += f"\nCalendar file written: {a.ics} ({len(items)} all-day events, reminder 9 a.m. the day before).\n"
    print(text)


if __name__ == "__main__":
    main()
