#!/usr/bin/env python3
"""Check a grant draft before anyone sees it: word limits, source tags, and
numbers that do not match the cited fact.

Usage:
  python3 draft_check.py DRAFT.md [--profile profile.md] [--rfp rfp.md] [--today 2026-10-02]
  python3 draft_check.py --lint-profile profile.md [--today 2026-10-02]

Draft format:
  Each answer starts with a heading such as
    ## Q2. Program design [limit: 400 words]
  (a "(400 words)" suffix also works; if the heading has no limit and --rfp is
  given, the limit is taken from the RFP heading with the same Q number).
  Claims carry tags: [source: profile#F03], [source: profile#reading-buddies]
  (a profile heading), [source: https://...], [source: <file name>], or
  [NEEDS DATA: what is missing].

Rules:
  words      = whitespace-separated tokens after removing tags and markdown
               symbols (what the funder will count once tags are stripped)
  chars      = characters of that same text, spaces included
  over limit = words (or chars, for "N characters" limits) > limit (FAIL)
  untagged   = a sentence containing a digit, $ or % that has no tag (FAIL).
               Grade bands like K-3 and labels like Q2/F03 are not counted.
  mismatch   = a number in a sentence tagged profile#X that does not appear in
               fact X, or in the prose of section X (tables need a fact ID) (FAIL)
  needs-data = a number whose only tag is [NEEDS DATA] (FAIL: no unsourced numbers)
  verify     = numbers tagged with a URL or file are listed for a manual check
  Only a #/## heading (or another Q heading) ends an answer; ### subheadings
  inside an answer are counted.
  stale      = a cited fact whose "As of" month is more than 18 months before
               today (WARN)
Exit code 1 on any FAIL, so a loop can run until clean.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

TAG = re.compile(r"\[(?:source|src)\s*:\s*([^\]]+)\]|\[NEEDS DATA[^\]]*\]", re.I)
NUM = re.compile(r"(?<![A-Za-z])(?<![A-Za-z]-)\$?\d(?:[\d,]*\d)?(?:\.\d+)?%?")
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
LIMIT = re.compile(r"(\d[\d,]*)\s*(words?|characters?|chars?)\b", re.I)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def norm_num(s):
    s = s.replace("$", "").replace(",", "").rstrip("%").rstrip(".")
    try:
        f = float(s)
    except ValueError:
        return s
    return str(int(f)) if f == int(f) else str(f)


def nums_in(text):
    return {norm_num(m) for m in NUM.findall(text)}


def load_profile(path):
    """Return {anchor: text}, {fact_id: as_of} from a Grant Desk profile."""
    anchors, as_of = {}, {}
    current, buf = None, []
    lines = Path(path).read_text().splitlines()
    for ln in lines:
        m = HEAD.match(ln)
        if m:
            if current:
                anchors[current] = "\n".join(buf)
            current, buf = slugify(m.group(2)), []
            continue
        if not ln.strip().startswith("|"):
            buf.append(ln)  # heading anchors cover prose only; table numbers need a fact ID
        cells = [c.strip() for c in ln.strip().strip("|").split("|")] if ln.strip().startswith("|") else []
        if len(cells) >= 3 and re.fullmatch(r"[A-Z]{1,3}\d{1,3}", cells[0]):
            anchors[cells[0].upper()] = " ".join(cells[1:])
            if len(cells) >= 5:
                as_of[cells[0].upper()] = (cells[3], cells[4])
    if current:
        anchors[current] = "\n".join(buf)
    return anchors, as_of


def months_old(as_of, today):
    m = re.match(r"(\d{4})-(\d{2})", as_of or "")
    if not m:
        return None
    return (today.year - int(m.group(1))) * 12 + (today.month - int(m.group(2)))


def lint_profile(path, today):
    anchors, as_of = load_profile(path)
    ids = [k for k in anchors if re.fullmatch(r"[A-Z]{1,3}\d{1,3}", k)]
    print(f"# Profile lint: {path}\n- facts: {len(ids)}")
    bad = 0
    for fid in ids:
        src, when = as_of.get(fid, ("", ""))
        age = months_old(when, today)
        if not src or src.lower() in ("", "n/a", "tbd", "?"):
            print(f"- FAIL {fid}: no source")
            bad += 1
        if age is None:
            print(f"- FAIL {fid}: 'As of' must be YYYY-MM, got {when!r}")
            bad += 1
        elif age > 18:
            print(f"- WARN {fid}: as of {when} ({age} months old); refresh before citing")
    print("- result: " + ("FAIL" if bad else "ok"))
    return 1 if bad else 0


def parse_limit(m):
    unit = "chars" if m.group(2).lower().startswith("char") else "words"
    return int(m.group(1).replace(",", "")), unit


def rfp_limits(path):
    lim = {}
    for ln in Path(path).read_text().splitlines():
        m = HEAD.match(ln)
        if m:
            q = re.match(r"(Q\d+)", m.group(2).strip(), re.I)
            w = LIMIT.search(m.group(2))
            if q and w:
                lim[q.group(1).upper()] = parse_limit(w)
    return lim


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\[\"(])", text)
    out = []
    lead = re.compile(r"^\s*((?:\[(?:source|src)\s*:[^\]]+\]\s*|\[NEEDS DATA[^\]]*\]\s*)+)", re.I)
    for p in parts:
        m = lead.match(p)
        if out and m:  # tags that trail the previous sentence's period
            out[-1] += " " + m.group(1).strip()
            p = p[m.end():]
        if p.strip():
            out.append(p)
    return [p for p in out if p.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft", nargs="?")
    ap.add_argument("--profile")
    ap.add_argument("--rfp")
    ap.add_argument("--lint-profile")
    ap.add_argument("--today")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    if a.lint_profile:
        sys.exit(lint_profile(a.lint_profile, today))
    if not a.draft:
        ap.error("give a DRAFT.md or --lint-profile")

    anchors, as_of = load_profile(a.profile) if a.profile else ({}, {})
    limits = rfp_limits(a.rfp) if a.rfp else {}
    sections, cur = [], None
    for ln in Path(a.draft).read_text().splitlines():
        m = HEAD.match(ln)
        if m and re.match(r"Q\d+", m.group(2).strip(), re.I):
            title = m.group(2).strip()
            lm = LIMIT.search(title)
            q = re.match(r"(Q\d+)", title, re.I).group(1).upper()
            limit = parse_limit(lm) if lm else limits.get(q)
            cur = {"q": q, "title": title, "limit": limit, "lines": []}
            sections.append(cur)
        elif m and len(m.group(1)) <= 2:
            cur = None  # a # or ## heading that is not a question ends the answer (e.g. "## Sources")
        elif cur is not None:
            cur["lines"].append(ln)

    if not sections:
        sys.exit("No answer headings found. Use '## Q1. Title [limit: 300 words]'.")
    fails, warns, needs, verify = [], [], [], []
    print(f"# Draft check: {a.draft}  (today {today})\n")
    print("| Section | Words | Limit | Chars | Tags | NEEDS DATA | Status |")
    print("|---|---|---|---|---|---|---|")
    for s in sections:
        body = "\n".join(s["lines"]).strip()
        plain = TAG.sub("", body)
        plain = re.sub(r"[*_`>#]|^\s*[-+]\s+|^\s*\d+\.\s+", " ", plain, flags=re.M)
        plain = re.sub(r"\s+([.,;:!?])", r"\1", plain)
        words = len(plain.split())
        chars = len(re.sub(r"\s+", " ", plain).strip())
        tags = TAG.findall(body)
        nd = re.findall(r"\[NEEDS DATA[^\]]*\]", body, re.I)
        needs += [(s["q"], n) for n in nd]
        status, lim_txt = "ok", "-"
        if s["limit"] is None:
            status = "no limit found"
            warns.append(f"{s['q']}: no word or character limit in heading or RFP")
        else:
            n, unit = s["limit"]
            used = words if unit == "words" else chars
            lim_txt = f"{n} {unit}"
            if used > n:
                status = f"OVER by {used - n} {unit}"
                fails.append(f"{s['q']}: {used} {unit}, limit {n} (cut {used - n})")
        print(f"| {s['title'][:48]} | {words} | {lim_txt} | {chars} | {len(tags)} | {len(nd)} | {status} |")

        for sent in split_sentences(re.sub(r"\s+", " ", body)):
            bare = re.sub(r"\s+([.,;:!?])", r"\1", TAG.sub("", sent))
            found = NUM.findall(bare)
            cites = [t.strip() for t in re.findall(r"\[(?:source|src)\s*:\s*([^\]]+)\]", sent, re.I)]
            has_nd = bool(re.search(r"\[NEEDS DATA", sent, re.I))
            if found and not cites:
                if has_nd:
                    fails.append(f"{s['q']}: number(s) {', '.join(found)} next to [NEEDS DATA] have no source; "
                                 f"remove them until sourced: \"{bare.strip()[:100]}\"")
                else:
                    fails.append(f"{s['q']}: untagged number(s) {', '.join(found)} in: \"{bare.strip()[:110]}\"")
                continue
            prof = []
            for c in cites:
                for part in re.split(r"[;,]\s*", c):
                    part = part.strip()
                    if found and part and not part.lower().startswith("profile#"):
                        verify.append((s["q"], part, ", ".join(found)))
                    if part.lower().startswith("profile#"):
                        key = part.split("#", 1)[1].strip()
                        key = key.upper() if re.fullmatch(r"[A-Za-z]{1,3}\d{1,3}", key) else slugify(key)
                        if anchors and key not in anchors:
                            hits = [k for k in anchors if k.startswith(key)]
                            key = hits[0] if len(hits) == 1 else key
                        if anchors and key not in anchors:
                            fails.append(f"{s['q']}: tag profile#{key} not found in profile")
                        else:
                            prof.append(key)
                        when = as_of.get(key, ("", ""))[1]
                        age = months_old(when, today)
                        if age is not None and age > 18:
                            warns.append(f"{s['q']}: cites {key} as of {when} ({age} months old)")
            if anchors and prof and found:
                pool = set()
                for k in prof:
                    pool |= nums_in(anchors.get(k, ""))
                missing = [n for n in found if norm_num(n) not in pool]
                if missing:
                    fails.append(f"{s['q']}: {', '.join(missing)} not in cited {', '.join('profile#' + k for k in prof)}: "
                                 f"\"{bare.strip()[:100]}\"")
    print()
    if needs:
        print("## NEEDS DATA (fill or remove before submitting)")
        for q, n in needs:
            print(f"- {q}: {n}")
        print()
    if verify:
        print("## Claims to verify by hand (external or file sources are not machine-checked)")
        print("| Q | Source | Numbers |\n|---|---|---|")
        for q, src, ns in verify:
            print(f"| {q} | {src} | {ns} |")
        print("Budget figures: run budget_check.py --narrative. URLs: open each and confirm the number.\n")
    if warns:
        print("## Warnings")
        for w in dict.fromkeys(warns):
            print(f"- WARN {w}")
        print()
    if fails:
        print("## Must fix")
        for f in fails:
            print(f"- FAIL {f}")
        print("\nResult: FAIL")
        sys.exit(1)
    print("Result: PASS (word limits met, every number tagged and matched to its source)")


if __name__ == "__main__":
    main()
