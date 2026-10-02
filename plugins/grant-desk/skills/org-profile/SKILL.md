---
name: org-profile
description: Use when the user wants to set up or update their nonprofit's boilerplate, case statement or grant library, or says "build our org profile", "save our boilerplate", "pull the facts out of our old proposals", "update our outcomes numbers", "what do you need to know about our organization". Produces grants/profile.md - mission, programs, staff and a Facts table where every number has a source and an as-of date - which every other Grant Desk skill drafts from.
---

# Org profile: the single source of truth for every draft

Output: `grants/profile.md` in the user's working folder, in exactly the
shape of `../../samples/sample-org/profile.md` (read it first; copy its
headings). Other skills cite facts as `profile#F03` or `profile#<heading>`.

## 1. Gather

Ask which applies, then follow it:
- **Ingest**: the user uploads past proposals, an annual report, a 990, or a
  case statement. Read them and extract candidates (step 2).
- **Interview**: ask in batches of at most 4 questions, in this order:
  1. Legal name, EIN, city/state, service area, year founded, annual budget.
  2. Mission (their words), programs (name, who, what, how often, where).
  3. Last full year's numbers: people served, sessions/units delivered,
     outcomes measured and how, volunteers, budget per program.
  4. Staff and board (names, roles; only what they want in proposals).
  5. Known gaps (no evaluation yet, no demographic data, etc.).

## 2. Facts table rules

Every number or verifiable claim becomes a row:

| ID | Fact | Value | Source | As of |
|----|------|-------|--------|-------|

- ID: F01, F02, ... never reused or renumbered (drafts cite them).
- Source: where the user's team can re-check it (database, report, file
  name and page). "Staff estimate" is allowed but must say so.
- As of: YYYY-MM.
- When documents disagree, do not pick one: list both and ask the user.
- Do not add outside statistics (census, research) unless the user gives
  the source; put them in the table with that source URL.
- Never round, inflate, or convert counts to percentages yourself; if the
  user wants a percentage, show the division (128 / 187 = 68.4%) and store
  both numbers.

## 3. Boilerplate

Keep paragraphs the user has approved under "Boilerplate paragraphs" with
"(approved YYYY-MM)". Tag any numbers inside them with fact IDs. Paragraphs
you draft are marked "(draft - needs approval)".

## 4. Check

Run `python3 ../../scripts/draft_check.py --lint-profile grants/profile.md`
and fix every FAIL (missing source or date). Report WARN rows (facts older
than 18 months) as a refresh list.

## 5. Reply

Show: number of facts, the refresh list, the "Known gaps" list, and the next
step ("Ready for grant-draft: give me an RFP"). Do not echo the whole file.
End with a human review checklist: a second person confirms each fact
against its source; board approves boilerplate paragraphs.

Privacy: the profile stays in the user's folder. Do not include donor names,
client names or other personal data about people served; aggregate counts
only.
