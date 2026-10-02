---
name: donor-thanks
description: Use when the user wants donor thank-you letters, year-end or GivingTuesday acknowledgments, gift receipts, or to segment donors from a CRM or gift CSV export, e.g. "write thank-you letters from this donor list", "segment our donors", "how many lapsed donors do we have", "year-end thank yous", "acknowledgment letters for gifts over $250". Not for thank-you or stewardship letters to foundations or grant funders. Segments donors locally with a script and mail-merges letters on the user's machine so names and emails are never sent to any outside tool.
---

# Donor thank-yous with personal data kept local

Script: `../../scripts/donors.py` relative to this skill's base directory.
Default templates: `templates/` beside this file. Demo data:
`../../samples/sample-donors.csv` (fictional donors).

## Privacy rules (follow exactly)

- Do not open, print, quote or summarize the donor CSV's rows yourself.
  The script reads it; you work from counts and from templates with
  placeholders.
- Never pass donor names, emails, addresses or amounts to web search, web
  fetch, an MCP connector, or the /request feedback skill.
- Outputs stay in `grants/donors/` in the user's folder. Remind the user
  that the folder contains personal data.
- If the user asks you to "personalize" letters for a specific donor, ask
  them to tell you only what they want included (for example, "met her at
  the gala").

## Steps

1. Ask for the as-of date if unclear (year-end letters: December 31 of the
   current year) and the major-gift threshold (default $1,000).
2. Run:
   `python3 ../../scripts/donors.py segment <donors.csv> --as-of <YYYY-MM-DD> --major <amount> --out grants/donors`
   Show its "Donors: N" line, data-quality line, segment table and any
   WARNING exactly as printed. If the user asks who is in a segment, point
   them to `grants/donors/segments.csv` (filter the segment column) rather
   than listing names.
3. Templates: copy `templates/*.md` to `grants/donors/templates/` and adapt
   the wording to the org (mission, program names, one real outcome from
   the org profile with its fact ID kept in a comment, signer). Each segment
   gets a distinct tone:
   - monthly: steady partnership, what a year of monthly gifts sustains
   - major: specific impact, invitation to a visit or call
   - first_time: welcome, what happens next, how to stay in touch
   - repeat: loyalty, "again this year"
   - lapsed: no thank-you for a gift this year; we miss you + one update
   - lapsed_long: no letter unless the user asks
   Allowed placeholders only: {first_name} {last_name} {year}
   {total_this_year} {gift_count} {last_gift_amount} {last_gift_date}
   {fund} {receipt_line}. Keep `{receipt_line}` in every thank-you: the
   script fills the IRS written-acknowledgment sentence for any single gift
   of $250 or more and leaves it empty otherwise.
   Never put an impact number in a template unless it is in the org
   profile; "your gift provided 12 books" style equivalences need a cost
   figure from the profile, shown with its fact ID.
4. Run:
   `python3 ../../scripts/donors.py merge grants/donors/segments.csv --templates grants/donors/templates --out grants/donors/letters`
5. Reply with: the segment table, the number of letters per segment, the
   count needing the IRS acknowledgment, any lapsed major donors to call,
   and the file paths. Show one template (with placeholders), not merged
   letters. End with a human review checklist: spot-check three letters;
   confirm no goods or services were given (else state their value);
   check names and salutations; remove anyone who asked not to be mailed.

Note for the user: the acknowledgment sentence assumes no goods or services
were given in return; for gala tickets or premiums, the letter must state
their fair market value instead (IRS Publication 1771).
