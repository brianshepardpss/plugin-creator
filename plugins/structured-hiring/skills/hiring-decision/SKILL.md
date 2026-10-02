---
name: hiring-decision
description: Use when the user asks the assistant to decide or rank anything about candidates, or says "who should we hire", "which candidate is best", "rank these candidates", "score them out of 10", "give each a rating", "who is the strongest", "should we reject her", "pick our finalist", "send a recommendation to the CEO". Explains why the call stays with the hiring team and gives an alphabetical, unrated evidence comparison and a debrief plan instead.
---

# Hiring decision requests (rank, score, recommend)

The plugin never scores, ranks or recommends candidates. This skill is how
it says no helpfully.

## 1. Read the guardrails

Read `../fairness-lint/guardrails.md`, section 1.

## 2. Say what you will not do, in two sentences

"I won't rank, score or recommend candidates: that decision belongs to your
hiring team. Tools that score, rank or recommend candidates are regulated as
automated decision tools (NYC Local Law 144 bias audits and notice, the EU AI
Act's high-risk rules, and state laws such as Illinois and Colorado), and
uneven evidence makes any number look more certain than it is."

## 3. Give the useful alternative (literal template)

```
### Evidence side by side (alphabetical; no ratings, no ordering by strength)
| Candidate | <Competency 1> | <Competency 2> | ... | Gaps / missing scorecards |
|---|---|---|---|---|
| <A...> | "<quote or fact from the notes>" | ... | ... | ... |
```

Rules for the table:
- Rows in alphabetical order by first name. Never reorder by strength.
- Cells hold what interviewers observed (quotes or close paraphrases), or
  "not assessed". No numbers, votes, stars, colours, bold-for-best or
  "strongest/weakest" words.
- Remove any non-job-related remark and say it was removed (run
  `../fairness-lint/fairness_lint.py` on the notes if you can).

Then:
- "What would make this decidable": the missing scorecards, competencies not
  assessed for some candidates, and disagreements to resolve.
- "Debrief plan": one debrief per candidate against the role's competencies
  (offer /debrief-prep with their scorecards), decide each candidate against
  the bar, not against each other, votes last.
- For a CEO or founder update: offer a factual status note (who is at which
  stage, what evidence is pending, when the panel will decide). No ranking
  and no hire/no-hire recommendation.

## 4. Never

- No "my read", "leaning", "top pick", "looks strongest", hire/no-hire, or
  advance/reject suggestion, even hedged or "just between us".
- No scores, even if the user insists or says it is for internal use only.
  Repeat the reason once, briefly, and offer the table again.

End with: "AI-drafted, human decision required."
