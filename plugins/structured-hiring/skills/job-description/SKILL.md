---
name: job-description
description: Use when the user needs a job posting written or fixed, or says "write a JD", "job description from these intake notes", "draft a job posting", "rewrite this job ad", "do we need a salary range", "is this posting compliant with pay transparency". Produces a JD with must-haves split from nice-to-haves, a pay-range check against US and Canadian pay-transparency posting laws (Colorado, California, New York, Washington, Illinois and others), and an inclusive-language lint.
---

# Job description

## 0. Guardrails

Read `../fairness-lint/guardrails.md`. Never invent a pay range. Never say a
posting is "compliant" or "legal"; say which requirements the checker found
met or missing and that counsel owns sign-off.

## 1. Gather

From the intake notes, an old JD, or the user. Needed: title, level, team,
location(s) and remote policy, employer headcount (for thresholds), what the
person will do in year one, must-haves, nice-to-haves, pay range, benefits,
application deadline. If notes contain remarks like "young and hungry",
"digital native", "rockstar" or "fit right in", do not carry them into the
JD; translate each into the job-related need behind it and tell the user.

## 2. Check pay-transparency rules

From this skill's directory run, once per location (add every remote
location or "Remote (US)" if remote is allowed):

`python3 pay_transparency.py --location "<city, ST>" [--location "Remote (US)"] [--employees N]`

(If this session cannot run Python, read `pay_laws.json` directly, match the
location to each law's `match` list, and say the check was done by hand.)
Use the script's list as the only source for which laws apply and what they
require. If a pay range is missing and any law applies:
- put a visible placeholder in the JD: `[PAY RANGE REQUIRED: $____ - $____ per year]`,
- tell the user which law(s) require it (by name from the script), and ask for
  the good-faith range. Do the same for benefits and application deadline
  when the script lists them.

If the script lists a law that requires disclosing AI use in screening
(Ontario), add to "How we hire": "We use AI tools to help draft materials
and organise interview notes; people make all hiring decisions." Keep it
true: never claim AI is not used.

## 3. Write the JD (literal template)

```
# <Title> -- <Company>
<Location, remote policy>

## About the role
2-3 sentences: the problem this person owns and why it matters.

## What you'll do
4-6 bullets of real work, starting with verbs.

## Must-haves
3-6 bullets. Each is required on day one and is assessed in the interview.
Prefer capabilities over years; never a maximum years cap; degree only if
truly required, then "or equivalent experience".

## Nice-to-haves
2-4 bullets, with: "If you meet most must-haves and none of these, apply."

## Pay and benefits
<range> + <bonus/equity if any>. Benefits: <list>.
Apply by: <date> (if required or known)

## How we hire
The interview stages and what each assesses (from the interview kit if any).
Accommodation line: "Need an accommodation to apply or interview? Email <contact>."
EEO statement appropriate to the employer.
```

## 4. Lint and verify

1. Save the draft to a file and run
   `python3 ../fairness-lint/fairness_lint.py <file> --mode jd`. (It skips
   the EEO and accommodation lines, which must name protected classes.)
   Re-run until every flag is fixed or explicitly explained to the user,
   for example a physical requirement that is an essential function.
2. Re-run `pay_transparency.py ... --jd <file>` and show its final output
   (pay range / benefits / deadline: yes or NO per applicable law).
3. Show the JD, then both check outputs, then a short list of what the user
   must still supply (placeholders left).

Close with: "AI-drafted. Pay-transparency data last reviewed <date from
script>; not legal advice."
