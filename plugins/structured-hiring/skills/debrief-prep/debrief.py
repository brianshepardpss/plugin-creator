#!/usr/bin/env python3
"""Build a debrief packet for ONE candidate from interviewer scorecards.

Usage:
  python3 debrief.py <scorecards> --candidate "<name>" [--kit kit.json]
                     [--as-of YYYY-MM-DD] [--thin-words 12] [--json]

<scorecards> may be:
  * normalized JSON  {"interviews": [{candidate, session, interviewer, date,
                      submitted_at|null, ratings{comp: 1-4 or label},
                      evidence{comp: text}, notes}]}   (see schema.md)
  * a Greenhouse-style export JSON (has "scorecards": [...])
  * an Ashby-style feedback CSV ("<Competency> - Score" / "<Competency> - Notes")

What it computes (all counts, no scores):
  * scorecard status: submitted, missing (with days since the interview as of
    --as-of), and late (submitted more than 1 day after the interview)
  * evidence matrix: competency x interviewer, rating label and quote
  * disagreements: a competency with at least one positive rating
    (Yes/Strong Yes, 3-4) and at least one negative rating (No/Strong No, 1-2).
    Reported as "<p> positive vs <n> negative" -- ratings are never averaged.
  * coverage gaps: kit competencies with no submitted evidence, and
    competencies resting on a single interviewer
  * rating/evidence mismatches: a rating whose evidence is empty or shorter
    than --thin-words words (default 12); flagged "strong" for 1 or 4 ratings
  * fairness flags: fairness_lint.py (mode feedback) over every evidence and
    note field; a flagged sentence inside evidence is replaced by
    "[excluded: flagged remark, see section 6]" in the matrix, the
    disagreement quotes and the evidence word count

What it never does: produce an overall score, an average, a ranking, a fit
percentage or a hire/no-hire recommendation. Interviewers' overall votes are
deliberately left out so the debrief starts from evidence.

Privacy: emails, phone numbers and URLs in free text are redacted; contact,
address and EEO/demographic fields in exports are dropped and never read
beyond detecting that they were present.
"""
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import importlib.util  # noqa: E402

sys.dont_write_bytecode = True

_spec = importlib.util.spec_from_file_location(
    "fairness_lint", Path(__file__).resolve().parent.parent / "fairness-lint" / "fairness_lint.py")
_fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fl)
lint = _fl.lint

LABELS = {1: "Strong No", 2: "No", 3: "Yes", 4: "Strong Yes"}
TEXT_LABELS = {"definitely_not": 1, "definitely not": 1, "strong no": 1, "strong_no": 1, "no": 2,
               "mixed": "mixed", "yes": 3, "strong yes": 4, "strong_yes": 4}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
URL = re.compile(r"https?://\S+|\b(?:www\.)?linkedin\.com/\S+", re.I)
EEO_KEYS = {"eeoc", "eeo", "demographics", "gender", "race", "ethnicity", "veteran_status",
            "disability_status", "date_of_birth", "age", "pronouns"}


def redact(text):
    text = text or ""
    n = 0
    for rx, tag in ((EMAIL, "[email removed]"), (URL, "[link removed]"), (PHONE, "[phone removed]")):
        text, k = rx.subn(tag, text)
        n += k
    return text, n


EXCLUDED = "[excluded: flagged remark, see section 6]"


def exclude_flagged(text):
    """Replace every sentence that trips the fairness lint with EXCLUDED, so
    flagged remarks never appear as evidence or count toward its length."""
    out = []
    for sent in re.split(r"(?<=[.!?;])\s+", text.strip()):
        if not sent:
            continue
        piece = EXCLUDED if lint(sent, "feedback") else sent
        if not (piece == EXCLUDED and out and out[-1] == EXCLUDED):
            out.append(piece)
    return " ".join(out)


def rating(v):
    """Return (value, label): value is 1-4 or 'mixed'; None if unrated."""
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        v = int(v)
        return (v, LABELS[v]) if v in LABELS else None
    s = str(v).strip().lower()
    m = re.match(r"^([1-4])\b", s)
    if m:
        k = int(m.group(1))
        return k, LABELS[k]
    k = TEXT_LABELS.get(s)
    if k is None:
        return None
    return (k, "Mixed") if k == "mixed" else (k, LABELS[k])


def find_eeo(obj, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in EEO_KEYS and v not in (None, "", {}, []):
                hits.append(path + k)
            else:
                hits += find_eeo(v, path + k + ".")
    elif isinstance(obj, list):
        for v in obj:
            hits += find_eeo(v, path)
    return hits


def load_normalized(d):
    return d.get("interviews", []), find_eeo({k: v for k, v in d.items() if k != "interviews"})


def load_greenhouse(d):
    cand = d.get("candidate", {})
    name = " ".join(x for x in (cand.get("first_name"), cand.get("last_name")) if x) or cand.get("name", "")
    rows = []
    for sc in d.get("scorecards", []):
        attrs = sc.get("attributes", [])
        names = [a.get("name", "") for a in attrs]
        ev, notes = {}, []
        for a in attrs:
            if a.get("note"):
                ev[a["name"]] = a["note"]
        for q in sc.get("questions", []):
            ans = (q.get("answer") or "").strip()
            if not ans:
                continue
            qtext = q.get("question") or ""
            comp = next((n for n in names if n and n.lower() in qtext.lower()), None)
            if comp:
                ev[comp] = (ev.get(comp, "") + " " + ans).strip()
            else:
                notes.append(ans)
        who = (sc.get("submitted_by") or sc.get("interviewer") or {}).get("name", "unknown")
        rows.append({"candidate": name, "session": sc.get("interview") or (sc.get("interview_step") or {}).get("name", ""),
                     "interviewer": who, "date": (sc.get("interviewed_at") or "")[:10],
                     "submitted_at": (sc.get("submitted_at") or "")[:10] or None,
                     "ratings": {a["name"]: a.get("rating") for a in attrs if a.get("rating")},
                     "evidence": ev, "notes": " ".join(notes)})
    for si in d.get("scheduled_interviews", []):
        for iv in si.get("interviewers", []):
            if iv.get("scorecard_id") is None:
                rows.append({"candidate": name, "session": (si.get("interview") or {}).get("name", ""),
                             "interviewer": iv.get("name", "unknown"),
                             "date": ((si.get("start") or {}).get("date_time") or "")[:10],
                             "submitted_at": None, "ratings": {}, "evidence": {}, "notes": ""})
    return rows, find_eeo(d)


def load_ashby_csv(path):
    rows, eeo = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        heads = rd.fieldnames or []
        score_cols = {m.group(1).strip(): h for h in heads
                      if (m := re.match(r"^(.*?)\s*[-:]\s*(score|rating)$", h, re.I))}
        note_cols = {m.group(1).strip(): h for h in heads
                     if (m := re.match(r"^(.*?)\s*[-:]\s*(notes|evidence|comments)$", h, re.I))}
        eeo = [h for h in heads if h.strip().lower().replace(" ", "_") in EEO_KEYS]

        def col(r, *names):
            for n in names:
                for h in heads:
                    if h.strip().lower() == n:
                        return (r.get(h) or "").strip()
            return ""
        for r in rd:
            if not any((v or "").strip() for v in r.values()):
                continue
            comps = set(score_cols) | set(note_cols)
            rows.append({"candidate": col(r, "candidate name", "candidate"),
                         "session": col(r, "interview", "interview name", "stage"),
                         "interviewer": col(r, "interviewer", "submitted by"),
                         "date": col(r, "interview date", "date")[:10],
                         "submitted_at": col(r, "submitted at", "submitted")[:10] or None,
                         "ratings": {c: r.get(score_cols[c]) for c in comps if c in score_cols and (r.get(score_cols[c]) or "").strip()},
                         "evidence": {c: r.get(note_cols[c]) for c in comps if c in note_cols and (r.get(note_cols[c]) or "").strip()},
                         "notes": col(r, "additional notes", "notes", "comments")})
    return rows, eeo


def load(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return load_ashby_csv(p)
    d = json.loads(p.read_text(encoding="utf-8"))
    return load_greenhouse(d) if "scorecards" in d else load_normalized(d)


def days(a, b):
    try:
        return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
    except (TypeError, ValueError):
        return None


def build(rows, candidate, kit=None, as_of=None, thin=12):
    mine = [r for r in rows if candidate.lower() in (r.get("candidate") or "").lower()]
    if not mine:
        names = sorted({r.get("candidate") for r in rows})
        raise SystemExit(f"No interviews for {candidate!r}. Candidates in file: {', '.join(names)}")
    names = sorted({r["candidate"] for r in mine})
    if len(names) > 1:
        raise SystemExit(f"{candidate!r} matches several candidates: {', '.join(names)}. Be more specific.")
    as_of = as_of or dt.date.today().isoformat()
    redactions = 0
    submitted, missing, late = [], [], []
    for r in mine:
        if r.get("submitted_at"):
            submitted.append(r)
            lag = days(r.get("date"), r["submitted_at"])
            if lag is not None and lag > 1:
                late.append((r, lag))
        else:
            missing.append((r, days(r.get("date"), as_of)))

    kit_comps = [c["name"] for c in (kit or {}).get("competencies", [])]
    seen_comps = []
    for r in submitted:
        for c in list(r.get("ratings", {})) + list(r.get("evidence", {})):
            if c not in seen_comps:
                seen_comps.append(c)
    comps = kit_comps + [c for c in seen_comps if c not in kit_comps]

    matrix = {c: [] for c in comps}
    mismatches, flags = [], []
    for r in submitted:
        who = f"{r['interviewer']} ({r['session']})"
        for c in comps:
            rt = rating(r.get("ratings", {}).get(c))
            ev_raw = (r.get("evidence", {}).get(c) or "").strip()
            if rt is None and not ev_raw:
                continue
            ev = exclude_flagged(redact(ev_raw)[0])
            matrix[c].append({"interviewer": r["interviewer"], "session": r["session"],
                              "value": rt[0] if rt else None, "label": rt[1] if rt else "unrated", "evidence": ev})
            words = len(ev.replace(EXCLUDED, "").split())
            if rt and words < thin:
                strong = rt[0] in (1, 4)
                mismatches.append({"interviewer": r["interviewer"], "competency": c, "label": rt[1],
                                   "evidence": ev or "(none)", "words": words, "strong": strong})
        texts = [(c, r.get("evidence", {}).get(c) or "") for c in r.get("evidence", {})] + [("notes", r.get("notes") or "")]
        for field, t in texts:
            t2, k = redact(t)
            redactions += k
            for f in lint(t2, "feedback"):
                flags.append({"interviewer": r["interviewer"], "field": field, **f})

    flags.sort(key=lambda f: ({"high": 0, "medium": 1, "low": 2}[f["severity"]], f["interviewer"]))
    disagreements = []
    for c, cells in matrix.items():
        pos = [x for x in cells if x["value"] in (3, 4)]
        neg = [x for x in cells if x["value"] in (1, 2)]
        if pos and neg:
            disagreements.append({"competency": c, "positive": pos, "negative": neg,
                                  "mixed": [x for x in cells if x["value"] == "mixed"]})

    planned = {}
    for s in (kit or {}).get("sessions", []):
        for c in s.get("competencies", []):
            planned.setdefault(c, []).append(s["name"])
    gaps, single = [], []
    for c in comps:
        evid = [x for x in matrix[c] if x["evidence"]]
        if not evid:
            why = [f"{r['interviewer']} ({r['session']}) has not submitted" for r, _ in missing
                   if r["session"] in planned.get(c, [])]
            gaps.append({"competency": c, "why": "; ".join(why) or "no session in this loop covered it"})
        elif len({x["interviewer"] for x in evid}) == 1:
            single.append({"competency": c, "interviewer": evid[0]["interviewer"]})

    return {"candidate": names[0], "as_of": as_of, "role": (kit or {}).get("role", ""),
            "req_id": (kit or {}).get("req_id", ""),
            "counts": {"interviews": len(mine), "submitted": len(submitted), "missing": len(missing)},
            "missing": [{"interviewer": r["interviewer"], "session": r["session"], "date": r.get("date"),
                         "days_since_interview": d} for r, d in missing],
            "late": [{"interviewer": r["interviewer"], "session": r["session"], "days_after_interview": lag} for r, lag in late],
            "competencies": comps, "matrix": matrix, "disagreements": disagreements,
            "gaps": gaps, "single_source": single, "mismatches": mismatches,
            "fairness_flags": flags, "redactions": redactions}


def cell(s):
    return (s or "").replace("|", "/").replace("\n", " ")


def render(p, eeo):
    L = []
    head = f"# Debrief packet: {p['candidate']}"
    if p["role"]:
        head += f" -- {p['role']}" + (f" ({p['req_id']})" if p["req_id"] else "")
    L += [head, "",
          f"As of {p['as_of']}. AI-drafted, human decision required. This packet organizes interviewer "
          "evidence. It does not score, rank or recommend, and interviewers' overall votes are left out "
          "so the discussion starts from evidence.", ""]
    if eeo:
        L += [f"> Privacy: the input contained EEO/demographic fields ({', '.join(sorted(set(eeo)))}). "
              "They were dropped and not used. Do not paste EEO data into hiring discussions.", ""]
    if p["redactions"]:
        L += [f"> Privacy: {p['redactions']} email/phone/link value(s) were removed from interviewer text.", ""]
    c = p["counts"]
    L += ["## 1. Scorecard status", "",
          f"- Submitted: {c['submitted']} of {c['interviews']} interviews."]
    for m in p["missing"]:
        d = m["days_since_interview"]
        L.append(f"- MISSING: {m['interviewer']} ({m['session']}, interviewed {m['date']})"
                 + (f" -- {d} day(s) since the interview." if d is not None else "."))
    for l in p["late"]:
        L.append(f"- Late: {l['interviewer']} ({l['session']}) submitted {l['days_after_interview']} days after the interview; "
                 "memory-based notes are less reliable.")
    L += ["", "## 2. Evidence matrix (competency x interviewer)", "",
          "| Competency | Interviewer (session) | Rating | Evidence |", "|---|---|---|---|"]
    for comp in p["competencies"]:
        cells = p["matrix"][comp]
        if not cells:
            L.append(f"| {comp} | -- | -- | NO EVIDENCE |")
        for x in cells:
            L.append(f"| {comp} | {x['interviewer']} ({x['session']}) | {x['label']} | \"{cell(x['evidence'])}\" |")
    L += ["", "## 3. Where interviewers disagree", ""]
    if not p["disagreements"]:
        L.append("- No competency has both positive and negative ratings.")
    for d in p["disagreements"]:
        L.append(f"- **{d['competency']}**: {len(d['positive'])} positive vs {len(d['negative'])} negative.")
        for x in d["positive"] + d["negative"]:
            L.append(f"  - {x['interviewer']} ({x['label']}): \"{cell(x['evidence'])}\"")
    L += ["", "## 4. Coverage gaps", ""]
    if not p["gaps"] and not p["single_source"]:
        L.append("- Every competency has evidence from at least two interviewers.")
    for g in p["gaps"]:
        L.append(f"- **{g['competency']}**: no evidence. {g['why']}.")
    for s in p["single_source"]:
        L.append(f"- {s['competency']}: evidence from one interviewer only ({s['interviewer']}).")
    L += ["", "## 5. Ratings without supporting evidence", ""]
    if not p["mismatches"]:
        L.append("- None: every rating has at least a sentence of evidence.")
    for m in p["mismatches"]:
        tag = "STRONG RATING, THIN EVIDENCE" if m["strong"] else "thin evidence"
        L.append(f"- {tag}: {m['interviewer']} rated {m['competency']} \"{m['label']}\" with {m['words']} word(s) "
                 f"of evidence: \"{cell(m['evidence'])}\"")
    L += ["", "## 6. Fairness flags (non-job-related remarks)", ""]
    if not p["fairness_flags"]:
        L.append("- No flags. A clean lint is not a guarantee; the facilitator still listens for them.")
    for f in p["fairness_flags"]:
        L.append(f"- [{f['severity']}] {f['interviewer']} ({f['field']}): \"{f['match']}\" in \"{cell(f['context'])}\" "
                 f"-- {f['category']}: {f['reason']} Fix: {f['suggestion']}")
    L += ["", "## 7. Questions for the debrief (seeds; edit before use)", ""]
    qs = []
    for d in p["disagreements"]:
        qs.append(f"{d['competency']}: {', '.join(x['interviewer'] for x in d['positive'])} saw it positively and "
                  f"{', '.join(x['interviewer'] for x in d['negative'])} negatively. What did each of you observe, "
                  "and which observation maps to which rubric anchor?")
    for g in p["gaps"]:
        qs.append(f"{g['competency']} has no evidence. Do we wait for the missing scorecard, add a follow-up, "
                  "or decide without it and record that?")
    for m in [m for m in p["mismatches"] if m["strong"]]:
        qs.append(f"{m['interviewer']}: what specific behaviour supports \"{m['label']}\" on {m['competency']}?")
    if p["fairness_flags"]:
        who = sorted({f["interviewer"] for f in p["fairness_flags"]})
        qs.append(f"Set aside the flagged remarks ({', '.join(who)}). Is the remaining job-related evidence enough?")
    for i, q in enumerate(qs[:6], 1):
        L.append(f"{i}. {q}")
    L += ["", "## 8. Decision memo (the hiring team fills this in)", "",
          "- Decision and decider: ______ (made by people, after discussion)",
          "- Evidence relied on, by competency: ______",
          "- Open risks and how they will be checked (references, follow-up interview): ______",
          "- Flagged remarks excluded from the decision: ______",
          "- Missing scorecards and how they were handled: ______", "",
          "AI-drafted, human decision required."]
    return "\n".join(L)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    cand = opt("--candidate")
    rows, eeo = load(a[0])
    if not cand:
        names = sorted({r.get("candidate") for r in rows})
        if len(names) != 1:
            sys.exit("Pass --candidate. One candidate per packet (data minimization). In file: " + ", ".join(names))
        cand = names[0]
    kit = json.loads(Path(opt("--kit")).read_text()) if opt("--kit") else None
    p = build(rows, cand, kit, opt("--as-of"), int(opt("--thin-words", 12)))
    p["eeo_fields_dropped"] = sorted(set(eeo))
    print(json.dumps(p, indent=2) if "--json" in a else render(p, eeo))


if __name__ == "__main__":
    main()
