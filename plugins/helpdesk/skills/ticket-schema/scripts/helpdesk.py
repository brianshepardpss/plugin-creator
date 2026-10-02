#!/usr/bin/env python3
"""Helpdesk Triage toolkit: one ticket schema for Zendesk and Freshdesk.

Standard library only. Every number the plugin shows comes from here.

Subcommands
  normalize <export>                 print the export in the shared schema (JSON)
  triage <export> [--top N]          ranked open queue, SLA math, flags, clusters
  ticket <export> <id>               one ticket's thread, redacted, plus every ID in it
  weekly <export> [--days 7]         drivers, volume delta, SLA misses, CSAT, gaps
  days <date-a> <date-b>             whole days from a to b (for policy windows)
  redact                             redact stdin (card numbers, SSNs, CVV, expiry)

Common options
  --now ISO        "as of" time. Default: the export's exported_at; for the
                   bundled samples 2026-10-02T09:00Z; otherwise the current
                   clock. "--now latest" uses the export's latest timestamp.
  --kb DIR         KB folder (articles *.md, macros.json, known-issues.md,
                   vip-accounts.txt: one org name, email or domain per line).
                   Default: <plugin>/samples/kb when the export is a sample.
  --rules FILE     categories/weights JSON. Default: categories.json beside this.
  --tz ZONE        IANA zone (America/Chicago) or offset (+05:30) for naive CSV
                   timestamps (Freshdesk exports use the account time zone).
                   Default +00:00.
  --datefmt FMT    strptime format for slash dates (03/04/2026 is ambiguous and
                   is otherwise ignored with a warning).
  --json           machine-readable output instead of markdown.
  <export> may be a path, "sample" (Zendesk sample), "sample-freshdesk", or
  "-" to read JSON/CSV from stdin (connector mode; nothing touches disk).

Accepted inputs
  * Zendesk API JSON: {"tickets": [...]} with optional "users",
    "organizations", "groups" sideloads, per-ticket "comments",
    "slas.policy_metrics" (breach_at, stage) and "metric_set.solved_at".
    NDJSON (one ticket per line) also works.
  * Freshdesk API JSON: a list (or {"tickets": [...]}) of tickets with numeric
    status/priority, "due_by"/"fr_due_by", optional "conversations" and
    "requester".
  * CSV from either tool's export screen. Header names are matched by alias;
    Freshdesk numeric codes are mapped. CSV exports carry no reply thread.

Status mapping (Freshdesk): 2 open, 3 pending, 4 solved (Resolved), 5 closed,
6 pending (Waiting on Customer), 7 hold (Waiting on Third Party).
Priority mapping (Freshdesk): 1 low, 2 normal (Medium), 3 high, 4 urgent.

Triage score (higher = handle first), weights from the rules file:
  SLA: breached +100, due within 4h +70, due within 24h +20
       (only for new/open tickets; pending/hold pause the SLA clock)
  Priority: urgent +40, high +25, normal +10, low +0
  Flags: legal +40, security +35, vip +25, churn +15, anger +10, repeat +10
  Waiting: +1 per full day since created, capped at +10
  Ties break on earlier SLA due, then lower ticket id.
Flags are read from customer-authored public text only, never internal notes.
repeat = same requester has another ticket in the same category created within
repeat_window_days (14) of this one.

SLA miss (weekly): a ticket created in the window whose sla_due passed before
it was solved, or that is still unsolved and past sla_due at the as-of time.
Volume delta % = (this window - prior window) / prior window * 100, 1 decimal.
Macro candidate: a category with >= --min tickets (default 3) in the window
and no macro. KB-gap candidate: same, with no KB article.

Redaction (text is NFKC-normalized first, so full-width digits and NBSP are
caught): any span of 13-19 digits inside a digit run (groups joined by up to
3 spaces, newlines, dots, dashes, slashes or underscores) that passes the
Luhn check becomes [card ending NNNN redacted]; NNN-NN-NNNN, or 9 digits after
"SSN"/"social security", becomes [SSN redacted]; values after exp/expiry/
valid thru and CVV/CVC/CID/security code are redacted. JSON output is
redacted field by field before serialization.
Unknown status values (custom statuses) are treated as open and listed in a
warning. Rows without a ticket id are skipped and counted. All text
output passes through redaction; there is no switch to turn it off.
"""
import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent.parent
SAMPLES = PLUGIN / "samples"

FD_STATUS = {2: "open", 3: "pending", 4: "solved", 5: "closed", 6: "pending", 7: "hold"}
FD_PRIORITY = {1: "low", 2: "normal", 3: "high", 4: "urgent"}
STATUS_NAMES = {"new": "new", "open": "open", "pending": "pending", "hold": "hold",
                "on-hold": "hold", "on hold": "hold", "solved": "solved", "resolved": "solved",
                "closed": "closed", "waiting on customer": "pending",
                "waiting on third party": "hold"}
PRIORITY_NAMES = {"low": "low", "normal": "normal", "medium": "normal", "high": "high",
                  "urgent": "urgent"}
OPEN = {"new", "open", "pending", "hold"}
ACTIVE = {"new", "open"}

CSV_ALIASES = {
    "id": ["ticket id", "id", "ticket #", "#"],
    "subject": ["subject", "title"],
    "description": ["description", "body", "first message", "description text"],
    "status": ["status"],
    "priority": ["priority"],
    "created_at": ["created time", "created at", "created", "requested"],
    "updated_at": ["last update time", "updated at", "updated", "last updated"],
    "sla_due": ["due by time", "due by", "next sla breach", "sla due", "due date"],
    "solved_at": ["resolved time", "solved at", "solved", "closed time"],
    "tags": ["tags"],
    "name": ["full name", "requester", "requester name", "contact", "contact name"],
    "email": ["email", "requester email", "contact email"],
    "org": ["company name", "organization", "company", "organisation"],
    "assignee": ["agent", "assignee"],
    "group": ["group"],
    "csat": ["satisfaction rating", "satisfaction", "survey results", "csat",
             "customer satisfaction"],
}

# ----------------------------------------------------------------- redaction
# A "digit run" is digit groups joined by up to 3 separator characters
# (space, NBSP, newline, dot, dash, slash, underscore). Card numbers are
# found inside runs by testing every span of whole groups that totals 13-19
# digits against the Luhn check, so neighbouring numbers cannot hide a card.
DIGIT_RUN_RE = re.compile(r"\d+(?:[\s.\-/_]{1,3}\d+)*")
SSN_RE = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
SSN_KW_RE = re.compile(r"\b(ssn|social security(?: number| no\.?)?|sin|tax id)(\W{0,4})\d{3}[ .-]?\d{2}[ .-]?\d{4}(?!\d)", re.I)
EXP_RE = re.compile(r"\b(exp(?:iry|ires|iration)?(?:\s+date)?|valid\s+(?:thru|through|until))(\W{0,4})\d{1,2}\s*[/.-]?\s*\d{2,4}(?!\d)", re.I)
CVV_RE = re.compile(r"\b(cvv2?|cvc2?|cv2|cid|csc|security\s+code)(\W{0,4})\d{3,4}(?!\d)", re.I)


def luhn(digits):
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def _cards_in_run(run):
    groups = [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"\d+", run)]
    spans = []
    i = 0
    while i < len(groups):
        best = None
        digits = ""
        for j in range(i, len(groups)):
            digits += groups[j][2]
            if len(digits) > 19:
                break
            if len(digits) >= 13 and luhn(digits):
                best = (j, digits)
        if best:
            j, digits = best
            spans.append((groups[i][0], groups[j][1], digits))
            i = j + 1
        else:
            i += 1
    return spans


def redact(text):
    if not text:
        return text
    text = unicodedata.normalize("NFKC", text)  # full-width digits, NBSP -> ASCII

    def run(m):
        r = m.group(0)
        out, last = [], 0
        for a, b, digits in _cards_in_run(r):
            out.append(r[last:a])
            out.append(f"[card ending {digits[-4:]} redacted]")
            last = b
        out.append(r[last:])
        return "".join(out)

    text = SSN_KW_RE.sub(lambda m: m.group(1) + m.group(2) + "[SSN redacted]", text)
    text = EXP_RE.sub(lambda m: m.group(1) + m.group(2) + "[redacted]", text)
    text = CVV_RE.sub(lambda m: m.group(1) + m.group(2) + "[redacted]", text)
    text = SSN_RE.sub("[SSN redacted]", text)
    text = DIGIT_RUN_RE.sub(run, text)
    return text


def redact_obj(o):
    """Redact every string inside a JSON-able object before it is serialized."""
    if isinstance(o, str):
        return redact(o)
    if isinstance(o, dict):
        return {k: redact_obj(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [redact_obj(v) for v in o]
    if isinstance(o, datetime):
        return iso(o)
    return o


def has_sensitive(text):
    return redact(text) != unicodedata.normalize("NFKC", text or "")

# --------------------------------------------------------------- time utils


DATEFMT = None
AMBIGUOUS_DATES = set()
UNKNOWN_STATUS = set()


def parse_ts(value, tz):
    if value in (None, ""):
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    fmts = [None, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%a, %d %b, %Y at %I:%M %p"]
    if DATEFMT:
        fmts.insert(0, DATEFMT)
    elif re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", s):
        AMBIGUOUS_DATES.add(s)  # 03/04/2026 could be March or April: refuse to guess
        return None
    for fmt in fmts:
        try:
            dt = datetime.fromisoformat(s) if fmt is None else datetime.strptime(s, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt.astimezone(timezone.utc)
    return None


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def fmt_delta(minutes):
    sign = "-" if minutes < 0 else ""
    m = abs(int(minutes))
    d, rem = divmod(m, 1440)
    h, mm = divmod(rem, 60)
    if d:
        return f"{sign}{d}d{h:02d}h"
    return f"{sign}{h}h{mm:02d}m"

# ------------------------------------------------------------------ loading


def norm_status(v):
    if v is None:
        return "open"
    s = str(v).strip().lower()
    if s.isdigit():
        if int(s) not in FD_STATUS:
            UNKNOWN_STATUS.add(s)
        return FD_STATUS.get(int(s), "open")
    if s in STATUS_NAMES:
        return STATUS_NAMES[s]
    if s:
        UNKNOWN_STATUS.add(str(v).strip())  # custom status (e.g. "In Progress"): treat as open
    return "open"


def norm_priority(v):
    if v is None or str(v).strip() == "":
        return "normal"
    s = str(v).strip().lower()
    if s.isdigit():
        return FD_PRIORITY.get(int(s), "normal")
    return PRIORITY_NAMES.get(s, "normal")


def norm_csat(v, comment=""):
    if v in (None, "", "unoffered", "offered"):
        return None
    s = str(v).strip().lower()
    try:
        n = int(s)
        score = "good" if n > 100 or n == 1 else ("neutral" if n == 100 else "bad")
    except ValueError:
        if any(w in s for w in ("unhappy", "bad", "not happy", "dissatisfied", "poor")):
            score = "bad"
        elif "neutral" in s:
            score = "neutral"
        elif any(w in s for w in ("happy", "good", "great", "awesome", "satisfied")):
            score = "good"
        else:
            return None
    return {"score": score, "comment": comment or ""}


def blank_ticket(source):
    return {"id": None, "source": source, "subject": "", "status": "open", "priority": "normal",
            "requester": {"name": "", "email": ""}, "org": "", "org_tags": [], "tags": [],
            "created_at": None, "updated_at": None, "solved_at": None, "sla_due": None,
            "sla_paused": False, "assignee": "", "group": "", "csat": None, "messages": []}


def load_zendesk(data, tz):
    users = {u["id"]: u for u in data.get("users", [])}
    orgs = {o["id"]: o for o in data.get("organizations", [])}
    groups = {g["id"]: g for g in data.get("groups", [])}
    out = []
    for z in data["tickets"]:
        t = blank_ticket("zendesk")
        t["id"] = str(z.get("id"))
        t["subject"] = z.get("subject") or ""
        t["status"] = norm_status(z.get("status"))
        t["priority"] = norm_priority(z.get("priority"))
        req = users.get(z.get("requester_id"), {})
        if isinstance(z.get("requester"), dict):
            req = z["requester"]
        t["requester"] = {"name": req.get("name", ""), "email": req.get("email", "")}
        org = orgs.get(z.get("organization_id"), {})
        t["org"] = org.get("name", "")
        t["org_tags"] = [x.lower() for x in org.get("tags", [])]
        t["tags"] = [x.lower() for x in z.get("tags", [])]
        t["created_at"] = parse_ts(z.get("created_at"), tz)
        t["updated_at"] = parse_ts(z.get("updated_at"), tz)
        t["solved_at"] = parse_ts((z.get("metric_set") or {}).get("solved_at"), tz)
        metrics = ((z.get("slas") or {}).get("policy_metrics")) or []
        dues = [(parse_ts(m.get("breach_at"), tz), m.get("stage")) for m in metrics if m.get("breach_at")]
        dues = [d for d in dues if d[0]]
        if dues:
            dues.sort()
            t["sla_due"] = dues[0][0]
            t["sla_paused"] = all(stage == "paused" for _, stage in dues)
        assignee = users.get(z.get("assignee_id"), {})
        t["assignee"] = assignee.get("name", "")
        t["group"] = groups.get(z.get("group_id"), {}).get("name", "")
        cs = z.get("satisfaction_rating") or {}
        t["csat"] = norm_csat(cs.get("score"), cs.get("comment", ""))
        comments = z.get("comments") or []
        if not comments and z.get("description"):
            comments = [{"id": None, "author_id": z.get("requester_id"), "public": True,
                         "body": z["description"], "created_at": z.get("created_at")}]
        for c in comments:
            au = users.get(c.get("author_id"), {})
            is_customer = c.get("author_id") == z.get("requester_id") or au.get("role") == "end-user"
            t["messages"].append({
                "id": c.get("id"), "author": au.get("name", ""),
                "role": "customer" if is_customer else "agent",
                "public": bool(c.get("public", True)),
                "created_at": parse_ts(c.get("created_at"), tz),
                "body": c.get("plain_body") or c.get("body") or ""})
        out.append(t)
    return out


def load_freshdesk_json(items, tz):
    out = []
    for f in items:
        t = blank_ticket("freshdesk")
        t["id"] = str(f.get("id"))
        t["subject"] = f.get("subject") or ""
        t["status"] = norm_status(f.get("status"))
        t["priority"] = norm_priority(f.get("priority"))
        req = f.get("requester") or {}
        t["requester"] = {"name": req.get("name", ""), "email": req.get("email", "")}
        comp = f.get("company") or {}
        t["org"] = comp.get("name", "")
        t["tags"] = [x.lower() for x in f.get("tags", []) or []]
        t["created_at"] = parse_ts(f.get("created_at"), tz)
        t["updated_at"] = parse_ts(f.get("updated_at"), tz)
        stats = f.get("stats") or {}
        t["solved_at"] = parse_ts(stats.get("resolved_at") or stats.get("closed_at"), tz)
        # before the first response the earlier of fr_due_by/due_by applies; after it, due_by
        keys = ("due_by",) if stats.get("first_responded_at") else ("fr_due_by", "due_by")
        dues = [d for d in (parse_ts(f.get(k), tz) for k in keys) if d]
        t["sla_due"] = min(dues) if dues else None
        t["sla_paused"] = t["status"] in ("pending", "hold")
        t["messages"].append({"id": None, "author": t["requester"]["name"], "role": "customer",
                              "public": True, "created_at": t["created_at"],
                              "body": f.get("description_text") or f.get("description") or ""})
        for c in f.get("conversations", []) or []:
            t["messages"].append({
                "id": c.get("id"), "author": "", "role": "customer" if c.get("incoming") else "agent",
                "public": not c.get("private", False), "created_at": parse_ts(c.get("created_at"), tz),
                "body": c.get("body_text") or c.get("body") or ""})
        out.append(t)
    return out


def load_csv(text, tz):
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip().lower() for h in rows[0]]
    idx = {}
    for key, names in CSV_ALIASES.items():
        for n in names:
            if n in header:
                idx[key] = header.index(n)
                break
    if "id" not in idx:
        sys.exit("CSV has no ticket id column (looked for: " + ", ".join(CSV_ALIASES["id"]) + ")")
    source = "freshdesk" if ("ticket id" in header or "due by time" in header) else "csv"
    out, skipped = [], 0
    for r in rows[1:]:
        if not any(c.strip() for c in r):
            skipped += 1
            continue

        def g(k):
            i = idx.get(k)
            return r[i].strip() if i is not None and i < len(r) else ""

        if not g("id"):
            skipped += 1
            continue
        t = blank_ticket(source)
        t["id"] = g("id")
        t["subject"] = g("subject")
        t["status"] = norm_status(g("status"))
        t["priority"] = norm_priority(g("priority"))
        t["requester"] = {"name": g("name"), "email": g("email")}
        t["org"] = g("org")
        sep = r"[,;]" if re.search(r"[,;]", g("tags")) else r"\s+"  # Zendesk CSV tags are space-separated
        t["tags"] = [x.strip().lower() for x in re.split(sep, g("tags")) if x.strip()]
        t["created_at"] = parse_ts(g("created_at"), tz)
        t["updated_at"] = parse_ts(g("updated_at"), tz)
        t["solved_at"] = parse_ts(g("solved_at"), tz)
        t["sla_due"] = parse_ts(g("sla_due"), tz)
        t["sla_paused"] = t["status"] in ("pending", "hold")
        t["assignee"] = g("assignee")
        t["group"] = g("group")
        t["csat"] = norm_csat(g("csat"))
        if g("description"):
            t["messages"].append({"id": None, "author": g("name"), "role": "customer",
                                  "public": True, "created_at": t["created_at"],
                                  "body": g("description")})
        out.append(t)
    return out, skipped


def load(path, tz):
    p = Path(path)
    if path == "sample" or path == "samples":
        p = SAMPLES / "zendesk_export.json"
    elif path in ("sample-freshdesk", "freshdesk-sample"):
        p = SAMPLES / "freshdesk_export.csv"
    if path == "-":  # connector mode: tickets piped in, nothing written to disk
        text = sys.stdin.read()
        p = Path("stdin.json") if text.lstrip().startswith(("{", "[")) else Path("stdin.csv")
    else:
        text = p.read_text(encoding="utf-8-sig")
    meta = {"file": str(p), "source": None, "exported_at": None, "skipped_rows": 0,
            "is_sample": path != "-" and p.resolve().parent == SAMPLES.resolve()}
    stripped = text.lstrip()
    if p.suffix.lower() == ".csv" or not stripped.startswith(("{", "[")):
        tickets, meta["skipped_rows"] = load_csv(text, tz)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"tickets": [json.loads(line) for line in text.splitlines() if line.strip()]}
        if isinstance(data, dict):
            meta["exported_at"] = parse_ts(data.get("exported_at"), tz)
            items = data.get("tickets", data.get("results", []))
        else:
            items = data
        if items and any(k in items[0] for k in ("due_by", "fr_due_by", "description_text")) \
                or (items and isinstance(items[0].get("status"), int)):
            tickets = load_freshdesk_json(items, tz)
        else:
            tickets = load_zendesk(data if isinstance(data, dict) else {"tickets": items}, tz)
    meta["source"] = tickets[0]["source"] if tickets else "unknown"
    return tickets, meta


SAMPLE_AS_OF = "2026-10-02T09:00:00Z"


def as_of(tickets, meta, now_arg):
    """Default: the export's exported_at; for the bundled samples a fixed
    2026-10-02T09:00Z; otherwise the current clock (conservative: SLA risk is
    never understated). --now <ISO> or --now latest overrides."""
    if now_arg == "now":
        return datetime.now(timezone.utc), "clock"
    if now_arg and now_arg != "latest":
        return parse_ts(now_arg, timezone.utc), "--now"
    if meta.get("exported_at") and now_arg != "latest":
        return meta["exported_at"], "exported_at"
    if meta.get("is_sample") and now_arg != "latest":
        return parse_ts(SAMPLE_AS_OF, timezone.utc), "sample snapshot time"
    if now_arg != "latest":
        return datetime.now(timezone.utc), "clock (export has no exported_at; pass --now to override)"
    stamps = [x for t in tickets for x in (t["created_at"], t["updated_at"], t["solved_at"]) if x]
    stamps += [m["created_at"] for t in tickets for m in t["messages"] if m["created_at"]]
    return (max(stamps) if stamps else datetime.now(timezone.utc)), "latest timestamp in export"

# ------------------------------------------------------------ KB and rules


def load_rules(path):
    return json.loads(Path(path or HERE / "categories.json").read_text())


def kb_dir(arg, meta):
    if arg:
        return Path(arg)
    if meta.get("is_sample"):
        return SAMPLES / "kb"
    return None


def load_kb(d):
    kb = {"articles": [], "macros": [], "known": [], "vip": []}
    if not d or not d.is_dir():
        return kb
    vf = d / "vip-accounts.txt"
    if vf.exists():
        kb["vip"] = [ln.strip().lower() for ln in vf.read_text().splitlines()
                     if ln.strip() and not ln.strip().startswith("#")]
    for f in sorted(d.glob("*.md")):
        txt = f.read_text()
        fm = {}
        m = re.match(r"---\n(.*?)\n---\n", txt, re.S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
        if fm.get("id") == "known-issues" or f.name.startswith("known-issues"):
            for sec in re.split(r"^## ", txt, flags=re.M)[1:]:
                kid = sec.splitlines()[0].strip()
                kw = re.search(r"Match keywords:\s*(.+)", sec)
                cat = re.search(r"Category:\s*(.+)", sec)
                st = re.search(r"Status:\s*(.+)", sec)
                summ = re.search(r"Summary:\s*(.+)", sec)
                kb["known"].append({
                    "id": kid, "keywords": [k.strip().lower() for k in kw.group(1).split(",")] if kw else [],
                    "category": cat.group(1).strip() if cat else None,
                    "status": st.group(1).strip() if st else "", "summary": summ.group(1).strip() if summ else ""})
            continue
        kb["articles"].append({"id": fm.get("id", f.stem), "title": fm.get("title", f.stem),
                               "category": fm.get("category", ""), "file": f.name})
    mf = d / "macros.json"
    if mf.exists():
        kb["macros"] = json.loads(mf.read_text())
    return kb

# ---------------------------------------------------------------- analysis


def kw_hits(patterns, text):
    n = 0
    for p in patterns:
        n += len(re.findall(r"(?<![\w])" + p + r"(?![\w])", text, re.I))
    return n


def customer_text(t):
    return "\n".join(m["body"] for m in t["messages"] if m["role"] == "customer" and m["public"])


def categorize(t, rules):
    subj = t["subject"]
    first = next((m["body"] for m in t["messages"] if m["role"] == "customer"), "")
    best, best_n = "other", 0
    for c in rules["categories"]:
        n = 2 * kw_hits(c["keywords"], subj) + kw_hits(c["keywords"], first)
        if n > best_n:
            best, best_n = c["name"], n
    return best


STOP = {
    "en": {"the", "and", "is", "are", "our", "we", "not", "you", "this", "with", "for", "have", "since"},
    "es": {"el", "los", "las", "que", "y", "en", "nuestro", "nuestra", "desde", "por", "gracias", "hola", "ya"},
    "fr": {"le", "les", "et", "est", "nous", "pas", "notre", "depuis", "merci", "bonjour"},
    "de": {"der", "die", "das", "und", "ist", "nicht", "wir", "unser", "seit", "danke", "hallo"},
    "pt": {"os", "que", "em", "nao", "nosso", "nossa", "desde", "obrigado", "ola", "voce"},
}


def language(text):
    words = re.findall("[a-zA-Z\u00e0-\u00ff]+", text.lower())
    counts = {lang: sum(w in s for w in words) for lang, s in STOP.items()}
    lang = max(counts, key=counts.get)
    return lang if counts[lang] >= 3 and counts[lang] > counts["en"] else "en"


def tokens(text):
    stop = STOP["en"] | {"a", "an", "to", "of", "in", "it", "on", "my", "i", "is", "since", "today",
                         "this", "morning", "was", "be", "can", "do", "how", "please", "any", "all",
                         "did", "get", "got", "their", "them", "none", "out"}
    ws = re.findall(r"[a-z0-9]+", text.lower())
    return {w.rstrip("s") for w in ws if w not in stop and len(w) > 2}


def analyze(tickets, now, rules, kb):
    W = rules["weights"]
    for t in tickets:
        t["category"] = categorize(t, rules)
        ctext = customer_text(t)
        t["language"] = language(t["subject"] + " " + ctext)
        flags = []
        for name, pats in rules["escalation"].items():
            hit = kw_hits(pats, t["subject"] + "\n" + ctext)
            if name == "anger" and not hit:
                caps = [w for w in re.findall(r"\b[A-Z]{4,}\b", t["subject"] + " " + ctext)
                        if w not in {"HTTP", "HTML", "JSON", "UTC", "VIP", "SSO"}]
                hit = len(caps) >= 2 or "!!" in ctext
            if hit:
                flags.append(name)
        email = t["requester"]["email"].lower()
        domain = email.split("@")[-1] if "@" in email else ""
        listed = any(v and (v == t["org"].lower() or v == email or v == domain) for v in kb["vip"])
        if listed or set(rules.get("vip_tags", [])) & set(t["org_tags"] + t["tags"]):
            flags.append("vip")
        if has_sensitive(t["subject"] + "\n" + "\n".join(m["body"] for m in t["messages"])):
            flags.append("pii-redacted")
        t["flags"] = flags
        t["known_issue"] = None
        for k in kb["known"]:
            if k["category"] and k["category"] != t["category"]:
                continue
            if any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", (t["subject"] + " " + ctext).lower())
                   for w in k["keywords"] if w):
                t["known_issue"] = k["id"]
                break
    # repeat contacts: same requester, same category, within window
    win = timedelta(days=rules.get("repeat_window_days", 14))
    for t in tickets:
        key = (t["requester"]["email"] or t["requester"]["name"]).lower()
        for o in tickets:
            if o is t or not key or (o["requester"]["email"] or o["requester"]["name"]).lower() != key:
                continue
            if o["category"] == t["category"] and o["created_at"] and t["created_at"] \
                    and abs(o["created_at"] - t["created_at"]) <= win:
                t["flags"].append("repeat")
                t.setdefault("repeat_of", []).append(o["id"])
                break
    # SLA and score
    for t in tickets:
        t["sla_minutes_left"] = None
        score, why = 0, []
        if t["sla_due"] is not None:
            t["sla_minutes_left"] = round((t["sla_due"] - now).total_seconds() / 60)
        if t["status"] in ACTIVE and t["sla_minutes_left"] is not None:
            left = t["sla_minutes_left"]
            if left < 0:
                score += W["sla_breached"]
                why.append(f"SLA breached {fmt_delta(-left)} ago")
            elif left <= 240:
                score += W["sla_within_4h"]
                why.append(f"SLA due in {fmt_delta(left)}")
            elif left <= 1440:
                score += W["sla_within_24h"]
                why.append(f"SLA due in {fmt_delta(left)}")
        score += W["priority"].get(t["priority"], 0)
        if t["priority"] in ("urgent", "high"):
            why.append(f"{t['priority']} priority")
        for f in t["flags"]:
            if f in W["flags"]:
                score += W["flags"][f]
        if t["created_at"]:
            days = int((now - t["created_at"]).total_seconds() // 86400)
            add = min(days * W["per_day_waiting"], W["waiting_cap"])
            score += max(add, 0)
            if days >= 3:
                why.append(f"waiting {days}d")
        t["score"] = score
        t["reasons"] = why
    return tickets


def clusters(open_tickets, rules):
    parent = {t["id"]: t["id"] for t in open_tickets}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_ki = {}
    for t in open_tickets:
        if t["known_issue"]:
            by_ki.setdefault(t["known_issue"], []).append(t["id"])
    for ids in by_ki.values():
        for i in ids[1:]:
            parent[find(i)] = find(ids[0])
    toks = {t["id"]: tokens(t["subject"] + " " + next(
        (m["body"] for m in t["messages"] if m["role"] == "customer"), "")) for t in open_tickets}
    thr = rules.get("duplicate_jaccard", 0.4)
    for i, a in enumerate(open_tickets):
        for b in open_tickets[i + 1:]:
            if a["category"] != b["category"]:
                continue
            ta, tb = toks[a["id"]], toks[b["id"]]
            if ta and tb and len(ta & tb) / len(ta | tb) >= thr:
                parent[find(b["id"])] = find(a["id"])
    groups = {}
    for t in open_tickets:
        groups.setdefault(find(t["id"]), []).append(t)
    out = []
    for members in groups.values():
        if len(members) < 2:
            continue
        ki = next((m["known_issue"] for m in members if m["known_issue"]), None)
        out.append({"label": f"C{len(out) + 1}", "ids": [m["id"] for m in members], "known_issue": ki,
                    "subject": members[0]["subject"]})
    return out


def route(t, rules):
    if {"legal", "security", "vip"} & set(t["flags"]):
        return rules.get("escalation_route", "Team lead")
    for c in rules["categories"]:
        if c["name"] == t["category"]:
            return c.get("route", "Tier 1")
    return "Tier 1"

# ------------------------------------------------------------------ output


def warnings(meta):
    w = []
    if meta.get("skipped_rows"):
        w.append(f"Skipped {meta['skipped_rows']} row(s) that were blank or had no ticket id.")
    if UNKNOWN_STATUS:
        w.append("Unrecognized status value(s) treated as open: " + ", ".join(sorted(UNKNOWN_STATUS)) + ".")
    if AMBIGUOUS_DATES:
        ex = sorted(AMBIGUOUS_DATES)[0]
        w.append(f"{len(AMBIGUOUS_DATES)} date(s) like '{ex}' are ambiguous (day/month order) and were "
                 "ignored; rerun with --datefmt '%m/%d/%Y %H:%M' or '%d/%m/%Y %H:%M'.")
    return w


def first_name(name):
    return (name or "").split(" ")[0]


def cmd_triage(a):
    tz = tzarg(a.tz)
    tickets, meta = load(a.export, tz)
    now, src = as_of(tickets, meta, a.now)
    rules = load_rules(a.rules)
    kb = load_kb(kb_dir(a.kb, meta))
    analyze(tickets, now, rules, kb)
    q = [t for t in tickets if t["status"] in OPEN]
    far = datetime.max.replace(tzinfo=timezone.utc)
    q.sort(key=lambda t: (-t["score"], t["sla_due"] or far, int(t["id"]) if t["id"].isdigit() else 0))
    cl = clusters(q, rules)
    cl_of = {i: c["label"] for c in cl for i in c["ids"]}
    for t in q:
        t["owner"] = route(t, rules)
        t["cluster"] = cl_of.get(t["id"])
    if a.json:
        print(json.dumps(redact_obj({"as_of": iso(now), "as_of_source": src, "source": meta["source"],
                                     "open": len(q), "queue": [slim(t) for t in q], "clusters": cl,
                                     "warnings": warnings(meta)}), indent=1))
        return
    top = q[:a.top] if a.top else q
    print(f"# Queue triage, as of {iso(now)} ({src})")
    print(f"Source: {meta['source']} export, {len(tickets)} tickets, {len(q)} open "
          f"(new/open/pending/hold).")
    for w in warnings(meta):
        print(f"Warning: {w}")
    at_risk = [t for t in q if t["status"] in ACTIVE and t["sla_minutes_left"] is not None
               and t["sla_minutes_left"] <= 240]
    breached = [t for t in at_risk if t["sla_minutes_left"] < 0]
    esc = [t for t in q if {"legal", "security", "vip"} & set(t["flags"])]
    print(f"SLA breached: {len(breached)}. SLA due within 4h: {len(at_risk) - len(breached)}. "
          f"Escalations (legal/security/vip): {len(esc)}. Duplicate clusters: {len(cl)}.\n")
    print("| # | Ticket | Subject | Pri | Category | SLA left | Flags | Owner | Dup | Why |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for n, t in enumerate(top, 1):
        if t["sla_minutes_left"] is None:
            sla = "none"
        elif t["status"] not in ACTIVE:
            sla = "paused"
        else:
            sla = fmt_delta(t["sla_minutes_left"]) + (" BREACHED" if t["sla_minutes_left"] < 0 else "")
        flags = ", ".join(t["flags"] + ([f"lang:{t['language']}"] if t["language"] != "en" else []))
        subj = t["subject"] if len(t["subject"]) <= 48 else t["subject"][:45] + "..."
        why = "; ".join(t["reasons"] + ([f"known issue {t['known_issue']}"] if t["known_issue"] else [])) or "routine"
        print(f"| {n} | {t['id']} | {redact(subj).replace('|', '/')} | {t['priority']} | {t['category']} | {sla} "
              f"| {flags or '-'} | {t['owner']} | {t['cluster'] or '-'} | {why} (score {t['score']}) |")
    if cl:
        print("\n## Duplicate clusters")
        for c in cl:
            ki = f" -> known issue {c['known_issue']}" if c["known_issue"] else ""
            print(f"- {c['label']}: tickets {', '.join(c['ids'])}{ki}")
    if kb["known"]:
        hits = [t for t in q if t["known_issue"]]
        if hits:
            print("\n## Known-issue matches")
            for t in hits:
                k = next(k for k in kb["known"] if k["id"] == t["known_issue"])
                print(f"- {t['id']}: {k['id']} ({k['status']})")
    if any("pii-redacted" in t["flags"] for t in q):
        print("\nNote: card numbers or other sensitive numbers were found and redacted in "
              + ", ".join(t["id"] for t in q if "pii-redacted" in t["flags"])
              + ". Ask an admin to redact them in the helpdesk too.")


def slim(t):
    return {"id": t["id"], "subject": t["subject"], "status": t["status"], "priority": t["priority"],
            "category": t["category"], "sla_due": iso(t["sla_due"]),
            "sla_minutes_left": t["sla_minutes_left"], "flags": t["flags"], "language": t["language"],
            "known_issue": t["known_issue"], "owner": t.get("owner"), "cluster": t.get("cluster"),
            "score": t["score"], "reasons": t["reasons"], "org": t["org"],
            "requester_first_name": first_name(t["requester"]["name"])}


def cmd_ticket(a):
    tz = tzarg(a.tz)
    tickets, meta = load(a.export, tz)
    now, src = as_of(tickets, meta, a.now)
    rules = load_rules(a.rules)
    kb = load_kb(kb_dir(a.kb, meta))
    analyze(tickets, now, rules, kb)
    t = next((x for x in tickets if x["id"] == str(a.id)), None)
    if not t:
        sys.exit(f"ticket {a.id} not found in {meta['file']}")
    lines = [f"# Ticket {t['id']}: {t['subject']}",
             f"Status: {t['status']} | Priority: {t['priority']} | Category: {t['category']} | "
             f"Language: {t['language']} | Flags: {', '.join(t['flags']) or '-'}",
             f"Requester: {t['requester']['name']} ({t['org'] or 'no org'}) | Assignee: {t['assignee'] or '-'}"
             f" | Group: {t['group'] or '-'}",
             f"Created: {iso(t['created_at'])} | SLA due: {iso(t['sla_due']) or '-'}"
             + (f" ({fmt_delta(t['sla_minutes_left'])} from as-of {iso(now)})" if t["sla_minutes_left"] is not None else ""),
             f"Known issue: {t['known_issue'] or '-'} | Repeat of: {', '.join(t.get('repeat_of', [])) or '-'}",
             f"Messages: {len(t['messages'])}" + (" (export has no reply thread; CSV exports carry only the first message)" if len(t['messages']) <= 1 and meta['source'] != 'zendesk' else ""),
             ""]
    for n, m in enumerate(t["messages"], 1):
        vis = "public" if m["public"] else "INTERNAL NOTE"
        lines.append(f"[{n}] {iso(m['created_at'])} {m['role']} {m['author'] or ''} ({vis}):")
        lines.append(m["body"])
        lines.append("")
    body = redact("\n".join(lines))
    msgs = redact("\n".join([t["subject"]] + [m["body"] for m in t["messages"]]))
    ids = sorted(set(re.findall(r"\b[A-Z]{2,6}-\d{2,}\b", msgs)))
    ids = sorted(set(ids) | set(re.findall(r"#\d{3,}\b", msgs)))
    money = sorted(set(re.findall("[$\u00a3\u20ac]\\s?\\d[\\d,]*(?:\\.\\d{2})?", msgs))
                   | set(re.findall(r"\b(?:USD|EUR|GBP|CAD|AUD|INR)\s?\d[\d,]*(?:\.\d{2})?", msgs)))
    dates = sorted(set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", "\n".join(m["body"] for m in t["messages"]))))
    print(body)
    print("## Identifiers present in this ticket (quote only these)")
    print(f"- reference IDs: {', '.join(ids) or 'none'}")
    print(f"- amounts: {', '.join(money) or 'none'}")
    print(f"- dates written in messages: {', '.join(dates) or 'none'}")


def cmd_weekly(a):
    tz = tzarg(a.tz)
    tickets, meta = load(a.export, tz)
    now, src = as_of(tickets, meta, a.now)
    rules = load_rules(a.rules)
    kb = load_kb(kb_dir(a.kb, meta))
    analyze(tickets, now, rules, kb)
    start = now - timedelta(days=a.days)
    pstart = start - timedelta(days=a.days)
    cur = [t for t in tickets if t["created_at"] and start < t["created_at"] <= now]
    prev = [t for t in tickets if t["created_at"] and pstart < t["created_at"] <= start]

    def missed(t):
        if not t["sla_due"]:
            return False
        if t["solved_at"]:
            return t["solved_at"] > t["sla_due"]
        return t["status"] in OPEN and now > t["sla_due"]

    def drivers(ts):
        c = {}
        for t in ts:
            c.setdefault(t["category"], []).append(t["id"])
        return sorted(c.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    delta = len(cur) - len(prev)
    pct = f"{delta / len(prev) * 100:+.1f}%" if prev else "n/a (no prior tickets)"
    cm, pm = [t for t in cur if missed(t)], [t for t in prev if missed(t)]
    lack = [t["id"] for t in cur + prev if t["status"] in ("solved", "closed") and not t["solved_at"]]
    nosolved = [f"{len(lack)} solved/closed ticket(s) have no solved time ({', '.join(lack[:10])}); "
                "SLA misses may be undercounted."] if lack else []
    good = [t for t in cur if t["csat"] and t["csat"]["score"] == "good"]
    bad = [t for t in cur if t["csat"] and t["csat"]["score"] == "bad"]
    rated = len(good) + len(bad) + len([t for t in cur if t["csat"] and t["csat"]["score"] == "neutral"])
    macro_cats = {m.get("category") for m in kb["macros"]}
    kb_cats = {x["category"] for x in kb["articles"]}
    d = drivers(cur)
    macro_c = [(c, ids) for c, ids in d if len(ids) >= a.min and c not in macro_cats and c != "other"]
    kb_c = [(c, ids) for c, ids in d if len(ids) >= a.min and c not in kb_cats and c != "other"]
    open_now = [t for t in tickets if t["status"] in OPEN]
    res = {"as_of": iso(now), "window": [iso(start), iso(now)], "prior_window": [iso(pstart), iso(start)],
           "created_this_window": len(cur), "created_prior_window": len(prev), "delta": delta, "delta_pct": pct,
           "open_now": len(open_now), "drivers": d, "drivers_prior": drivers(prev),
           "sla_missed": [t["id"] for t in cm], "sla_missed_prior": [t["id"] for t in pm],
           "csat_good": len(good), "csat_bad": len(bad), "csat_rated": rated,
           "detractors": [{"id": t["id"], "category": t["category"], "comment": t["csat"]["comment"]} for t in bad],
           "macro_candidates": macro_c, "kb_gap_candidates": kb_c, "kb_loaded": bool(kb["articles"] or kb["macros"])}
    if a.json:
        res["warnings"] = warnings(meta) + nosolved
        print(json.dumps(redact_obj(res), indent=1))
        return
    print(f"# Weekly support report, {start.date()} to {now.date()} (as of {iso(now)}, {src})")
    print(f"Source: {meta['source']} export, {len(tickets)} tickets.")
    for w in warnings(meta) + nosolved:
        print(f"Warning: {w}")
    print("\n## Volume")
    print(f"- Created this window: {len(cur)} (prior window: {len(prev)}; change {delta:+d}, {pct})")
    print(f"- Open right now (new/open/pending/hold): {len(open_now)}")
    print("\n## Top drivers (this window)")
    prev_d = dict(drivers(prev))
    print("| Category | Tickets | Prior | Ticket IDs |")
    print("|---|---|---|---|")
    for c, ids in d:
        print(f"| {c} | {len(ids)} | {len(prev_d.get(c, []))} | {', '.join(ids)} |")
    print("\n## SLA")
    print(f"- SLA misses among tickets created this window: {len(cm)}"
          + (f" ({', '.join(t['id'] for t in cm)})" if cm else "")
          + f"; prior window: {len(pm)}" + (f" ({', '.join(t['id'] for t in pm)})" if pm else ""))
    print("\n## CSAT (tickets created this window)")
    if rated:
        print(f"- Rated: {rated}; good {len(good)}, bad {len(bad)}; good share {len(good) / rated * 100:.1f}%")
    else:
        print("- No ratings in this window.")
    for t in bad:
        print(f"- Detractor {t['id']} ({t['category']}): \"{redact(t['csat']['comment']) or 'no comment'}\"")
    print(f"\n## Macro candidates (>= {a.min} tickets, no macro in category)")
    if not res["kb_loaded"]:
        print("- No KB folder given (--kb); cannot check macro or article coverage.")
    for c, ids in macro_c:
        print(f"- {c}: {len(ids)} tickets ({', '.join(ids)})")
    if res["kb_loaded"] and not macro_c:
        print("- none")
    print(f"\n## KB-gap candidates (>= {a.min} tickets, no article in category)")
    for c, ids in kb_c:
        print(f"- {c}: {len(ids)} tickets ({', '.join(ids)})")
    if res["kb_loaded"] and not kb_c:
        print("- none")


def cmd_normalize(a):
    tickets, meta = load(a.export, tzarg(a.tz))

    def enc(o):
        return iso(o) if isinstance(o, datetime) else str(o)

    meta = dict(meta, warnings=warnings(meta))
    print(json.dumps(redact_obj({"meta": meta, "tickets": tickets}), default=enc, indent=1))


def cmd_days(a):
    x, y = parse_ts(a.a, timezone.utc), parse_ts(a.b, timezone.utc)
    if not x or not y:
        sys.exit("could not parse dates; use YYYY-MM-DD")
    print(f"{(y.date() - x.date()).days} days from {x.date()} to {y.date()}")


def cmd_redact(a):
    sys.stdout.write(redact(sys.stdin.read()))


def tzarg(s):
    """--tz accepts an IANA zone (America/Chicago; handles daylight saving)
    or a fixed offset (+05:30)."""
    m = re.fullmatch(r"([+-])(\d{2}):?(\d{2})", s or "+00:00")
    if not m:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(s)
        except Exception:
            sys.exit("--tz must be an IANA zone like America/Chicago or an offset like +05:30")
    mins = int(m.group(2)) * 60 + int(m.group(3))
    return timezone(timedelta(minutes=mins if m.group(1) == "+" else -mins))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("export", help="path, 'sample', 'sample-freshdesk', or - for stdin")
        p.add_argument("--now")
        p.add_argument("--kb")
        p.add_argument("--rules")
        p.add_argument("--tz", default="+00:00")
        p.add_argument("--datefmt", help="strptime format for slash dates, e.g. '%%m/%%d/%%Y %%H:%%M'")
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("triage"); common(p); p.add_argument("--top", type=int, default=0)
    p.set_defaults(fn=cmd_triage)
    p = sub.add_parser("ticket"); common(p); p.add_argument("id"); p.set_defaults(fn=cmd_ticket)
    p = sub.add_parser("weekly"); common(p); p.add_argument("--days", type=int, default=7)
    p.add_argument("--min", type=int, default=3); p.set_defaults(fn=cmd_weekly)
    p = sub.add_parser("normalize"); p.add_argument("export"); p.add_argument("--tz", default="+00:00")
    p.set_defaults(fn=cmd_normalize)
    p = sub.add_parser("days"); p.add_argument("a"); p.add_argument("b"); p.set_defaults(fn=cmd_days)
    p = sub.add_parser("redact"); p.set_defaults(fn=cmd_redact)
    a = ap.parse_args()
    global DATEFMT
    DATEFMT = getattr(a, "datefmt", None)
    a.fn(a)


if __name__ == "__main__":
    main()
