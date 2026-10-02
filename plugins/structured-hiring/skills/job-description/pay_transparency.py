#!/usr/bin/env python3
"""Which pay-transparency posting laws apply to a job, and does a JD meet them?

Usage:
  python3 pay_transparency.py --location "Denver, CO" [--location "Remote (US)"]
        [--employees N] [--as-of YYYY-MM-DD] [--jd jd.md] [--json]

Matching: a law applies when any of its `match` strings appears in a
location as a whole word (case-insensitive; two-letter codes must match a
state code exactly, e.g. "Denver, CO"). A location containing "remote"
with a US scope lists every law in force, because most laws cover remote
jobs that could be performed in that jurisdiction. Laws whose effective
date is after --as-of are listed as "upcoming". --employees filters out
laws whose min_employees is higher (omit it if unsure; the law is kept).

--jd checks the text for: a pay range (two money amounts joined by a dash,
"to" or "-"), a benefits mention, and an application deadline. It reports
which required items look missing for each applicable law.

Data: pay_laws.json beside this script (last_reviewed date inside). This is
a drafting aid, not legal advice.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent / "pay_laws.json").read_text())
MONEY = r"(?:[$\u00a3\u20ac]|USD|CAD)\s?\d[\d,]*(?:\.\d+)?\s?[kK]?"
RANGE = re.compile(MONEY + r"\s*(?:-|to|--|\u2013)\s*" + MONEY + r"|" + r"\d[\d,]*\s?[kK]?\s*(?:-|to)\s*\d[\d,]*\s?[kK]?\s*(?:USD|per year|/yr|/year|a year|per hour|/hr|/hour)", re.I)
BENEFITS = re.compile(r"\b(benefits?|medical|dental|vision|401\s?\(?k\)?|pto|paid time off|health insurance|pension|equity)\b", re.I)
DEADLINE = re.compile(r"\b(apply by|applications? (close|due|accepted until|deadline|window)|deadline|closing date|open until)\b", re.I)


def applies(law, loc):
    l = loc.strip()
    for m in law["match"]:
        if len(m) == 2 and m.isupper():
            if re.search(r"(^|[,\s(])" + m + r"($|[\s,)])", l):
                return True
        elif re.search(r"\b" + re.escape(m) + r"\b", l, re.I):
            return True
    return False


def check(locations, employees=None, as_of=None, jd=None):
    as_of = as_of or dt.date.today()
    remote = any(re.search(r"\bremote\b", l, re.I) and not re.search(r"\b(EU|UK|Canada|Europe)\b", l) for l in locations)
    now, upcoming = [], []
    for law in DATA["laws"]:
        hit = [l for l in locations if applies(law, l)]
        if not hit and not (remote and law["id"] not in ("ON", "BC")):
            continue
        if employees is not None and employees < law["min_employees"]:
            continue
        eff = dt.date.fromisoformat(law["effective"])
        item = {**law, "why": ("location " + ", ".join(hit)) if hit else "remote role could be performed there"}
        (now if eff <= as_of else upcoming).append(item)
    jd_check = None
    if jd is not None:
        jd_check = {"pay_range": bool(RANGE.search(jd)), "benefits": bool(BENEFITS.search(jd)),
                    "application_deadline": bool(DEADLINE.search(jd))}
    gaps = []
    if jd_check:
        for law in now:
            req = " ".join(law["requires"]).lower()
            miss = []
            if ("range" in req or "scale" in req or "pay" in req or "wage" in req) and not jd_check["pay_range"]:
                miss.append("pay range")
            if "benefit" in req and not jd_check["benefits"]:
                miss.append("benefits description")
            if "deadline" in req and not jd_check["application_deadline"]:
                miss.append("application deadline")
            if miss:
                gaps.append({"law": law["id"], "missing": miss})
    return {"as_of": as_of.isoformat(), "last_reviewed": DATA["last_reviewed"], "in_force": now,
            "upcoming": upcoming, "jd_check": jd_check, "gaps": gaps}


def render(r):
    L = [f"Pay-transparency check as of {r['as_of']} (law data last reviewed {r['last_reviewed']}; not legal advice).", ""]
    if not r["in_force"] and not r["upcoming"]:
        L.append("No posting-range law in our list matched these locations. Posting a range is still best practice.")
    for law in r["in_force"]:
        L.append(f"- {law['id']} -- {law['name']} (in force since {law['effective']}, {law['min_employees']}+ employees; "
                 f"{law['why']}). Requires: {'; '.join(law['requires'])}. Remote: {law['remote']}")
    for law in r["upcoming"]:
        L.append(f"- UPCOMING {law['id']} -- {law['name']} (from {law['effective']}). Requires: {'; '.join(law['requires'])}.")
    if r["jd_check"] is not None:
        j = r["jd_check"]
        L += ["", f"JD contains: pay range {'yes' if j['pay_range'] else 'NO'}; benefits {'yes' if j['benefits'] else 'NO'}; "
              f"application deadline {'yes' if j['application_deadline'] else 'NO'}."]
        for g in r["gaps"]:
            L.append(f"- {g['law']}: missing {', '.join(g['missing'])}")
    return "\n".join(L)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    locs = [a[i + 1] for i, x in enumerate(a) if x == "--location"]
    if not locs:
        sys.exit("Pass at least one --location")
    emp = int(a[a.index("--employees") + 1]) if "--employees" in a else None
    as_of = dt.date.fromisoformat(a[a.index("--as-of") + 1]) if "--as-of" in a else None
    jd = Path(a[a.index("--jd") + 1]).read_text(encoding="utf-8") if "--jd" in a else None
    r = check(locs, emp, as_of, jd)
    print(json.dumps(r, indent=2) if "--json" in a else render(r))


if __name__ == "__main__":
    main()
