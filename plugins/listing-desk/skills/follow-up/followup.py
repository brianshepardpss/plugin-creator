#!/usr/bin/env python3
"""Open-house / lead follow-up planner. Standard library only.

Usage:
  python3 followup.py signins.csv [--event-date 2026-09-27] [--property "26 Larkspur Dr"]
                      [--out plan.md] [--json-out plan.json]

What it does (deterministic, so the plan is the same every run):
  1. Maps headers loosely (Name, Email, Phone, Has Agent, Timeline,
     Consent To Text, Notes, Visit Date). Drops blank rows and duplicates
     (same email, or same phone when there is no email), listing each.
  2. Segments each person:
       represented-buyer  Has Agent = Y            -> 1 courtesy thank-you, no solicitation
       hot-buyer          timeline 0-3 months      -> touches on day 0, 2, 7
       warm-buyer         timeline 3-12 months     -> touches on day 1, 7, 30
       neighbor-or-looking "just looking"/neighbor -> touches on day 1, 14, 45
       unknown            anything else            -> touches on day 1, 7, 30
  3. Channels allowed per person: email if an email exists; text ONLY if
     Consent To Text = Y and a phone exists. Nothing is ever sent: the skill
     writes drafts for the agent to review and send.
  4. Touch date = event date + day offset (calendar days).
"""
import argparse
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ALIASES = {
    "name": ["name", "full name", "visitor", "guest", "contact"],
    "first": ["first name", "first"],
    "last": ["last name", "last"],
    "email": ["email", "e-mail", "email address"],
    "phone": ["phone", "mobile", "cell", "phone number", "mobile phone"],
    "has_agent": ["has agent", "working with agent", "agent", "has an agent", "represented",
                  "are you working with an agent"],
    "timeline": ["timeline", "time frame", "timeframe", "when buying", "buying timeline", "moving"],
    "consent_text": ["consent to text", "text ok", "sms consent", "ok to text", "consent_to_text", "text opt in"],
    "notes": ["notes", "comments", "note"],
    "date": ["visit date", "date", "event date", "signed in"],
}
PLANS = {
    "represented-buyer": [(0, "courtesy thank-you only; do not solicit; offer to send info through their agent")],
    "hot-buyer": [(0, "thank-you + the one thing they asked about"), (2, "matching listings or answer + offer a tour"),
                  (7, "check-in; offer buyer consultation")],
    "warm-buyer": [(1, "thank-you + offer a saved search"), (7, "useful resource (process overview, financing steps)"),
                   (30, "market update + check-in on timeline")],
    "neighbor-or-looking": [(1, "thank-you + offer a free home value review"), (14, "neighborhood sales recap (facts only)"),
                            (45, "seasonal check-in")],
    "unknown": [(1, "thank-you"), (7, "helpful resource"), (30, "check-in")],
}


def norm(s):
    return re.sub(r"[^a-z0-9]", " ", (s or "").lower()).strip()


def mapcols(headers):
    out = {}
    for key, al in ALIASES.items():
        for h in headers:
            if norm(h) in [norm(x) for x in al] and key not in out:
                out[key] = h
    return out


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    raise SystemExit(f"unreadable event date {s!r}; pass --event-date YYYY-MM-DD")


def yes(v):
    return norm(v) in {"y", "yes", "true", "1", "x"}


def segment(r):
    if yes(r.get("has_agent")):
        return "represented-buyer"
    t = norm(r.get("timeline"))
    if re.search(r"\b0 ?3\b|asap|\bnow\b|immediately|1 3|30 days", t):
        return "hot-buyer"
    if re.search(r"\b3 6\b|\b6 12\b|months|year", t):
        return "warm-buyer"
    if re.search(r"looking|neighbor|curious|browsing", t + " " + norm(r.get("notes"))):
        return "neighbor-or-looking"
    return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--event-date")
    ap.add_argument("--property", default="")
    ap.add_argument("--out")
    ap.add_argument("--json-out")
    a = ap.parse_args()
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        cols = mapcols(rd.fieldnames or [])
        raw = list(rd)
    people, dropped, seen = [], [], {}
    for i, row in enumerate(raw, start=2):
        r = {k: (row.get(h) or "").strip() for k, h in cols.items()}
        if not r.get("name") and (r.get("first") or r.get("last")):
            r["name"] = f"{r.get('first', '')} {r.get('last', '')}".strip()
        if not any(r.values()):
            dropped.append((i, "blank row"))
            continue
        key = r.get("email", "").lower() or re.sub(r"\D", "", r.get("phone", ""))
        if not key:
            dropped.append((i, f"{r.get('name') or 'no name'}: no email or phone"))
            continue
        if key in seen:
            dropped.append((i, f"{r.get('name')}: duplicate of line {seen[key]}"))
            continue
        seen[key] = i
        r["_line"] = i
        people.append(r)

    ev = a.event_date or next((p.get("date") for p in people if p.get("date")), None)
    ev = parse_date(ev) if ev else None
    plan = []
    for p in people:
        seg = segment(p)
        ch = []
        if p.get("email"):
            ch.append("email")
        if p.get("phone") and yes(p.get("consent_text")):
            ch.append("text")
        touches = []
        for n, (off, purpose) in enumerate(PLANS[seg], 1):
            d = (ev + timedelta(days=off)).isoformat() if ev else f"day {off}"
            touches.append({"touch": n, "date": d, "day": off, "purpose": purpose})
        plan.append({"name": p.get("name"), "line": p["_line"], "segment": seg, "channels": ch,
                     "text_blocked": bool(p.get("phone")) and not yes(p.get("consent_text")),
                     "timeline": p.get("timeline"), "notes": p.get("notes"), "touches": touches,
                     "buyer_agreement_reminder": seg in ("hot-buyer", "warm-buyer", "unknown")})

    L = [f"# Follow-up plan{': ' + a.property if a.property else ''}", "",
         f"Event date: {ev or 'unknown (dates shown as day offsets)'}. People: {len(plan)}. Rows skipped: {len(dropped)}.", ""]
    if dropped:
        L += ["| CSV line | Skipped because |", "|---|---|"] + [f"| {l} | {w} |" for l, w in dropped] + [""]
    L += ["| Name | Segment | Channels allowed | Touches (date: purpose) | Notes |", "|---|---|---|---|---|"]
    for p in plan:
        ch = ", ".join(p["channels"]) or "none (call or mail only)"
        if p["text_blocked"]:
            ch += " (no text: no consent)"
        t = "<br>".join(f"{x['date']}: {x['purpose']}" for x in p["touches"])
        L.append(f"| {p['name']} | {p['segment']} | {ch} | {t} | {p['notes'] or ''} |")
    counts = {}
    for p in plan:
        counts[p["segment"]] = counts.get(p["segment"], 0) + 1
    L += ["", "Segments: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ".",
          f"Drafts to write: {sum(len(p['touches']) * max(1, len(p['channels'])) for p in plan)} "
          "(touches x allowed channels). Nothing is sent automatically.", ""]
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps({"event_date": str(ev), "plan": plan, "skipped": dropped}, indent=2))
    print(text)


if __name__ == "__main__":
    main()
