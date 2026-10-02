#!/usr/bin/env python3
"""Fairness lint for hiring text: interviewer feedback, job descriptions,
interview questions and candidate outreach.

Usage:
  python3 fairness_lint.py <file|-> [--mode feedback|jd|questions|outreach] [--json]

It is a pattern matcher, not a judge. Each rule is a regular expression with
a category, a severity and a reason (see RULES below). A flag means "a human
should look at this", never "this person is biased". Rules apply to every
mode unless `modes` restricts them. Exit code is 0 even when flags are found.

Severity:
  high   -- protected-class proxy or an unlawful question (age, family status,
            national origin, disability, religion, pregnancy, salary history)
  medium -- non-job-related judgement (culture fit, pedigree, employment gaps,
            appearance, demeanor or emotion inferences)
  low    -- coded or exclusionary wording in postings (rockstar, ninja)
"""
import json
import re
import sys

ALL = ("feedback", "jd", "questions", "outreach")

# (category, severity, pattern, reason, suggestion, modes)
RULES = [
    # --- age ---
    ("age", "high", r"\byoung(er)?\b(?! (kids|children|child|family|daughter|son|baby|company|startup|product|market|industry|field)\b)|\byouthful\b|\bold(er)? (guy|man|woman|lady|person|candidate)\b|\b(he|she|they)('s| is| are) (in (his|her|their) )?\d{2}\b|\b(over|under) (40|45|50|55|60|65)\b|\bretire(ment|s|d)?\b|\bnear(ing)? retirement\b|\bclass of (19|20)\d\d\b",
     "Age-coded wording (ADEA protects 40+).", "Describe the job-related behaviour instead.", ALL),
    ("age", "high", r"\bdigital native\b|\brecent grad(uate)?s? (only|need not apply|preferred)\b|\brecent grads need not apply\b|\bover-?qualified\b|\bold[- ]school\b|\bset in (his|her|their) ways\b|\b(millennial|gen ?z|boomer)s?\b",
     "Age-coded wording.", "Name the skill or experience actually required.", ALL),
    ("age", "high", r"\bhow old\b|\bgraduation year\b|\bwhen did you graduate\b|\bwhat year were you born\b|\bdate of birth\b",
     "Asks for or relies on age.", "Remove; ask only whether the candidate meets a lawful minimum age if one applies.", ALL),
    ("age", "medium", r"\b\d{1,2}\s*-\s*\d{1,2}\+? years of experience\b|\bno more than \d+ years\b|\bmax(imum)?\.? \d+ years\b|\bup to \d+ years of experience\b",
     "A maximum years-of-experience cap screens out older applicants.", "Use a minimum or describe the capability.", ("jd",)),
    ("age", "low", r"\bhigh[- ]energy\b|\benergetic\b",
     "Energy wording often reads as age-coded in postings.", "Describe the pace or workload concretely.", ("jd", "outreach")),
    # --- family / pregnancy / marital status ---
    ("family-status", "high", r"\b(kids|children|child(?! (process|processes|thread|threads|node|nodes|element|elements|table|tables|class|component|components|span|record|records|entity|entities))(?<!parent/child)(?<!parent-child)|baby|babies|toddler|newborn|pregnan\w*|maternity|paternity|childcare|daycare|married|marriage|wife|husband|spouse|family plans|start(ing)? a family|planning (a|to have a) family|have (kids|children)|single mom|single dad|mom|dad(?! joke))\b",
     "Family, marital or pregnancy status is not job-related and is protected in many jurisdictions.", "Delete the remark; assess availability only through the job's stated schedule, asked of everyone.", ("feedback", "questions", "outreach")),
    # --- national origin / language / citizenship ---
    ("national-origin", "high", r"\baccent(ed)?\b|\bnative[- ](english|speaker|language|level english)\b|\bwhat is your (native|first|mother) (language|tongue)\b|\bmother tongue\b|\benglish (is not|isn't|is) (his|her|their) (first|second|native) language\b|\b(second|first) language\b|\bforeign(er)?\b(?! (key|keys|exchange|currency|function|table))|\bwhere (is|are) (he|she|they|you) (really |originally )?from\b|\bwhere were you born\b|\bgrew up in\b|\bimmigrant\b|\bethnic\w*\b",
     "National origin, ancestry or language-origin remark.", "Assess communication against the rubric (clarity, structure), not accent, language origin or birthplace. Postings may require 'fluent' or 'professional' English if the job needs it.", ALL),
    ("national-origin", "high", r"\b(are you|is (he|she|they)) a (us |u\.s\. )?citizen\b|\bcitizenship\b",
     "Citizenship questions are restricted; work authorization is the lawful question.", "Ask: 'Are you legally authorized to work in <country>? Will you now or in future require sponsorship?'", ALL),
    # --- disability / health / military ---
    ("disability-health", "high", r"\bdisab\w*\b|\bwheelchair\b|\bhealth (issue|problem|condition)s?\b|\bmedical (condition|history|leave)\b|\bon medication\b|\bmental(ly)? (ill|health)\b|\bdepress(ed|ion)\b(?! (rate|throughput|latency))|\banxiety disorder\b|\b(adhd|autis\w*|dyslexi\w*|bipolar|ptsd)\b|\bable-bodied\b|\bsick (days|leave)\b",
     "Disability or health remark (ADA).", "Delete; if the job has a physical requirement, state it as an essential function with 'with or without reasonable accommodation'.", ALL),
    ("disability-health", "medium", r"\blift \d+\s*(lbs?|pounds|kg)\b|\bmust be able to stand\b",
     "Physical requirement; lawful only if it is an essential function of this job.", "Keep only if essential, and add 'with or without reasonable accommodation'.", ("jd",)),
    ("military-status", "medium", r"\b(veteran|military service|national guard|reservist|discharge(d)? from)\b",
     "Military and veteran status is protected (USERRA and many states).", "Assess the job-related skills, not service status.", ("feedback", "questions")),
    # --- religion ---
    ("religion", "high", r"\b(church|mosque|synagogue|religio\w*|pray(s|ing|er)?|sabbath|ramadan|hijab|turban|yarmulke)\b",
     "Religion remark or question.", "Delete; scheduling needs are handled through accommodation, not interview questions.", ALL),
    ("religion", "medium", r"\b(christmas|temple)\b(?! (university|street|run))",
     "Possible religion reference; often harmless (holiday closures, place names).", "Check the context; remove if it concerns the person's beliefs.", ("feedback", "questions")),
    # --- gender / sex / orientation ---
    ("gender", "high", r"\b(maiden name|sexual orientation|gay|lesbian|transgender|girlfriend|boyfriend)\b",
     "Sex, gender identity or orientation remark.", "Delete.", ("feedback", "questions", "outreach")),
    ("gender", "low", r"\b(salesman|chairman|manpower|guys|he or she|he/she|strong man|man the)\b",
     "Gendered wording.", "Use neutral terms (salesperson, chair, staffing, team, they).", ("jd", "outreach")),
    ("gender", "low", r"\b(rock ?star|ninja|guru|wizard|jedi|superhero|crush(ing)? it|aggressive|dominant|fearless|work hard,? play hard)\b",
     "Masculine-coded or exclusionary posting language (Gaucher et al., 2011).", "Describe the actual work and standard.", ("jd", "outreach")),
    # --- culture fit and other non-job-related judgements ---
    ("culture-fit", "medium", r"\bcultur(e|al) fit\b|\bfit (right )?in with (the|our) team\b|\bfit right in\b|\b(would|could) (grab|have) a beer\b|\bbeer test\b|\bairport test\b|\bone of us\b|\bvibe(s)?\b|\bgut feel(ing)?\b",
     "'Culture fit' and gut-feel remarks are not job-related and are a common proxy for similarity bias.", "Replace with evidence against a named competency, or with 'values alignment' tied to a written value.", ALL),
    ("pedigree", "medium", r"\b(ivy league|top[- ]tier (school|university|college)|top school|elite (school|university)|pedigree|target school|stanford|harvard|mit grad|prestigious (school|university))\b",
     "School prestige is a weak predictor and a proxy for class and race.", "Name the skill; accept equivalent experience.", ALL),
    ("employment-gap", "medium", r"\b(employment|resume|career|work) gaps?\b|\bgaps? in (his|her|their|your)? ?(resume|cv|employment|work history)\b|\bno gaps\b|\btime off (work|from work)\b|\bunemployed\b|\bcurrently employed (only|candidates)\b|\bjob[- ]hopp\w*\b",
     "Gaps and tenure patterns often reflect caregiving, illness or layoffs.", "Ask everyone the same question about relevant recent experience, or drop it.", ALL),
    ("appearance", "medium", r"\b(attractive|good[- ]looking|pretty|handsome|overweight|heavy-?set|well[- ]groomed|hair(style)?|tattoo\w*|dress(ed)? (well|poorly|up)|professional appearance)\b",
     "Appearance remark.", "Delete unless a lawful, written dress requirement applies to the role.", ALL),
    ("demeanor-emotion", "medium", r"\b(seemed|seems|looked|appeared|sounded|came (across|off)( as)?|was) (very |a bit |a little |really |quite |so |too )?(nervous|anxious|stressed|insecure|timid|shy|arrogant|cocky|emotional|angry|upset|excited|bored|uninterested|unsure|uncertain|low[- ]energy|high[- ]energy|passionate|confident(?! (about|that|in the|the)))\b|\b(lacked|lacks|no|low|high) (confidence|passion|energy|enthusiasm)\b|\b(introvert|extrovert)(ed)?\b|\bpersonality\b",
     "Inference about emotion, demeanor or personality. These are unreliable signals, and AI systems may not infer emotions at work (EU AI Act Art. 5(1)(f)).", "Record what the candidate said or did against the rubric.", ("feedback",)),
    # --- unlawful or risky questions ---
    ("salary-history", "high", r"\b(salary|pay|compensation|wage) history\b|\bcurrent (salary|pay|compensation)\b|\bhow much (do|did) you (make|earn)\b|\bwhat (do|did) you (make|earn)\b|\bprevious (salary|pay)\b",
     "Salary-history questions are banned in many US states and cities (e.g. CA, CO, NY, IL, MA, NJ, WA, VA).", "Ask for salary expectations instead.", ("questions", "outreach", "feedback")),
    ("arrest-record", "high", r"\b(ever been arrested|arrest record|criminal record|convicted)\b",
     "Arrest and conviction questions are restricted by ban-the-box laws before a conditional offer.", "Remove from the interview; handle background checks after an offer per local law.", ("questions", "outreach")),
    ("comp-vague", "medium", r"\bcompetitive (salary|pay|compensation)\b|\bDOE\b|\bdepending on experience\b",
     "Vague pay wording; many jurisdictions require a posted range (run pay_transparency.py).", "State the good-faith range.", ("jd",)),
]

# Lines that are an equal-opportunity or accommodation statement are skipped
# in jd and outreach modes: they must name protected classes to protect them.
EEO_LINE = re.compile(r"equal (employment )?opportunity|without regard to|\bEEO\b|reasonable accommodation|affirmative action|regardless of (race|age|gender|sex)", re.I)

COMPILED = [(c, s, re.compile(p, re.I), why, fix, modes) for c, s, p, why, fix, modes in RULES]
ORDER = {"high": 0, "medium": 1, "low": 2}


def lint(text, mode="feedback"):
    """Return a list of flags: {line, category, severity, match, context, reason, suggestion}."""
    flags = []
    for ln, line in enumerate(text.splitlines(), 1):
        if mode in ("jd", "outreach") and EEO_LINE.search(line):
            continue
        seen = set()
        for cat, sev, rx, why, fix, modes in COMPILED:
            if mode not in modes:
                continue
            for m in rx.finditer(line):
                key = (cat, m.start())
                if key in seen:
                    continue
                seen.add(key)
                a, b = max(0, m.start() - 50), min(len(line), m.end() + 50)
                flags.append({"line": ln, "category": cat, "severity": sev,
                              "match": m.group(0), "context": line[a:b].strip(),
                              "reason": why, "suggestion": fix})
    flags.sort(key=lambda f: (ORDER[f["severity"]], f["line"]))
    return flags


def render(flags, mode):
    if not flags:
        return f"Fairness lint ({mode}): no flags. A clean lint is not a fairness guarantee; a human still reviews."
    out = [f"Fairness lint ({mode}): {len(flags)} flag(s). Flags mean 'a human should look', not 'this is biased'.", "",
           "| Sev | Line | Category | Phrase | Why | Suggested fix |", "|---|---|---|---|---|---|"]
    for f in flags:
        out.append(f"| {f['severity']} | {f['line']} | {f['category']} | \"{f['match']}\" | {f['reason']} | {f['suggestion']} |")
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    mode = "feedback"
    if "--mode" in args:
        mode = args[args.index("--mode") + 1]
        if mode not in ALL:
            sys.exit(f"--mode must be one of {', '.join(ALL)}")
    src = args[0]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    flags = lint(text, mode)
    print(json.dumps(flags, indent=2) if "--json" in args else render(flags, mode))


if __name__ == "__main__":
    main()
