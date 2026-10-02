#!/usr/bin/env python3
"""DealTender: exact pipeline math for Pipedrive deal data. Standard library only.

Every number DealTender shows (days stale, scores, weighted totals, dates)
comes from this script, so it can be audited.

Usage (DEALS is a Pipedrive deals CSV export, or the word `sample`):
  dealtender.py load     DEALS [--map map.json] [--write normalized.csv]
  dealtender.py triage   DEALS [--top N] [--json]
  dealtender.py forecast DEALS [--prev PREV.csv] [--period 2026Q4|2026-10|YYYY-MM-DD:YYYY-MM-DD] [--json]
  dealtender.py match    DEALS [--person NAME] [--org NAME] [--email ADDR] [--keywords "w1 w2"]
  dealtender.py prep     DEALS QUERY [--limit 5]
  dealtender.py diff     DEALS --changes changes.json
  dealtender.py date     [--add-days N | --add-business-days N | --weekday friday]
Common options: --stages stages.json --settings settings.json --today YYYY-MM-DD
                --persons persons.csv --activities activities.csv

Definitions (also printed with the output):
  last touch      = Last activity date, else Last stage change, else Deal created.
  days idle       = today - last touch, in calendar days.
  threshold       = the stage's rotting days from stages.json, else settings
                    stale_days (default 14).
  STALE           = open deal, days idle >= threshold, and no next activity on
                    or after today (none scheduled, or only overdue ones).
  PAST CLOSE      = open deal whose expected close date is before today.
  WATCH           = open deal, not stale or past close, with no next activity
                    on or after today.
  priority score  = value in base currency x (days idle + days past close) / 1000.
                    Value converts with settings fx_to_base (user-entered rates);
                    a currency with no rate is scored 1:1 and marked "nofx".
  probability     = Deal - Probability column if filled, else the stage's
                    probability from stages.json.
  weighted        = sum(value x probability / 100) over open deals whose
                    expected close date falls in the period, per currency.
  best case       = sum(value) over the same deals.
  commit          = sum(value) over those deals with probability >=
                    settings commit_probability (default 80).
  slipped         = open deals whose expected close date is before today.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = (HERE.parent / "samples").resolve()

ALIASES = {
    "id": ["id", "deal id"],
    "title": ["title", "deal title", "name", "deal name"],
    "value": ["value", "deal value", "amount"],
    "currency": ["currency", "currency of value", "deal currency"],
    "pipeline": ["pipeline", "pipeline name"],
    "stage": ["stage", "stage name", "deal stage"],
    "status": ["status", "deal status"],
    "owner": ["owner", "deal owner", "owner name", "user"],
    "org": ["organization", "organisation", "organization name", "org", "company"],
    "person": ["contact person", "person", "contact", "person name"],
    "probability": ["probability", "deal probability", "win probability"],
    "close": ["expected close date", "close date", "expected close"],
    "created": ["deal created", "add time", "created", "created at"],
    "stage_change": ["last stage change", "stage change time", "stage changed"],
    "last_activity": ["last activity date", "last activity"],
    "next_activity": ["next activity date", "next activity"],
    "update_time": ["update time", "last updated", "updated"],
    "won_time": ["won time", "won date"],
    "lost_reason": ["lost reason"],
}
REQUIRED = ["id", "title", "value", "stage", "status"]
DOW = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# ---------- parsing helpers ----------

def norm_header(h):
    h = (h or "").strip().lower().lstrip("\ufeff")
    h = re.sub(r"^deal\s*-\s*", "", h)
    return re.sub(r"\s+", " ", h)


AMBIGUOUS = []  # (value, assumed) for slash dates that could be M/D or D/M


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})(?:\s.*)?", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if a > 12:
            return dt.date(y, b, a)          # D/M/Y
        if b <= 12 and a != b:
            AMBIGUOUS.append(s)              # assume US M/D/Y, report it
        return dt.date(y, a, b)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
                "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(s[:19] if "T" in s or " " in s else s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date {s!r}")


def parse_num(s):
    s = re.sub(r"[^\d,.\-]", "", (s or "").strip())
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        parts = s.split(",")
        s = s.replace(",", "") if len(parts[-1]) == 3 else s.replace(",", ".")
    elif s.count(".") > 1 or re.fullmatch(r"-?\d{1,3}\.\d{3}", s):
        NUM_GUESSES.append(s)                # "48.000" read as 48000 (European thousands)
        s = s.replace(".", "")
    return float(s)


NUM_GUESSES = []


def money(x):
    return f"{x:,.2f}"


def load_json(p):
    return json.loads(Path(p).read_text()) if p and Path(p).exists() else {}


# ---------- context ----------

class Ctx:
    def __init__(self, a):
        deals = a.deals
        self.is_sample = deals == "sample"
        self.deals_path = (SAMPLES / "deals_export.csv") if self.is_sample else Path(deals)
        if not self.deals_path.exists():
            sys.exit(f"error: {self.deals_path} not found")
        base = self.deals_path.resolve().parent
        self.is_sample = self.is_sample or base == SAMPLES
        cwd = Path.cwd()

        def pick(explicit, *cands):
            if explicit:
                return Path(explicit)
            for c in cands:
                if c and Path(c).exists():
                    return Path(c)
            return None

        self.settings_path = pick(getattr(a, "settings", None),
                                  (base / "settings.json") if base == SAMPLES else None,
                                  base / "dealtender-settings.json", cwd / "dealtender-settings.json")
        self.settings = load_json(self.settings_path)
        self.stages_path = pick(getattr(a, "stages", None), self.settings.get("stages_file"),
                                base / "stages.json", cwd / "stages.json")
        self.stages = load_json(self.stages_path)
        self.persons_path = pick(getattr(a, "persons", None), base / "persons.csv")
        self.activities_path = pick(getattr(a, "activities", None), base / "activities.csv")
        t = getattr(a, "today", None) or self.settings.get("as_of")
        self.today = parse_date(t) if t else dt.date.today()
        self.stale_days = int(self.settings.get("stale_days", 14))
        self.commit_p = float(self.settings.get("commit_probability", 80))
        self.base_cur = self.settings.get("base_currency")
        self.fx = {k.upper(): float(v) for k, v in self.settings.get("fx_to_base", {}).items()}
        self.stage_info = {}
        for p in self.stages.get("pipelines", []):
            for s in p.get("stages", []):
                self.stage_info[(p["name"].lower(), s["name"].lower())] = dict(s, pipeline=p["name"])
        extra_map = load_json(getattr(a, "map", None))
        self.deals, self.report = read_deals(self.deals_path, extra_map, self.settings.get("field_map", {}))

    def stage(self, d):
        return self.stage_info.get(((d["pipeline"] or "").lower(), (d["stage"] or "").lower()))

    def prob(self, d):
        if d["probability"] is not None:
            return d["probability"], "deal"
        s = self.stage(d)
        if s and s.get("probability") is not None:
            return float(s["probability"]), "stage"
        return None, "none"

    def threshold(self, d):
        s = self.stage(d)
        if s and s.get("rotten_days"):
            return int(s["rotten_days"]), "stage"
        return self.stale_days, "default"

    def to_base(self, value, cur):
        if not self.base_cur:
            return value, len({d["currency"] for d in self.deals}) <= 1
        if cur == self.base_cur:
            return value, True
        if cur in self.fx:
            return value * self.fx[cur], True
        return value, False

    def header(self, title):
        return (f"DealTender {title} - as of {self.today.isoformat()} ({self.today.strftime('%A')})\n"
                f"Source: {self.deals_path.name}{' (bundled sample, fictional)' if self.is_sample else ''}")


def read_deals(path, extra_map, field_map):
    del AMBIGUOUS[:], NUM_GUESSES[:]
    rows = list(csv.reader(path.open(newline="", encoding="utf-8-sig")))
    if not rows:
        sys.exit("error: empty CSV")
    headers = rows[0]
    lookup = {}
    for canon, al in ALIASES.items():
        for a in al:
            lookup[a] = canon
    extra_map = dict(extra_map or {})
    status_map = {k.lower(): v.lower() for k, v in extra_map.pop("status_values", {}).items()}
    for k, v in extra_map.items():
        lookup[norm_header(k)] = v
    colmap, unmapped, hashcols = {}, [], []
    for i, h in enumerate(headers):
        n = norm_header(h)
        if n in lookup and lookup[n] in ALIASES and lookup[n] not in colmap:
            colmap[lookup[n]] = i
        elif re.fullmatch(r"[0-9a-f]{40}", n):
            hashcols.append((h, field_map.get(h)))
        else:
            unmapped.append(h)
    missing = [k for k in REQUIRED if k not in colmap]
    rep = {"headers": len(headers), "mapped": {k: headers[i] for k, i in colmap.items()},
           "unmapped": unmapped, "hash_columns": hashcols, "missing_required": missing,
           "blank_rows": 0, "warnings": [], "rows": 0}
    if missing:
        return [], rep
    deals = []
    for ln, r in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in r):
            rep["blank_rows"] += 1
            continue
        g = lambda k: (r[colmap[k]].strip() if k in colmap and colmap[k] < len(r) else "")
        d = {"line": ln}
        for k in ALIASES:
            d[k] = g(k)
        try:
            d["value"] = parse_num(d["value"]) or 0.0
        except ValueError:
            rep["warnings"].append(f"line {ln}: value {d['value']!r} unreadable, using 0")
            d["value"] = 0.0
        try:
            d["probability"] = parse_num(d["probability"])
        except ValueError:
            d["probability"] = None
        for k in ("close", "created", "stage_change", "last_activity", "next_activity", "update_time", "won_time"):
            try:
                d[k] = parse_date(d[k])
            except ValueError as e:
                rep["warnings"].append(f"line {ln}: {k} {e}")
                d[k] = None
        d["status"] = (d["status"] or "open").strip().lower()
        d["status"] = status_map.get(d["status"], d["status"])
        if d["status"] not in ("open", "won", "lost"):
            rep["warnings"].append(f"line {ln}: status {d['status']!r} is not open/won/lost; "
                                   "add it to \"status_values\" in map.json")
        d["currency"] = (d["currency"] or "").upper() or "?"
        try:
            d["id"] = int(float(d["id"]))
        except ValueError:
            pass
        deals.append(d)
    rep["rows"] = len(deals)
    if AMBIGUOUS:
        rep["warnings"].append(f"{len(AMBIGUOUS)} dates like {AMBIGUOUS[0]!r} could be month/day or day/month; "
                               "read as month/day (US). If your Pipedrive uses day/month, re-export with ISO dates.")
    if NUM_GUESSES:
        rep["warnings"].append(f"{len(NUM_GUESSES)} values like {NUM_GUESSES[0]!r} read with '.' as thousands separator")
    return deals, rep


# ---------- analyses ----------

def data_note(ctx):
    """Print parse warnings so a bad export never fails silently."""
    w = ctx.report["warnings"]
    nodate = [d["id"] for d in ctx.deals if d["status"] == "open"
              and not (d["last_activity"] or d["stage_change"] or d["created"])]
    if w:
        print(f"DATA WARNINGS ({len(w)}): " + " | ".join(w[:5]) + (" | ..." if len(w) > 5 else "")
              + "  -> run `load` for the full list; results below may be incomplete.")
    if nodate:
        print(f"Open deals with no activity, stage-change or created date (cannot judge staleness): {nodate}")

def assess(ctx, d):
    t = ctx.today
    touch = d["last_activity"] or d["stage_change"] or d["created"]
    touch_src = "activity" if d["last_activity"] else ("stage change" if d["stage_change"] else "created")
    idle = (t - touch).days if touch else None
    thr, thr_src = ctx.threshold(d)
    has_next = d["next_activity"] is not None and d["next_activity"] >= t
    overdue = d["next_activity"] is not None and d["next_activity"] < t
    past = (t - d["close"]).days if d["close"] and d["close"] < t else 0
    flags, reasons = [], []
    if idle is not None and idle >= thr and not has_next:
        flags.append("STALE")
        why = f"no activity for {idle} days (threshold {thr}, {thr_src})"
        why += f"; next activity overdue since {d['next_activity'].isoformat()}" if overdue else "; nothing scheduled"
        reasons.append(why)
    if past:
        flags.append("PAST CLOSE")
        reasons.append(f"expected close {d['close'].isoformat()} passed {past} days ago")
    watch = not flags and not has_next
    base, ok = ctx.to_base(d["value"], d["currency"])
    score = base * ((idle or 0) + past) / 1000.0
    return {"id": d["id"], "title": d["title"], "org": d["org"], "person": d["person"],
            "owner": d["owner"], "pipeline": d["pipeline"], "stage": d["stage"],
            "value": d["value"], "currency": d["currency"], "value_base": round(base, 2), "fx_ok": ok,
            "last_touch": touch.isoformat() if touch else None, "touch_source": touch_src,
            "days_idle": idle, "threshold": thr,
            "next_activity": d["next_activity"].isoformat() if d["next_activity"] else None,
            "next_overdue": overdue, "close": d["close"].isoformat() if d["close"] else None,
            "days_past_close": past, "flags": flags, "reasons": reasons, "watch": watch,
            "score": round(score, 1)}


def hygiene(ctx):
    open_ = [d for d in ctx.deals if d["status"] == "open"]
    seen, dups = {}, []
    for d in open_:
        key = (re.sub(r"\W+", " ", d["title"].lower()).strip(), d["org"].lower())
        if key in seen:
            dups.append((seen[key], d["id"], d["title"]))
        else:
            seen[key] = d["id"]
    return {
        "possible_duplicates": dups,
        "missing_close_date": [d["id"] for d in open_ if not d["close"]],
        "zero_value": [d["id"] for d in open_ if not d["value"]],
        "unknown_stage": sorted({f"{d['pipeline']} / {d['stage']}" for d in open_ if ctx.stage_info and not ctx.stage(d)}),
        "no_probability": [d["id"] for d in open_ if ctx.prob(d)[0] is None],
    }


def cmd_load(ctx, a):
    r = ctx.report
    print(ctx.header("load check"))
    print(f"Columns: {r['headers']}  |  deal rows: {r['rows']}  |  blank rows skipped: {r['blank_rows']}")
    if r["missing_required"]:
        print("MISSING REQUIRED COLUMNS: " + ", ".join(r["missing_required"]))
        print("Fix: pass --map map.json mapping your header text to one of: " + ", ".join(ALIASES))
        sys.exit(2)
    print("Mapped: " + "; ".join(f"{k} <- '{v}'" for k, v in r["mapped"].items()))
    if r["hash_columns"]:
        for h, label in r["hash_columns"]:
            print(f"Custom field (hash key) {h}: " + (f"labelled '{label}' via settings field_map" if label
                  else "UNLABELLED - look it up in Pipedrive (Settings > Data fields) or the connector's deal fields"))
    if r["unmapped"]:
        print("Ignored columns: " + ", ".join(r["unmapped"]))
    for w in r["warnings"]:
        print("Warning: " + w)
    by = {}
    for d in ctx.deals:
        by.setdefault(d["status"], 0)
        by[d["status"]] += 1
    print("Status counts: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    curs = sorted({d["currency"] for d in ctx.deals})
    print("Currencies: " + ", ".join(curs) + (f"  (base {ctx.base_cur}; fx for "
          + ", ".join(sorted(ctx.fx)) + ")" if ctx.base_cur else "  (no base currency set)"))
    print(f"Stages file: {ctx.stages_path.name if ctx.stages_path else 'none - stage probabilities and rotting days unknown, defaults apply'}"
          f"  |  settings: {ctx.settings_path.name if ctx.settings_path else 'none (defaults)'}")
    h = hygiene(ctx)
    print("\nHygiene")
    print(f"  Possible duplicates: " + ("; ".join(f"{x} and {y} ({t})" for x, y, t in h["possible_duplicates"]) or "none"))
    print(f"  Open deals missing close date: {h['missing_close_date'] or 'none'}")
    print(f"  Open deals with zero value: {h['zero_value'] or 'none'}")
    print(f"  Stages not in stages file: {h['unknown_stage'] or 'none'}")
    print(f"  Open deals with no probability: {h['no_probability'] or 'none'}")
    if a.write:
        keys = ["id", "title", "value", "currency", "pipeline", "stage", "status", "owner", "org", "person",
                "probability", "close", "created", "stage_change", "last_activity", "next_activity"]
        with open(a.write, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(keys)
            for d in ctx.deals:
                w.writerow(["" if d[k] is None else (d[k].isoformat() if hasattr(d[k], "isoformat") else d[k]) for k in keys])
        print(f"\nWrote normalized CSV: {a.write}")


def cmd_triage(ctx, a):
    rows = [assess(ctx, d) for d in ctx.deals if d["status"] == "open"]
    flagged = sorted([r for r in rows if r["flags"]], key=lambda r: (-r["score"], str(r["id"])))
    watch = sorted([r for r in rows if r["watch"]], key=lambda r: -r["value_base"])
    n_st = sum("STALE" in r["flags"] for r in flagged)
    n_pc = sum("PAST CLOSE" in r["flags"] for r in flagged)
    n_both = sum(len(r["flags"]) == 2 for r in flagged)
    if a.json:
        print(json.dumps({"as_of": ctx.today.isoformat(), "open": len(rows), "stale": n_st, "past_close": n_pc,
                          "both": n_both, "flagged": flagged, "watch": watch, "hygiene": hygiene(ctx)}, indent=2))
        return
    print(ctx.header("pipeline triage"))
    data_note(ctx)
    print(f"Open deals: {len(rows)} | needs attention: {len(flagged)} (stale {n_st}, past close {n_pc}, both {n_both}) | watch: {len(watch)}")
    print(f"Score = value in {ctx.base_cur or 'deal currency'} x (days idle + days past close) / 1000")
    print()
    print("Rank | ID | Deal | Stage | Value | Last touch (days idle) | Next activity | Close | Flags | Score")
    shown = flagged[: a.top] if a.top else flagged
    for k, r in enumerate(shown, 1):
        nxt = r["next_activity"] or "none"
        if r["next_overdue"]:
            nxt += " OVERDUE"
        val = f"{money(r['value'])} {r['currency']}" + ("" if r["fx_ok"] else " nofx")
        print(f"{k} | {r['id']} | {r['title']} | {r['pipeline']} / {r['stage']} | {val} | "
              f"{r['last_touch']} ({r['days_idle']}d) | {nxt} | {r['close']} | {', '.join(r['flags'])} | {r['score']}")
    print("\nReasons")
    for r in shown:
        print(f"  {r['id']}: " + "; ".join(r["reasons"]))
    print("\nWatch list (recent touch but no next activity scheduled)")
    for r in watch:
        print(f"  {r['id']} | {r['title']} | {r['stage']} | {money(r['value'])} {r['currency']} | last touch {r['last_touch']} ({r['days_idle']}d)")
    if not watch:
        print("  none")
    h = hygiene(ctx)
    if h["possible_duplicates"]:
        print("\nPossible duplicates: " + "; ".join(f"{x} and {y} ({t})" for x, y, t in h["possible_duplicates"]))
    print("\nRules: STALE = no activity for >= the stage's rotting days (else default "
          f"{ctx.stale_days}) and no upcoming activity. PAST CLOSE = expected close date before today.")


def period_of(spec, today):
    if not spec:
        q = (today.month - 1) // 3
        start = dt.date(today.year, 3 * q + 1, 1)
        end = dt.date(today.year + (q == 3), (3 * q + 3) % 12 + 1, 1) - dt.timedelta(days=1)
        return start, end, f"{today.year} Q{q + 1}"
    m = re.fullmatch(r"(\d{4})Q([1-4])", spec.upper())
    if m:
        y, q = int(m.group(1)), int(m.group(2)) - 1
        start = dt.date(y, 3 * q + 1, 1)
        end = dt.date(y + (q == 3), (3 * q + 3) % 12 + 1, 1) - dt.timedelta(days=1)
        return start, end, f"{y} Q{q + 1}"
    m = re.fullmatch(r"(\d{4})-(\d{2})", spec)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        end = dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
        return dt.date(y, mo, 1), end, spec
    s, e = spec.split(":")
    return parse_date(s), parse_date(e), spec


def cmd_forecast(ctx, a):
    start, end, label = period_of(a.period, ctx.today)
    open_ = [d for d in ctx.deals if d["status"] == "open"]
    inp = [d for d in open_ if d["close"] and start <= d["close"] <= end and d["close"] >= ctx.today]
    slipped = [d for d in open_ if d["close"] and d["close"] < ctx.today]
    later = [d for d in open_ if d["close"] and d["close"] > end]
    won = [d for d in ctx.deals if d["status"] == "won" and d["won_time"] and start <= d["won_time"] <= end]
    curs = sorted({d["currency"] for d in inp + won + slipped})
    table, noprob = {}, []
    for c in curs:
        t = {"deals": 0, "best_case": 0.0, "weighted": 0.0, "commit": 0.0, "commit_deals": 0, "won": 0.0, "won_deals": 0}
        for d in inp:
            if d["currency"] != c:
                continue
            p, _ = ctx.prob(d)
            t["deals"] += 1
            t["best_case"] += d["value"]
            if p is None:
                noprob.append(d["id"])
                continue
            t["weighted"] += d["value"] * p / 100
            if p >= ctx.commit_p:
                t["commit"] += d["value"]
                t["commit_deals"] += 1
        for d in won:
            if d["currency"] == c:
                t["won"] += d["value"]
                t["won_deals"] += 1
        table[c] = {k: round(v, 2) if isinstance(v, float) else v for k, v in t.items()}
    base = None
    if ctx.base_cur and all(c == ctx.base_cur or c in ctx.fx for c in table):
        base = {k: round(sum(ctx.to_base(table[c][k], c)[0] for c in table), 2)
                for k in ("best_case", "weighted", "commit", "won")}
    moves = movement(ctx, a.prev, start, end) if a.prev else None
    out = {"period": label, "start": start.isoformat(), "end": end.isoformat(), "as_of": ctx.today.isoformat(),
           "by_currency": table, "base_currency": ctx.base_cur if base else None, "base_totals": base,
           "fx_used": ctx.fx if base else None,
           "slipped": [{"id": d["id"], "title": d["title"], "close": d["close"].isoformat(), "value": d["value"],
                        "currency": d["currency"], "days_past": (ctx.today - d["close"]).days} for d in slipped],
           "later": {"deals": len(later)}, "no_probability": noprob, "movement": moves}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(ctx.header(f"forecast {label} ({start.isoformat()} to {end.isoformat()})"))
    data_note(ctx)
    print(f"Probability = deal probability if set, else stage probability. Commit = probability >= {ctx.commit_p:g}%.")
    print("Open deals counted: expected close on or after today and inside the period.\n")
    print("Currency | Open deals | Best case | Weighted | Commit (deals) | Won in period (deals)")
    for c, t in table.items():
        print(f"{c} | {t['deals']} | {money(t['best_case'])} | {money(t['weighted'])} | "
              f"{money(t['commit'])} ({t['commit_deals']}) | {money(t['won'])} ({t['won_deals']})")
    if base:
        rates = ", ".join(f"1 {k} = {v:g} {ctx.base_cur}" for k, v in sorted(ctx.fx.items()) if k != ctx.base_cur)
        print(f"\nIn {ctx.base_cur} (fx from settings: {rates}): best case {money(base['best_case'])} | "
              f"weighted {money(base['weighted'])} | commit {money(base['commit'])} | won {money(base['won'])}")
    else:
        print("\nNo combined total: set base_currency and fx_to_base for every currency to combine.")
    if noprob:
        print(f"Not weighted (no probability): {noprob}")
    print(f"\nSlipped (still open, expected close already passed): {len(slipped)}")
    for s in out["slipped"]:
        print(f"  {s['id']} | {s['title']} | was {s['close']} ({s['days_past']} days ago) | {money(s['value'])} {s['currency']}")
    print(f"Open deals closing after {end.isoformat()}: {len(later)}")
    nodate = [d["id"] for d in open_ if not d["close"]]
    if nodate:
        print(f"Open deals with no expected close date (not counted): {nodate}")
    if moves:
        print(f"\nMovement since {moves['prev_file']}")
        for k, label2 in (("new", "New deals"), ("won", "Won"), ("lost", "Lost"), ("stage", "Stage moves"),
                          ("value", "Value changes"), ("close", "Close date changes")):
            items = moves[k]
            print(f"  {label2}: " + ("; ".join(items) if items else "none"))


def movement(ctx, prev_path, start, end):
    prev, _ = read_deals(Path(prev_path), None, {})
    P = {d["id"]: d for d in prev}
    C = {d["id"]: d for d in ctx.deals}
    m = {"prev_file": Path(prev_path).name, "new": [], "won": [], "lost": [], "stage": [], "value": [], "close": []}
    for i, d in C.items():
        p = P.get(i)
        if not p:
            m["new"].append(f"{i} {d['title']} ({money(d['value'])} {d['currency']})")
            continue
        if d["status"] != p["status"] and d["status"] in ("won", "lost"):
            m[d["status"]].append(f"{i} {d['title']} ({money(d['value'])} {d['currency']})"
                                  + (f" - {d['lost_reason']}" if d["lost_reason"] else ""))
        if d["stage"] != p["stage"]:
            m["stage"].append(f"{i} {d['title']}: {p['stage']} -> {d['stage']}")
        if d["value"] != p["value"]:
            diff = d["value"] - p["value"]
            m["value"].append(f"{i} {d['title']}: {money(p['value'])} -> {money(d['value'])} {d['currency']} ({'+' if diff >= 0 else ''}{money(diff)})")
        if d["close"] != p["close"]:
            pc, dc = p["close"], d["close"]
            note = ""
            if pc and dc and start <= pc <= end and dc > end:
                note = " (pushed OUT of period)"
            elif pc and dc and pc > end and start <= dc <= end:
                note = " (pulled INTO period)"
            m["close"].append(f"{i} {d['title']}: {pc} -> {dc}{note}")
    return m


def read_csv(path):
    if not path or not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{norm_header(re.sub(r"^(person|organization|activity)\s*-\s*", "", k, flags=re.I)): v for k, v in r.items()}
                for r in csv.DictReader(f)]


def cmd_match(ctx, a):
    persons = read_csv(ctx.persons_path)
    words = lambda s: set(re.findall(r"[a-z0-9]+", (s or "").lower()))
    pw, ow = words(a.person), words(a.org) - {"co", "inc", "ltd", "llc", "gmbh", "the"}
    email = (a.email or "").lower()
    cands = []
    for p in persons:
        sc, why = 0, []
        if email and p.get("email", "").lower() == email:
            sc += 10; why.append("email exact")
        if pw and pw & words(p.get("name")):
            sc += 3 * len(pw & words(p.get("name"))); why.append("name")
        if ow and ow & words(p.get("organization")):
            sc += 2; why.append("organization")
        if sc:
            cands.append((sc, p, why))
    cands.sort(key=lambda x: -x[0])
    print(ctx.header("match"))
    if not cands:
        print("No matching person in persons data. Do NOT create a deal; ask the user whether to add the person "
              "(and later a deal) themselves, or log the note on an organization.")
    kw = words(a.keywords)
    for sc, p, why in cands[:5]:
        print(f"Person {p.get('id')} | {p.get('name')} | {p.get('organization')} | {p.get('email')} | match: {', '.join(why)} (score {sc})")
        ds = [d for d in ctx.deals if d["status"] == "open" and (d["person"].lower() == p.get("name", "").lower()
              or d["org"].lower() == p.get("organization", "").lower())]
        for d in ds:
            hit = sorted(kw & words(d["title"]))
            print(f"   open deal {d['id']} | {d['title']} | {d['pipeline']} / {d['stage']} | "
                  f"{money(d['value'])} {d['currency']} | close {d['close']} | title keyword hits: {hit or 'none'}")
        if len(ds) > 1:
            print(f"   AMBIGUOUS: {len(ds)} open deals. Pick only if one title clearly matches the notes; otherwise ask.")
        if not ds:
            print("   No open deal. Do NOT create one; ask the user.")


def cmd_prep(ctx, a):
    q = a.query.lower().strip()
    if len(q) < 3 and not q.isdigit():
        sys.exit("error: query too short; use at least 3 characters of a company, person or deal title, or a deal id")
    ds = [d for d in ctx.deals if q in d["title"].lower() or q in d["org"].lower() or q in d["person"].lower()
          or str(d["id"]) == q]
    print(ctx.header(f"prep for '{a.query}'"))
    data_note(ctx)
    if not ds:
        print("No deal, organization or contact matches. Do not invent details; ask the user.")
        return
    orgs = {d["org"] for d in ds}
    for d in ds:
        r = assess(ctx, d)
        p, src = ctx.prob(d)
        print(f"\nDeal {d['id']} | {d['title']} | status {d['status']} | {d['pipeline']} / {d['stage']} | "
              f"{money(d['value'])} {d['currency']} | probability {p if p is not None else 'unknown'}% ({src}) | owner {d['owner']}")
        print(f"  Contact: {d['person']} | Org: {d['org']} | expected close {r['close']}"
              + (f" (PASSED {r['days_past_close']} days ago)" if r["days_past_close"] else ""))
        print(f"  Last touch {r['last_touch']} ({r['days_idle']} days ago, from {r['touch_source']}) | "
              f"next activity {r['next_activity'] or 'none'}{' OVERDUE' if r['next_overdue'] else ''}"
              + (f" | flags: {', '.join(r['flags'])}" if r["flags"] else ""))
    print("\nPeople at " + ", ".join(sorted(orgs)))
    for p in read_csv(ctx.persons_path):
        if p.get("organization") in orgs:
            print(f"  {p.get('name')} | {p.get('job title') or '-'} | {p.get('email')} | {p.get('phone')}")
    ids = {str(d["id"]) for d in ds}
    acts = [x for x in read_csv(ctx.activities_path) if x.get("deal id") in ids]
    done = sorted([x for x in acts if x.get("done", "").lower() in ("done", "1", "true", "yes")],
                  key=lambda x: x.get("due date", ""), reverse=True)[: a.limit]
    todo = sorted([x for x in acts if x not in done and x.get("done", "").lower() not in ("done", "1", "true", "yes")],
                  key=lambda x: x.get("due date", ""))
    print(f"\nLast {len(done)} done activities (newest first)")
    for x in done:
        print(f"  {x.get('due date')} | {x.get('type')} | {x.get('subject')} | deal {x.get('deal id')}"
              + (f" | note: {x.get('note')}" if x.get("note") else ""))
    print("Planned")
    for x in todo:
        print(f"  {x.get('due date')} | {x.get('type')} | {x.get('subject')} | deal {x.get('deal id')}")
    if not acts:
        print("  (no activity file or no activities for these deals)")


def resolve_stage(ctx, d, name):
    stages = [s for (pl, _), s in ctx.stage_info.items() if pl == (d["pipeline"] or "").lower()]
    if not stages:
        return None, f"no stages known for pipeline '{d['pipeline']}' (load stages.json or getStages)"
    n = name.lower().strip()
    exact = [s for s in stages if s["name"].lower() == n]
    if exact:
        return exact[0], None
    part = [s for s in stages if n in s["name"].lower() or all(w in s["name"].lower() for w in n.split())]
    if len(part) == 1:
        return part[0], None
    names = ", ".join(s["name"] for s in stages)
    return None, (f"'{name}' matches {len(part)} stages in pipeline '{d['pipeline']}' ({names}); ask the user"
                  if part else f"no stage like '{name}' in pipeline '{d['pipeline']}' (stages: {names})")


def cmd_diff(ctx, a):
    ch = json.loads(Path(a.changes).read_text())
    byid = {str(d["id"]): d for d in ctx.deals}
    print(ctx.header("proposed changes (nothing has been written)"))
    errors = questions = 0
    deal_ids = {str(c.get("deal_id")) for c in ch.get("changes", [])}
    if len(deal_ids) > 10:
        print(f"ERROR {len(deal_ids)} deals in one change list; split into batches of 10 or fewer.")
        errors += 1
    for c in ch.get("changes", []):
        d = byid.get(str(c.get("deal_id")))
        if not d:
            print(f"\nERROR deal {c.get('deal_id')} not found. Never create a deal to make a change fit.")
            errors += 1
            continue
        print(f"\nDeal {d['id']} | {d['title']} | {d['pipeline']} / {d['stage']} | status {d['status']}")
        if d["status"] != "open":
            print(f"  WARNING deal is {d['status']}; confirm with the user before changing it.")
        print("  Field | Current | Proposed")
        for f, v in (c.get("set") or {}).items():
            if f == "stage":
                s, err = resolve_stage(ctx, d, str(v))
                if err:
                    print(f"  stage | {d['stage']} | ERROR {err}")
                    errors += 1
                    continue
                sid = f" (stage_id {s['id']})" if s.get("id") is not None else ""
                print(f"  stage | {d['stage']} | {s['name']}{sid} ({s.get('probability', '?')}% stage probability)")
            elif f in ("close", "expected_close_date") and str(v).strip().lower() in ("", "tbd", "[you choose]", "you choose", "ask"):
                print(f"  expected close date | {d['close']} | QUESTION: user to choose a new date (not applied until given)")
                questions += 1
            elif f in ("close", "expected_close_date"):
                try:
                    nd = parse_date(str(v))
                except ValueError as e:
                    print(f"  expected close date | {d['close']} | ERROR {e}"); errors += 1; continue
                warn = " WARNING in the past" if nd < ctx.today else ""
                print(f"  expected close date | {d['close']} | {nd.isoformat()} ({nd.strftime('%a')}){warn}")
            elif f == "value":
                print(f"  value | {money(d['value'])} {d['currency']} | {money(float(v))} {d['currency']}"
                      "  CHECK: only if the user or the notes stated this value")
            elif f in ("status", "owner"):
                print(f"  {f} | {d.get(f, '')} | {v}  CHECK: change {f} only on the user's explicit instruction")
            else:
                print(f"  {f} | {d.get(f, '')} | {v}")
        if c.get("add_note"):
            print(f"  + note: {c['add_note']}")
        act = c.get("add_activity")
        if act:
            try:
                due = parse_date(act.get("due_date"))
                dd = f"{due.isoformat()} ({due.strftime('%a')})" + (" WARNING in the past" if due < ctx.today else "")
            except (ValueError, TypeError):
                dd = "ERROR no valid due_date"; errors += 1
            print(f"  + activity: {act.get('type', 'call')} '{act.get('subject', '')}' due {dd}")
    print(f"\n{errors} error(s), {questions} open question(s). " + ("Fix errors before asking for approval." if errors
          else "Show this to the user and wait for an explicit yes before writing anything."
          + (" Items marked QUESTION are applied only once the user supplies the value." if questions else "")))
    sys.exit(1 if errors else 0)


def cmd_date(a):
    t = parse_date(a.today) if a.today else dt.date.today()
    if a.add_days is not None:
        r = t + dt.timedelta(days=a.add_days)
    elif a.add_business_days is not None:
        r, n = t, a.add_business_days
        while n > 0:
            r += dt.timedelta(days=1)
            if r.weekday() < 5:
                n -= 1
    elif a.weekday:
        hits = [i for i, x in enumerate(DOW) if x.startswith(a.weekday.lower()[:3])]
        if not hits:
            sys.exit(f"error: unknown weekday {a.weekday!r}")
        r = t + dt.timedelta(days=((hits[0] - t.weekday() - 1) % 7) + 1)  # next one strictly after today
    else:
        r = t
    print(f"{r.isoformat()} ({r.strftime('%A')}) from {t.isoformat()} ({t.strftime('%A')})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, deals=True):
        if deals:
            p.add_argument("deals", help="deals CSV export, or 'sample'")
        p.add_argument("--stages")
        p.add_argument("--settings")
        p.add_argument("--today")
        p.add_argument("--persons")
        p.add_argument("--activities")
        p.add_argument("--map")
        return p

    p = common(sub.add_parser("load")); p.add_argument("--write")
    p = common(sub.add_parser("triage")); p.add_argument("--top", type=int, default=0); p.add_argument("--json", action="store_true")
    p = common(sub.add_parser("forecast")); p.add_argument("--prev"); p.add_argument("--period"); p.add_argument("--json", action="store_true")
    p = common(sub.add_parser("match"))
    for o in ("--person", "--org", "--email", "--keywords"):
        p.add_argument(o)
    p = common(sub.add_parser("prep")); p.add_argument("query"); p.add_argument("--limit", type=int, default=5)
    p = common(sub.add_parser("diff")); p.add_argument("--changes", required=True)
    p = sub.add_parser("date"); p.add_argument("--today"); p.add_argument("--add-days", type=int)
    p.add_argument("--add-business-days", type=int); p.add_argument("--weekday")
    a = ap.parse_args()
    if a.cmd == "date":
        return cmd_date(a)
    if a.cmd == "forecast" and a.prev == "sample":
        a.prev = str(SAMPLES / "deals_export_prev.csv")
    ctx = Ctx(a)
    if ctx.report["missing_required"] and a.cmd != "load":
        sys.exit("error: CSV is missing required columns " + ", ".join(ctx.report["missing_required"])
                 + ". Run `load` for the mapping report.")
    {"load": cmd_load, "triage": cmd_triage, "forecast": cmd_forecast, "match": cmd_match,
     "prep": cmd_prep, "diff": cmd_diff}[a.cmd](ctx, a)


if __name__ == "__main__":
    main()
