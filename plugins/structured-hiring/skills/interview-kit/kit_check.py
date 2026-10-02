#!/usr/bin/env python3
"""Check an interview kit JSON against the structured-interview rules.

Usage:
  python3 kit_check.py <kit.json> [--require-questions] [--json]

Kit shape (see SKILL.md): {"role", "competencies": [{"name", "definition",
"anchors": {"1".."4"}, "questions": [{"type": "behavioral"|"situational",
"text", "probes": [...]}]}], "sessions": [{"name", "competencies": [...],
"secondary": [...]}]}

Rules checked (each line reports PASS, WARN or FAIL):
  R1  4-6 competencies
  R2  every competency has a definition and anchors for exactly 1, 2, 3, 4
  R3  every competency has >= 2 behavioral and >= 1 situational question
  R4  every question has >= 1 probe
  R5  every competency is owned by exactly one session ("competencies");
      extra coverage must be listed under "secondary" (WARN otherwise)
  R6  every competency is owned by some session; every session competency
      exists in the kit
  R7  no question, definition or anchor trips fairness_lint (mode questions)
  R8  no competency or attribute is a personality trait or "culture fit"
FAIL on R1, R2, R6, R7, R8. WARN on R3, R4, R5 (kits used only as
scorecards, like samples/fernhill-robotics/kit.json, have no questions);
--require-questions turns R3 and R4 into FAIL, as the interview-kit skill
uses it.
"""
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

TRAIT = re.compile(r"\b(culture fit|cultural fit|personality|likeab\w*|charisma|energy|vibe|attitude|confidence|passion)\b", re.I)


def check(kit, require_questions=False):
    res = []

    def add(rule, status, msg):
        res.append({"rule": rule, "status": status, "message": msg})
    comps = kit.get("competencies", [])
    names = [c.get("name", "") for c in comps]
    n = len(comps)
    add("R1", "PASS" if 4 <= n <= 6 else "FAIL", f"{n} competencies (want 4-6)")
    for c in comps:
        a = c.get("anchors", {})
        ok = c.get("definition") and sorted(a) == ["1", "2", "3", "4"] and all(a.values())
        add("R2", "PASS" if ok else "FAIL", f"{c.get('name')}: definition and 1-4 anchors" + ("" if ok else " incomplete"))
        qs = c.get("questions", [])
        b = sum(1 for q in qs if q.get("type") == "behavioral")
        s = sum(1 for q in qs if q.get("type") == "situational")
        add("R3", "PASS" if b >= 2 and s >= 1 else ("FAIL" if require_questions else "WARN"), f"{c.get('name')}: {b} behavioral, {s} situational")
        nop = [q.get("text", "")[:50] for q in qs if not q.get("probes")]
        if qs:
            add("R4", "PASS" if not nop else ("FAIL" if require_questions else "WARN"), f"{c.get('name')}: " + ("all questions have probes" if not nop else f"no probes for: {nop}"))
        if TRAIT.search(c.get("name", "")):
            add("R8", "FAIL", f"{c.get('name')}: personality/culture-fit competency; rewrite as an observable, job-related skill")
    owners = {}
    for s in kit.get("sessions", []):
        for c in s.get("competencies", []):
            owners.setdefault(c, []).append(s.get("name"))
            if c not in names:
                add("R6", "FAIL", f"session '{s.get('name')}' assesses '{c}', which is not in the kit")
    for c in names:
        o = owners.get(c, [])
        if not o:
            add("R6", "FAIL", f"{c}: no session assesses it")
        elif len(o) > 1:
            add("R5", "WARN", f"{c}: owned by {len(o)} sessions ({', '.join(o)}); keep one owner and list the rest under 'secondary'")
    if not any(r["rule"] == "R6" for r in res):
        add("R6", "PASS", "every competency has an owner session")
    if not any(r["rule"] == "R5" for r in res):
        add("R5", "PASS", "no duplicated competency across sessions")
    text = []
    for c in comps:
        text.append(c.get("definition", ""))
        text += list(c.get("anchors", {}).values())
        for q in c.get("questions", []):
            text.append(q.get("text", ""))
            text += q.get("probes", [])
    flags = lint("\n".join(text), "questions")
    add("R7", "PASS" if not flags else "FAIL",
        "no fairness flags" if not flags else "; ".join(f"\"{f['match']}\" ({f['category']})" for f in flags))
    if not any(r["rule"] == "R8" for r in res):
        add("R8", "PASS", "no personality or culture-fit competencies")
    return res


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    res = check(json.loads(Path(a[0]).read_text(encoding="utf-8")), "--require-questions" in a)
    if "--json" in a:
        print(json.dumps(res, indent=2))
    else:
        for r in res:
            print(f"{r['status']:4} {r['rule']} {r['message']}")
        fails = sum(r["status"] == "FAIL" for r in res)
        warns = sum(r["status"] == "WARN" for r in res)
        print(f"\n{fails} fail, {warns} warn")


if __name__ == "__main__":
    main()
