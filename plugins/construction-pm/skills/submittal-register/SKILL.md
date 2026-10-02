---
name: submittal-register
description: Use when the user wants a submittal register, submittal log or submittal schedule built from spec sections or a project manual, or says "build my submittal register", "make a submittal log from the specs", "pull the submittals out of these spec sections", "what submittals does Division 08 need", "which submittals are long lead", or "update the register for the addendum". Takes spec section PDFs or text (CSI MasterFormat numbering) plus an optional schedule CSV; produces a cited, numbered, dated submittals.csv that opens in Excel.
---

# Submittal register from spec sections

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

Output is a DRAFT for the project engineer to verify. Every row cites the
section and article it came from. Never add an item the spec text does not
contain; never drop one silently.

Scripts live in `scripts/` beside this file. Sample data lives in
`<skill dir>/../../samples/` (relative to this skill's directory).

## 1. Collect inputs

- Spec sections: PDF or text files, one section per file or a whole project
  manual. If the user says "sample" or "try it", use
  `<skill dir>/../../samples/spec/*.txt` and `<skill dir>/../../samples/schedule.csv`.
- Schedule CSV export (P6, MS Project, Excel) with a Spec Section column,
  used for need dates. Optional; without it rows get no Submit By date.
- An existing register CSV, if this is an update (addendum, bulletin).
- Ask for nothing else up front. Defaults: 14-day review, 7-day buffer for
  one resubmittal, 4-week lead time when the spec states none.

## 2. Get text

- `.txt` files: use as is.
- PDFs: the script tries `pdftotext`. If it reports it is missing, read the
  PDF yourself and write its text to `<name>.txt` line by line, keeping the
  article numbers ("1.3", "A.", "1.") at the start of lines. Do not
  summarize or reflow.
- A whole project manual: split it into one `.txt` per section at each
  `SECTION NN NN NN` heading before running the script.
- If a page has no text layer (scanned), say so, list the pages, and ask the
  user to OCR them. Do not guess their content.

## 3. Extract candidates

```
python3 <skill dir>/scripts/submittal_register.py extract <spec files> --out candidates.csv
```

Show the PARSED/SKIPPED report lines to the user. They are the list of
sections parsed vs skipped that the register must state.

## 4. Review candidates (your judgment, not the script's)

Read `candidates.csv` next to the spec text and fix only what the text
supports:
- `type` or `category` clearly wrong for the paragraph: correct it.
- Rows with origin "outside submittal article - verify": keep if the text
  really requires something to be submitted or built for approval; delete if
  it is only a mention. Say which you kept and why.
- A paragraph that lists several separate submittals (for example "Samples:
  1. hinges 2. levers") may be split into one row per item, same ref.
- Do not change dates, lead weeks or numbering here.
If the user or a supplier gave real lead times, pass them in step 5 with
`--lead "SECTION=WEEKS"` rather than editing the file.

## 5. Finalize

```
python3 <skill dir>/scripts/submittal_register.py finalize candidates.csv \
  --schedule <schedule.csv> --out submittals.csv --as-of <today YYYY-MM-DD> \
  [--lead "08 71 00=14"] [--existing <old register.csv>]
```

The script numbers rows `NN NN NN-001`, computes Need Date, Submit By and
the Working column, flags OVERDUE / DUE IN Nd / LONG-LEAD / or-equal, and
drops rows marked as duplicates (it prints which). With `--existing` it
keeps existing numbers and statuses and flags rows no longer in the spec.
Never compute or adjust a date yourself; rerun the script with different
flags instead.

## 6. Report

Reply in this shape:

```
DRAFT submittal register - verify against the spec before use.
File: submittals.csv (<N> rows: <a> action, <i> informational, <c> closeout)
Sections parsed: <list with titles>   Skipped: <list with reason, or none>

Due now (next 14 days or overdue):
| No | Item | Submit by | Why |  (from the script table)

Long-lead: <items, lead weeks and source: spec article or "assumed">
Or-equal / substitution allowed: <sections and refs>
Kept from outside submittal articles: <refs>   Dropped as duplicates: <refs>
Assumptions: review <R> days, buffer <B> days, default lead <L> weeks where
the spec is silent. Need dates come from <schedule file>.
```

Then offer: "Want me to draft the transmittal for the due-now items, or
build a 3-week look-ahead against this register?"

## Guardrails

- Rows must trace to spec text. If the user asks you to add an item that
  is not in the spec, add it with Source "user added" so it is visibly not
  from the spec.
- Lead times not stated in the spec are assumptions; keep the "assumed -
  confirm with supplier" label in the output.
- Submit By dates are planning targets computed from the schedule, not
  contract deadlines. When the spec states its own deadline (for example
  "within 30 days after Notice to Proceed") the row uses it and cites it.
- Division 01 (01 33 00 Submittal Procedures) usually sets review periods
  and format. If the user provides it, use its review period with
  `--review-days`; otherwise say the 14-day default is an assumption.
- Read `reference.md` only if you need the MasterFormat division names or
  the type/category definitions.
