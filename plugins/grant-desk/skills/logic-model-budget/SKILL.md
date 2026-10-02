---
name: logic-model-budget
description: Use when the user needs a logic model, theory of change table, outcomes and indicators, evaluation plan, budget justification or budget narrative for a grant, or says "build the logic model", "write the budget narrative", "does my budget add up", "check the budget against the narrative", "outputs vs outcomes". Reads a program budget CSV and the org profile; produces a logic model table and a budget narrative whose every dollar figure reconciles to the CSV (checked by a script).
---

# Logic model and budget narrative that agree with the numbers

Scripts: `../../scripts/` relative to this skill's base directory. Demo
inputs: `../../samples/sample-budget.csv`, `../../samples/sample-org/profile.md`,
`../../samples/sample-rfp.md` (cap $25,000).

## 0. AI-use policy

If this is for a specific funder, apply the AI-use policy gate from
`../grant-draft/SKILL.md` step 1 (and `../grant-draft/ai-policies.md`)
first. In ASSIST mode (e.g. NIH under NOT-OD-25-132), run the budget check
and give the logic model as an outline of points, but do not write the
budget justification prose; offer to edit the user's own text instead.

## 1. Reconcile the budget first

Run `python3 ../../scripts/budget_check.py <budget.csv> --cap <cap>`.
- Show its category table and the request / indirect / other-funding lines.
- If it reports FAIL rows (stated totals that do not add up, request over a
  line or over the cap), stop and show them; ask the user which number is
  right. Never "fix" a budget by changing numbers yourself.

## 2. Logic model

Write `grants/logic-model-<program>.md` with this table:

| Inputs | Activities | Outputs (counts) | Short-term outcomes | Long-term outcomes | Indicator and data source |
|---|---|---|---|---|---|

Rules:
- Inputs come from budget lines (staff, materials, volunteers) and profile
  facts.
- Outputs are counts of what the program does (students served, sessions).
  Targets must come from the profile's last-year actuals or a target the
  user states; label which. Never invent a target.
- Outcomes are changes in people (skills, behavior, condition), each with
  one measurable indicator, the instrument, and when it is collected.
- Every outcome must trace to at least one activity; every activity to at
  least one budget line. List any orphan.
- Tag numbers `[source: profile#Fxx]`, `[source: <budget file>]` or
  `[NEEDS DATA: ...]`.

## 3. Budget narrative

Write `grants/budget-narrative-<program>.md`: one short paragraph per
category in the CSV order, then the request summary. Use only figures from
the step-1 output: line totals, unit costs, category totals, shares, the
request total and share, indirect rate, other funding needed. Explain the
basis of each line (qty x unit cost) and what the funder's share buys.

Then run
`python3 ../../scripts/budget_check.py <budget.csv> --cap <cap> --narrative grants/budget-narrative-<program>.md`
and fix every UNMATCHED figure until the result is PASS.

## 4. Sustainability

If the RFP asks how the program continues, state the "other funding needed"
figure from the script and list only funding sources the user names; if
none are named, write `[NEEDS DATA: other committed or pending sources]`.

## 5. Reply

Show: the category table, the request line, the logic model table, the
narrative check result (PASS), orphans or NEEDS DATA items, and file paths.
End with a human review checklist: targets confirmed by program staff;
budget figures match the funder's template; NEEDS DATA items resolved.
