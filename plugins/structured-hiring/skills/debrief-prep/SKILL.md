---
name: debrief-prep
description: Use when a candidate has finished interviews and the hiring team needs to get ready for the debrief, or when the user says "prep the debrief", "summarize the scorecards", "synthesize interview feedback", "where does the panel disagree", "which scorecards are missing for <candidate>", "debrief packet for <candidate>", or pastes several interviewers' feedback. Works from bundled samples, pasted scorecards, a Greenhouse or Ashby export, or a connected Greenhouse/Ashby MCP. Produces a one-page evidence packet; never a score, ranking or hire recommendation.
---

# Debrief prep

Output: one packet for ONE candidate: scorecard status, competency x
interviewer evidence matrix, disagreements, coverage gaps, thin-evidence
ratings, fairness flags, debrief questions and a decision-memo template.

## 0. Guardrails

Read `../fairness-lint/guardrails.md` before anything else. In particular:
no score, no ranking, no hire/no-hire, no emotion inference, one candidate
at a time, contact details removed, EEO data ignored.

## 1. Get the scorecards (pick the first that applies)

- **Sample** (`--sample`, "try it", "demo", or no data given and the user
  wants to see it work): use `../../samples/fernhill-robotics/scorecards.json`
  with `--kit ../../samples/fernhill-robotics/kit.json --as-of 2026-10-01`.
  Default candidate: Priya N. Tell the user it is synthetic data.
- **A file** (JSON or CSV export): pass its path. Greenhouse-style JSON
  (has `scorecards`) and Ashby-style CSV (`<Competency> - Score` /
  `<Competency> - Notes` columns) are read directly. Other CSVs: read
  `schema.md` and convert to the normalized JSON first.
- **Pasted text**: read `schema.md`, write the normalized JSON to a temp
  file (contact details removed; one interview object per interviewer; a
  listed interviewer with no feedback gets `"submitted_at": null`). Do not
  invent ratings: if the paste has no per-competency rating, leave
  `ratings` empty and put the text in `evidence` under the competency it
  discusses, or in `notes`.
- **Connected ATS (Greenhouse or Ashby MCP)**: read `ats-sources.md` and
  fetch only this candidate's application, scorecards/feedback and
  interview plan. Read-only calls only. Convert to the normalized JSON.
- **Lever or anything else**: ask for a CSV export or a paste. Do not
  scrape a UI.

If the user has no kit, the script derives competencies from the
scorecards; mention that a kit (`interview-kit` skill) gives better gap
detection.

## 2. Run the script

From this skill's directory:

```
python3 debrief.py <scorecards> --candidate "<name>" [--kit <kit.json>] [--as-of YYYY-MM-DD]
```

`--as-of` defaults to today; use the sample date for the sample. If the
file holds several candidates you must pass `--candidate`. Never loop over
every candidate in an export.

If this session cannot run Python (no shell or code tool), say so, then build
the same eight sections by hand from the input, show the working for every
count and date (for example "interviewed 2026-09-28, as of 2026-10-01 = 3
days"), and label the packet "built by hand -- check against debrief.py".
All guardrails still apply.

## 3. Present the packet

1. Show the script output verbatim (it is already the packet). Every count
   and date in it comes from the script; do not restate numbers in prose
   with different values.
2. Then add, under a heading "Facilitator notes", at most five bullets:
   - turn the seed questions into sharper ones using the quoted evidence
     (for example, for a System Design split, name the specific constraint
     each side tested);
   - which rubric anchors the disagreeing evidence matches, if a kit exists;
   - a suggested agenda: evidence by competency first, flagged remarks
     excluded, votes last.
3. Do not add: any summary judgement of the candidate, words like
   "strong candidate", "likely hire", "overall positive", a tally of votes,
   or any sentiment about the candidate. If interviewers' overall votes
   are in the data, leave them out (the packet explains why).
4. End with "AI-drafted, human decision required."

## 4. Follow-ups the user may ask for

- "Write it up" / "save it": write the packet to a markdown file named
  `debrief-<req or role>-<candidate initials>.md` in the user's folder.
- "Nudge the missing interviewer": draft a short internal reminder naming
  the session and date; do not send it.
- "Who should we hire?" / "rank them" / "is she a yes?": use the
  hiring-decision skill.
- "Compare Priya and Morgan": the same alphabetical, unrated, evidence-only
  table; run the script once per candidate and lay the evidence side by side.
- "Move her to offer" or any ATS change: guardrails section 6.
