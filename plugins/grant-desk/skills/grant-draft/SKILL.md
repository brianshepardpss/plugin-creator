---
name: grant-draft
description: Use when the user wants to write, draft or answer a grant proposal, LOI or application from an RFP or funder guidelines, or says "draft this grant", "answer these RFP questions", "write the program design section", "help me apply to this foundation", "grant draft", or "try Grant Desk on the sample". Produces a funder fit memo from public 990-PF data, a section-by-section draft where every claim is tagged to a source or [NEEDS DATA], a word-limit check, and the deadlines in a tracker CSV.
---

# Grant draft: RFP + org profile -> fit memo, tagged draft, checks, deadlines

Paths: scripts are in `../../scripts/` and demo files in `../../samples/`,
relative to this skill's base directory. Write all outputs under `grants/`
in the user's working folder (create it).

Hard rules for this whole skill:
- Never invent a statistic, citation, quote, outcome, partner or name. A
  number may appear only if it is in the org profile, a file the user gave
  you, or a script output with its URL. Otherwise write
  `[NEEDS DATA: what is missing]`.
- Every sentence with a number or a factual claim about the org carries a
  tag: `[source: profile#F05]`, `[source: profile#reading-buddies]`,
  `[source: https://...]`, `[source: <file name>]`, or `[NEEDS DATA: ...]`.

## 0. Inputs

First, before asking for anything else: if the request names NIH (R01,
R21, K, Specific Aims, etc.) or the Spencer Foundation, read
`ai-policies.md` and state `Mode: ASSIST` with the quoted rule right away;
the steps below then run in ASSIST mode.

- If the user says "sample", "demo" or "try it": RFP = `../../samples/sample-rfp.md`,
  profile = `../../samples/sample-org/profile.md`, budget =
  `../../samples/sample-budget.csv`, and add `--mode offline` to every
  funder script call so the demo is reproducible. Say once that the sample
  funder is fictional and the fit memo uses a real stand-in foundation, as
  the RFP's demo note explains.
- Otherwise ask for the RFP (file, link or paste) and the org profile. If
  there is no profile, run the org-profile skill first.

## 1. AI-use policy gate (always first, before any drafting)

1. Search the RFP for: AI, artificial intelligence, generative, ChatGPT,
   language model, machine-generated, original work, disclosure.
2. If found, quote the sentence and pick the mode using `ai-policies.md`.
3. If the funder is listed in `ai-policies.md` (NIH, Spencer), use that mode
   even if the user asks for more.
4. If the RFP is silent and the funder is not listed, ask: "Does <funder>
   have a policy on applicants using AI? Paste it, or say no / don't know."
   Wait for the answer. "Don't know" -> recommend asking the program officer
   and offer ASSIST mode now; use DRAFT only if the user confirms.
5. State the mode in one line: `Mode: DRAFT (RFP permits AI with disclosure)`
   or `Mode: ASSIST (NIH NOT-OD-25-132)`.

In ASSIST mode skip step 4's prose: give the question map and a bullet
outline per question (which facts to use, in what order), then offer to
critique and line-edit text the user writes. Steps 2, 3, 5 and 6 still run.

## 2. Read and map

1. Lint the profile:
   `python3 ../../scripts/draft_check.py --lint-profile <profile>`.
   Mention stale facts it warns about.
2. From the RFP, list each question with its exact word or character limit,
   award range or cap, geography and eligibility, required attachments and
   every date.
3. Build the question map table:

| Q | What they ask | Limit | Profile facts that answer it | Gaps |
|---|---|---|---|---|

Flag eligibility problems (geography, budget size, 501(c)(3) status) before
going further.

## 3. Fit memo

1. Find the funder's EIN (in the RFP, or `propublica.py search "<name>" --state XX`,
   then confirm the match with the user if more than one is plausible).
2. Run:
   `python3 ../../scripts/propublica.py org <EIN>` and
   `python3 ../../scripts/grantees.py <EIN> --state <org state> --city <org city> --keyword <3-5 mission words> --cap <RFP cap>`
3. Write `grants/fit-memo-<funder-slug>.md` from `fit-memo-template.md`,
   copying figures from the script output only. Keep the tax year and the
   source URLs. If a script fails and there is no cache, say so and ask the
   user for the funder's 990-PF PDF; do not estimate.

## 4. Draft (DRAFT mode only)

Write `grants/draft-<funder-slug>.md`:

```
# <Org> - <Funder> <program> draft (<date>)
Mode: DRAFT. Remove all [source: ...] tags before submitting.

## Q1. <title> [limit: <N> words]
<answer>
```

- Answer what is asked, in the funder's order and vocabulary; first
  sentence answers the question directly.
- Use only profile facts and the user's files. Reuse approved boilerplate
  paragraphs where they fit.
- Use the space the facts support, up to the limit; never over, and never
  pad with generic claims to fill it.
- Where the RFP asks for something the profile lacks (demographics,
  third-party evaluation, letters of support), write one honest sentence and
  a `[NEEDS DATA: ...]` tag. Do not fill the gap with general statistics.
- External statistics (county, state, research) are allowed only from a
  source the user supplied or you fetched in this session, tagged with its
  URL. Stale facts (flagged by the lint) get "as of <date>" in the sentence.

## 5. Check and fix (loop)

Run `python3 ../../scripts/draft_check.py grants/draft-<slug>.md --profile <profile> --rfp <rfp>`.
Fix every FAIL (cut words, add or correct tags, remove unsupported numbers)
and run it again until the result is PASS. If a budget is involved also run
`python3 ../../scripts/budget_check.py <budget.csv> --cap <cap> --narrative grants/draft-<slug>.md`
and fix every UNMATCHED figure. For a budget question, follow the
logic-model-budget skill's budget steps (reconcile the CSV first). Show the
final check table and its "Claims to verify by hand" list to the user. A
URL tag is allowed only for a page you fetched in this session.

## 6. Deadlines

Write every RFP date to a JSON list and run
`python3 ../../scripts/tracker.py add-json --tracker grants/tracker.csv <file>`
(type loi, application, report or other; include the time and time zone in
`time`; `source` = RFP file name and section). This also writes
`grants/deadlines.ics`.

## 7. Reply

```
Mode: <DRAFT|ASSIST> - <reason, quoting the policy>
Fit: <2-3 lines from the fit memo: tax year, grants paid, count near the
     user, suggested ask with range>. Full memo: grants/fit-memo-<slug>.md
Draft: grants/draft-<slug>.md - <check table from draft_check.py>
NEEDS DATA (<n>): <list>
Deadlines added: <n> -> grants/tracker.csv, grants/deadlines.ics (next: <item, date>)

Human review checklist
- [ ] Every [NEEDS DATA] filled or the sentence removed
- [ ] Each number re-checked against its source; tags removed
- [ ] Voice rewritten to sound like us; program staff read Q2/Q3
- [ ] Attachments gathered: <list from RFP>
- [ ] AI disclosure completed if the funder asks (sentence in ai-policies.md)
```

Do not paste the whole draft into chat unless asked; point to the file.
