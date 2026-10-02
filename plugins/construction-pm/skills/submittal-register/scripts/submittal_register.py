#!/usr/bin/env python3
"""Build a submittal register from spec section text. Standard library only.

Two steps:

  extract   spec text files -> candidates.csv (one row per submittal paragraph)
  finalize  candidates.csv + schedule CSV -> submittals.csv (numbered, dated)

Usage:
  python3 submittal_register.py extract SPEC.txt [SPEC.txt ...] --out candidates.csv
  python3 submittal_register.py finalize candidates.csv --schedule schedule.csv \
      --out submittals.csv [--as-of YYYY-MM-DD] [--review-days 14] [--buffer-days 7]
      [--default-lead-weeks 4] [--lead "08 71 00=12"] [--ntp DATE] [--sc DATE]
      [--existing old_submittals.csv]

How extract works (deterministic, auditable):
  * Section number and title come from the "SECTION NN NN NN" line.
  * Every paragraph (A., B., ...) inside a PART 1 article whose title contains
    "SUBMITTAL" becomes a row, except admin lines ("Submit under provisions of
    Section 01 33 00", "None required").
  * Paragraphs anywhere else that say "submit"/"submittal" or describe a
    mockup become rows marked "outside submittal article - verify".
  * A row outside the submittal articles that points back to "Article 1.x"
    with the same submittal type as a row in that article is marked as a
    duplicate (dup_of) and dropped by finalize.
  * Lead time: the largest "N weeks" / "N to M weeks" found in a paragraph
    that mentions lead time. "Long-lead" text sets the long-lead flag.
  * Spec deadlines: "within N days after Notice to Proceed" -> NTP+N;
    "at/before Substantial Completion" -> SC.

How finalize computes dates (calendar days, shown in the Working column):
  need date   = earliest Start in the schedule for an activity whose Spec
                Section equals the row's section.
  Action rows (product data, shop drawings, samples):
      submit by = need date - lead weeks x 7 - review days - buffer days
  Mockups:
      submit by = need date - review days
  Informational rows with a spec deadline: submit by = that deadline.
  Informational rows without one: submit with the section's earliest action
      submittal, or need date - review days if the section has none.
  Closeout rows: submit by = Substantial Completion (or the spec deadline).
  Lead weeks: --lead override for the section, else the spec text, else
      --default-lead-weeks (marked "assumed - confirm with supplier").
"""
import argparse
import csv
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

SEC_RE = re.compile(r"^\s*SECTION\s+(\d{2})\s?(\d{2})\s?(\d{2})((?:\.\d+)?)\b(.*)", re.I)
HEAD_RE = re.compile(r"^\s*SECTION\s+(\d{2})\s?(\d{2})\s?(\d{2})((?:\.\d+)?)\b([^a-z]*)$")
PART_RE = re.compile(r"^\s*PART\s+(\d|ONE|TWO|THREE)\b\s*[-.:]?\s*([A-Za-z ()/&,]*)$", re.I)
ART_RE = re.compile(r"^\s*(\d{1,2}\.\d{1,2})\.?\s+([A-Za-z][A-Za-z0-9 ,&/()'\-]+?)\s*[:.]?\s*$")
SMALL_WORDS = {"and", "or", "of", "for", "the", "to", "in", "a", "an", "with", "by", "on", "at"}


def is_article_title(t):
    """All caps, or Title Case (small words excepted), and short: a heading, not wrapped text."""
    if len(t) > 60:
        return False
    if t.upper() == t:
        return True
    words = [w for w in re.split(r"[\s,/&()-]+", t) if w]
    return all(w[0].isupper() or w.lower() in SMALL_WORDS for w in words)
PARA_RE = re.compile(r"^\s*([A-Z])\.\s+(.+)$")
SUB_RE = re.compile(r"^\s*(\d{1,2})\.\s+(.+)$")
SUBSUB_RE = re.compile(r"^\s*([a-z])\.\s+(.+)$")
ADMIN_RE = re.compile(r"^(submit (under|in accordance with|per) (the )?provisions|comply with section|"
                      r"none required|not used|general:?\s*$|submittal procedures:)", re.I)
SUBMIT_WORD_RE = re.compile(r"\bsubmit\b|\bmock-?ups?\b", re.I)

TYPE_RULES = [
    ("Mockup", r"mock-?up"),
    ("Warranty", r"warrant"),
    ("O&M Data", r"maintenance data|operation and maintenance|\bo&m\b"),
    ("Extra Stock", r"maintenance material|extra (stock|material)|attic stock"),
    ("Sample", r"\bsamples?\b|drawdown"),
    ("Qualification", r"qualification"),
    ("Test/Inspection Report", r"report"),
    ("Certificate", r"certif"),
    ("Plan/Procedure", r"\bplan\b|procedure"),
    ("Shop Drawing", r"shop drawing|schedule\b|wiring diagram|layout|riser|coordination drawing"),
    ("Product Data", r"product data|product list|data sheet"),
]
ACTION_TYPES = {"Product Data", "Shop Drawing", "Sample", "Mockup"}
CLOSEOUT_TYPES = {"Warranty", "O&M Data", "Extra Stock", "Closeout Document"}


def norm_section(s):
    digits = re.sub(r"\D", "", s or "")
    if len(digits) < 6:
        return (s or "").strip()
    return f"{digits[0:2]} {digits[2:4]} {digits[4:6]}"


def parse_date(s):
    """Accept 2026-10-05, 10/5/2026, 10/5/26, 05-Oct-26, 'Mon 10/5/26', '05-Oct-26 A'."""
    if not s:
        return None
    s = s.strip().rstrip("*").strip()
    s = re.sub(r"\s+A$", "", s)
    s = re.sub(r"^[A-Za-z]{3}\s+(?=\d)", "", s)
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%y", "%d-%b-%Y", "%d %b %Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def safe(v):
    """Stop spreadsheet formula injection."""
    v = "" if v is None else str(v)
    return "'" + v if v[:1] in ("=", "+", "@") else v


def read_spec(path):
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        exe = shutil.which("pdftotext")
        if not exe:
            return None, ("PDF given but pdftotext is not installed. Read the PDF yourself and save "
                          "its text, line by line, to a .txt file, then rerun on the .txt.")
        r = subprocess.run([exe, "-layout", str(p), "-"], capture_output=True, text=True)
        if r.returncode != 0:
            return None, f"pdftotext failed ({r.stderr.strip()[:200]}). Encrypted or damaged PDF?"
        return normalize(r.stdout), None
    return normalize(p.read_text(errors="replace")), None


def normalize(text):
    """Turn typographic dashes and quotes from Word/PDF into ASCII."""
    for a, b in (("\u2013", "-"), ("\u2014", "-"), ("\u2012", "-"), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " ")):
        text = text.replace(a, b)
    return text


def split_sections(text):
    """Split a multi-section file (project manual) at heading-style SECTION lines."""
    lines = text.splitlines()
    starts, seen = [], set()
    for i, ln in enumerate(lines):
        m = HEAD_RE.match(ln)
        if m:
            key = "".join(m.group(1, 2, 3, 4))
            if key not in seen:
                seen.add(key)
                starts.append(i)
    if len(starts) <= 1:
        return [text]
    starts[0] = 0
    return ["\n".join(lines[a:b]) for a, b in zip(starts, starts[1:] + [len(lines)])]


def item_name(text):
    m = re.match(r"^(.{3,70}?)[:.,]", text)
    return (m.group(1) if m else " ".join(text.split()[:8])).strip()


def classify(item, text):
    for t, pat in TYPE_RULES:
        if re.search(pat, item, re.I):
            return t
    hits = []
    for i, (t, pat) in enumerate(TYPE_RULES):
        m = re.search(pat, text, re.I)
        if m:
            hits.append((m.start(), i, t))
    return min(hits)[2] if hits else "Other"


def category_for(article_title, typ):
    t = article_title.upper()
    if "ACTION" in t:
        return "Action"
    if "INFORMATIONAL" in t:
        return "Informational"
    if "CLOSEOUT" in t or "MAINTENANCE MATERIAL" in t:
        return "Closeout"
    if typ in ACTION_TYPES:
        return "Action"
    if typ in CLOSEOUT_TYPES:
        return "Closeout"
    return "Informational"


def due_rule(text):
    m = re.search(r"within\s+(\d+)\s+(calendar\s+|working\s+|business\s+)?days\s+(after|of|following)\s+"
                  r"(the\s+)?(notice to proceed|ntp|award|contract award)", text, re.I)
    if m:
        kind = (m.group(2) or "").strip().lower()
        base = "NTP" if m.group(5).lower() in ("notice to proceed", "ntp") else "AWARD"
        return f"{base}+{m.group(1)}" + ("WD" if kind in ("working", "business") else "")
    if re.search(r"(at|before|prior to)\s+substantial completion", text, re.I):
        return "SC"
    return ""


def parse_paragraphs(text):
    """Return (section_id, title, paragraphs, warnings). Paragraph = dict."""
    lines = text.splitlines()
    sec, title = "", ""
    for i, ln in enumerate(lines[:15]):
        m = HEAD_RE.match(ln) or SEC_RE.search(ln)
        if m:
            sec = f"{m.group(1)} {m.group(2)} {m.group(3)}{m.group(4)}"
            title = m.group(5).strip(" -:\t")
            if not title:
                for nxt in lines[i + 1:i + 4]:
                    if nxt.strip() and not PART_RE.match(nxt):
                        title = nxt.strip()
                        break
            break
    footer = re.compile(r"(%s|%s)\s*-\s*\d+\b" % (re.escape(sec), re.escape(sec.replace(" ", ""))) if sec else r"$^")
    paras, part, art, cur = [], 0, None, None
    for n, raw in enumerate(lines, 1):
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if footer.search(ln) or re.match(r"^\s*END OF SECTION", ln, re.I) \
                or HEAD_RE.match(ln):
            continue
        m = PART_RE.match(ln)
        if m and (m.group(2).strip() or ln.strip().startswith("PART")):
            art, cur = None, None
            continue
        m = ART_RE.match(ln)
        if m and is_article_title(m.group(2).strip()):
            art, cur = (m.group(1), m.group(2).strip()), None
            part = int(m.group(1).split(".")[0])  # SectionFormat: article 1.x is in PART 1
            continue
        if art is None:
            continue
        m = PARA_RE.match(ln)
        if m:
            cur = {"part": part, "art": art[0], "art_title": art[1], "para": m.group(1),
                   "text": m.group(2).strip(), "subs": [], "line": n}
            paras.append(cur)
            continue
        m = SUB_RE.match(ln) or SUBSUB_RE.match(ln)
        if m and cur is not None:
            cur["subs"].append(f"{m.group(1)}. {m.group(2).strip()}")
            continue
        if cur is not None:
            if cur["subs"]:
                cur["subs"][-1] += " " + ln.strip()
            else:
                cur["text"] += " " + ln.strip()
    warnings = []
    if len(text.strip()) < 400:
        warnings.append("very little text - scanned PDF? OCR it and rerun")
    if not sec:
        warnings.append("no 'SECTION NN NN NN' line found")
    return sec, title, paras, warnings


def lead_info(paras):
    """Largest lead time stated in the section, with its article ref."""
    best, ref, longlead = None, "", False
    for p in paras:
        full = p["text"] + " " + " ".join(p["subs"])
        if re.search(r"long[- ]lead", full, re.I):
            longlead = True
        if not re.search(r"lead[- ]time|long[- ]lead|manufactur\w* and deliver", full, re.I):
            continue
        nums = [int(x) for pair in re.findall(r"(\d+)\s*(?:to|-)\s*(\d+)\s*weeks", full, re.I) for x in pair]
        nums += [int(x) for x in re.findall(r"(\d+)\s*weeks", full, re.I)]
        if nums and (best is None or max(nums) > best):
            best, ref = max(nums), f"{p['art']}.{p['para']}"
    return best, ref, longlead


def extract(args):
    rows, report = [], []
    chunks = []
    for f in args.files:
        text, err = read_spec(f)
        if err:
            report.append(f"SKIPPED {f}: {err}")
            continue
        parts = split_sections(text)
        if len(parts) > 1:
            report.append(f"NOTE    {Path(f).name} holds {len(parts)} sections; split at SECTION headings")
        chunks += [(f, t) for t in parts]
    for f, text in chunks:
        sec, title, paras, warns = parse_paragraphs(text)
        if not sec:
            report.append(f"SKIPPED {f}: " + "; ".join(warns))
            continue
        lead, lead_ref, longlead = lead_info(paras)
        orequal = [f"{p['art']}.{p['para']}" for p in paras
                   if re.search(r"or approved equal|or equal\b|comparable products", p["text"], re.I)]
        subst = [f"{p['art']}.{p['para']}" for p in paras if re.search(r"substitution", p["text"], re.I)]
        n_in, n_out, n_admin, n_dup = 0, 0, 0, 0
        sec_rows = []
        for p in paras:
            full = (p["text"] + " " + " ".join(p["subs"])).strip()
            in_article = p["part"] == 1 and "SUBMITTAL" in p["art_title"].upper()
            ref = f"{p['art']}.{p['para']}"
            if in_article and ADMIN_RE.search(p["text"]):
                n_admin += 1
                report.append(f"  {sec} {ref}: admin line skipped ({p['text'][:50]})")
                continue
            if not in_article and not SUBMIT_WORD_RE.search(full):
                continue
            item = item_name(p["text"])
            typ = classify(item, full)
            cat = category_for(p["art_title"] if in_article else "", typ)
            if cat == "Closeout" and typ not in CLOSEOUT_TYPES:
                typ = "Closeout Document"
            flags = []
            if longlead or lead:
                if cat == "Action" and typ != "Mockup":
                    flags.append("LONG-LEAD" if (longlead or (lead or 0) >= 8) else f"lead {lead} wk")
            if orequal and typ == "Product Data":
                flags.append(f"or-equal/substitution allowed ({', '.join(sorted(set(orequal + subst)))})")
            m = re.search(r"concurrently with section\s+(\d{2}\s?\d{2}\s?\d{2})", full, re.I)
            if m:
                flags.append(f"submit with {norm_section(m.group(1))}")
            origin = "submittal article" if in_article else "outside submittal article - verify"
            row = {
                "section": sec, "section_title": title, "ref": ref, "article_title": p["art_title"],
                "item": item, "type": typ, "category": cat, "description": full[:500],
                "due_rule": due_rule(full), "lead_weeks": lead if (cat == "Action" and lead) else "",
                "lead_source": f"spec {lead_ref}" if (cat == "Action" and lead) else "",
                "flags": "; ".join(flags), "origin": origin, "dup_of": "",
                "source_file": Path(f).name, "source_line": p["line"], "part": p["part"],
            }
            if not in_article:
                m = re.search(r"article\s+(\d{1,2}\.\d{1,2})", full, re.I)
                if m:
                    for r0 in sec_rows:
                        if r0["ref"].startswith(m.group(1) + ".") and r0["type"] == typ and r0["origin"] == "submittal article":
                            row["dup_of"] = f"{sec} {r0['ref']}"
                            n_dup += 1
                            break
                n_out += 1
            else:
                n_in += 1
            sec_rows.append(row)
        if n_in == 0 and n_admin == 0:
            warns.append("no PART 1 submittal article recognized - check the article headings by hand")
        rows += sec_rows
        report.insert(0, f"PARSED  {sec} {title} ({Path(f).name}): {n_in} in submittal articles, "
                         f"{n_out} found elsewhere, {n_admin} admin skipped, {n_dup} duplicates"
                      + (f"; lead time {lead} wk ({lead_ref})" if lead else "")
                      + ("; WARN " + "; ".join(warns) if warns else ""))
    cols = ["section", "section_title", "ref", "article_title", "item", "type", "category", "description",
            "due_rule", "lead_weeks", "lead_source", "flags", "origin", "dup_of", "source_file", "source_line", "part"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: safe(v) for k, v in r.items()})
    print("\n".join(report))
    print(f"\n{len(rows)} candidate rows ({sum(1 for r in rows if r['dup_of'])} marked duplicate) -> {args.out}")


def load_schedule(path):
    acts = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
            if not any(r.values()):
                continue
            name = r.get("activity name") or r.get("name") or r.get("task name") or ""
            start = parse_date(r.get("start") or r.get("start date") or "")
            finish = parse_date(r.get("finish") or r.get("finish date") or "") or start
            sec = norm_section(r.get("spec section") or r.get("section") or "")
            acts.append({"id": r.get("activity id") or r.get("id") or "", "name": name, "start": start, "finish": finish, "sec": sec})
    return acts


def finalize(args):
    acts = load_schedule(args.schedule)
    ntp = parse_date(args.ntp) if args.ntp else next(
        (a["start"] for a in acts if re.search(r"notice to proceed|\bntp\b", a["name"], re.I)), None)
    sc = parse_date(args.sc) if args.sc else next(
        (a["start"] for a in acts if re.search(r"substantial completion", a["name"], re.I)), None)
    as_of = parse_date(args.as_of) if args.as_of else dt.date.today()
    overrides = {}
    for o in args.lead or []:
        k, _, v = o.partition("=")
        overrides[norm_section(k)] = int(v)
    need, last = {}, {}
    for a in acts:
        if a["sec"] and a["finish"] and (a["sec"] not in last or a["finish"] > last[a["sec"]][0]):
            last[a["sec"]] = (a["finish"], f"{a['id']} {a['name']}".strip())
        if a["sec"] and a["start"]:
            if a["sec"] not in need or a["start"] < need[a["sec"]][0]:
                need[a["sec"]] = (a["start"], f"{a['id']} {a['name']}".strip())
    with open(args.candidates, newline="", encoding="utf-8-sig") as fh:
        cands = [r for r in csv.DictReader(fh)]
    dropped = [r for r in cands if r.get("dup_of")]
    cands = [r for r in cands if not r.get("dup_of")]
    R, B = args.review_days, args.buffer_days
    out = []
    for r in cands:
        sec = norm_section(r["section"])
        nd, nbasis = need.get(sec, (None, ""))
        flags = [f for f in (r.get("flags") or "").split("; ") if f]
        lw, lsrc = None, ""
        if r["category"] == "Action" and r["type"] != "Mockup":
            if sec in overrides:
                lw, lsrc = overrides[sec], "user override"
            elif r.get("lead_weeks"):
                lw, lsrc = int(r["lead_weeks"]), r.get("lead_source") or "spec"
            else:
                lw, lsrc = args.default_lead_weeks, "assumed - confirm with supplier"
        rule = r.get("due_rule") or ""
        submit_by, working = None, ""
        if rule.startswith(("NTP+", "AWARD+")):
            base = ntp if rule.startswith("NTP") else None
            days = int(re.sub(r"\D", "", rule))
            if base and not rule.endswith("WD"):
                submit_by = base + dt.timedelta(days=days)
                working = f"spec {r['ref']}: NTP {base} + {days}d = {submit_by}"
            else:
                flags.append(f"spec deadline {rule} - compute by hand (base date or working days unknown)")
        elif rule == "SC" or r["category"] == "Closeout":
            if sc:
                submit_by = sc
                working = f"Substantial Completion {sc}" + (f" (spec {r['ref']})" if rule == "SC" else
                                                            " (verify closeout timing in Division 01)")
        elif r["category"] == "Action" and nd:
            if r["type"] == "Mockup":
                submit_by = nd - dt.timedelta(days=R)
                working = f"need {nd} - {R}d review = {submit_by}"
            else:
                submit_by = nd - dt.timedelta(days=lw * 7 + R + B)
                working = f"need {nd} - {lw}wk x 7 = {lw * 7}d lead - {R}d review - {B}d buffer = {submit_by}"
        r.update({"_sec": sec, "_need": nd, "_nbasis": nbasis, "_lw": lw, "_lsrc": lsrc,
                  "_sb": submit_by, "_work": working, "_flags": flags})
        out.append(r)
    # informational rows without a deadline: reports after the work, the rest ride with
    # the section's first action submittal
    for r in out:
        post_work = r["type"] == "Test/Inspection Report" or str(r.get("part")) == "3"
        if r["_sb"] is None and r["category"] == "Informational" and post_work:
            lf = last.get(r["_sec"])
            if lf:
                r["_sb"] = lf[0]
                r["_work"] = f"after the work: last finish {lf[0]} ({lf[1]})"
        elif r["_sb"] is None and r["category"] == "Informational":
            acts_sb = [x["_sb"] for x in out if x["_sec"] == r["_sec"] and x["category"] == "Action" and x["_sb"]]
            if acts_sb:
                r["_sb"] = min(acts_sb)
                r["_work"] = f"with first action submittal of section ({r['_sb']})"
            elif r["_need"]:
                r["_sb"] = r["_need"] - dt.timedelta(days=R)
                r["_work"] = f"need {r['_need']} - {R}d review = {r['_sb']}"
        if r["_need"] is None and r["category"] != "Closeout" and not (r.get("due_rule") or ""):
            r["_flags"].append("no schedule activity for this section - add one or enter a need date")
        if r["_sb"]:
            d = (r["_sb"] - as_of).days
            if d < 0:
                r["_flags"].insert(0, f"OVERDUE by {-d}d")
            elif d <= 14:
                r["_flags"].insert(0, f"DUE IN {d}d")
    # numbering, merge with an existing register
    existing, keep = {}, []
    if args.existing:
        with open(args.existing, newline="", encoding="utf-8-sig") as fh:
            for e in csv.DictReader(fh):
                existing[(norm_section(e["Spec Section"]), e["Spec Ref"], e["Item"].lower())] = e
    seq = {}
    for e in existing.values():
        m = re.search(r"-(\d+)$", e["Submittal No"])
        if m:
            s = norm_section(e["Spec Section"])
            seq[s] = max(seq.get(s, 0), int(m.group(1)))
    out.sort(key=lambda r: (r["_sec"], [int(x) if x.isdigit() else x for x in re.split(r"[.]", r["ref"])]))
    rows, seen = [], set()
    for r in out:
        key = (r["_sec"], r["ref"], r["item"].lower())
        old = existing.get(key)
        seen.add(key)
        if old:
            no, status, bic = old["Submittal No"], old.get("Status", ""), old.get("Ball In Court", "")
        else:
            seq[r["_sec"]] = seq.get(r["_sec"], 0) + 1
            no, status, bic = f"{r['_sec']}-{seq[r['_sec']]:03d}", "Not submitted", "GC/Sub"
        div = int(r["_sec"][:2]) if r["_sec"][:2].isdigit() else 0
        reviewer = "Architect / MEP Engineer" if 21 <= div <= 28 else "Architect"
        rows.append({
            "Submittal No": no, "Spec Section": r["_sec"], "Section Title": r["section_title"],
            "Spec Ref": r["ref"], "Item": r["item"], "Type": r["type"], "Category": r["category"],
            "Description": r["description"], "Reviewer": reviewer,
            "Need Date": r["_need"] or "", "Need Basis": r["_nbasis"],
            "Lead Weeks": "" if r["_lw"] is None else r["_lw"], "Lead Source": r["_lsrc"],
            "Submit By": r["_sb"] or "", "Working": r["_work"], "Status": status, "Ball In Court": bic,
            "Flags": "; ".join(r["_flags"]), "Source": f"{r['source_file']}:{r['source_line']} ({r['origin']})",
        })
    for key, e in existing.items():
        if key not in seen:
            e = dict(e)
            e["Flags"] = ("NOT FOUND in latest spec parse - deleted by addendum? verify; " + e.get("Flags", "")).strip("; ")
            rows.append(e)
    cols = ["Submittal No", "Spec Section", "Section Title", "Spec Ref", "Item", "Type", "Category", "Description",
            "Reviewer", "Need Date", "Need Basis", "Lead Weeks", "Lead Source", "Submit By", "Working", "Status",
            "Ball In Court", "Flags", "Source"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: safe(r.get(k, "")) for k in cols})
    # summary
    print(f"DRAFT submittal register - verify against the spec before use. As of {as_of}.")
    print(f"NTP {ntp or 'not found'}; Substantial Completion {sc or 'not found'}; review {R}d, buffer {B}d.\n")
    print("| No | Ref | Item | Category | Submit By | Flags |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['Submittal No']} | {r['Spec Ref']} | {r['Item']} | {r['Category']} | {r['Submit By'] or '-'} | {r['Flags']} |")
    counts = {}
    for r in rows:
        counts[r["Category"]] = counts.get(r["Category"], 0) + 1
    print(f"\n{len(rows)} rows: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if dropped:
        print("Dropped as duplicates: " + "; ".join(f"{d['section']} {d['ref']} (dup of {d['dup_of']})" for d in dropped))
    print(f"Wrote {args.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("extract")
    e.add_argument("files", nargs="+")
    e.add_argument("--out", default="candidates.csv")
    f = sp.add_parser("finalize")
    f.add_argument("candidates")
    f.add_argument("--schedule", required=True)
    f.add_argument("--out", default="submittals.csv")
    f.add_argument("--as-of")
    f.add_argument("--review-days", type=int, default=14)
    f.add_argument("--buffer-days", type=int, default=7)
    f.add_argument("--default-lead-weeks", type=int, default=4)
    f.add_argument("--lead", action="append", help='section=weeks, e.g. "09 91 23=2"')
    f.add_argument("--ntp")
    f.add_argument("--sc")
    f.add_argument("--existing")
    a = ap.parse_args()
    (extract if a.cmd == "extract" else finalize)(a)


if __name__ == "__main__":
    main()
