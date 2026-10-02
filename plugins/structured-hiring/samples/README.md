# Sample data (synthetic)

Everything here is invented. Fernhill Robotics and Loop Lane Labs are
fictional companies; every person is a first name plus initial; every email
uses example.com and every phone number uses the 555-01xx fiction range.

`fernhill-robotics/` -- one req (REQ-1042, Senior Backend Engineer, Denver):

| File | What it is |
|---|---|
| kit.json | Interview kit: 6 competencies, anchored 1-4 rubric, 5 sessions |
| scorecards.json | 15 interviews for 6 candidates, 14 submitted scorecards, 1 missing |
| greenhouse-export-priya.json | Priya N.'s scorecards in a Greenhouse-style export shape (includes contact info and EEO fields that the tools must drop) |
| ashby-feedback-priya.csv | The same scorecards as an Ashby-style feedback CSV |
| pipeline.csv | Pipeline export, with a duplicate row, a blank row, a lower-case stage and a US-format date |
| intake-notes-backend.md | Intake notes for the job description (no pay range yet) |
| jd-draft-backend.md | A badly written JD draft for the fairness lint |
| pasted-scorecards-example.txt | Free-text scorecards as a user might paste them |

Planted problems (what the tools should find):

- Priya N.: Debugging & operations scorecard missing (Gabe T.), so Debugging &
  Operations has no evidence; System Design split 2 vs 2 (Ana Q. 3, Dev M. 4
  vs Ben O. 2, Farah S. 2); Chen H. rated Code Quality & Testing 4 with the
  evidence "Solid coder, would be great."; Dev M. wrote "Great culture fit --
  she brings the young energy this team needs."; Ben O. wrote "Seemed nervous
  at the start"; a phone number and an email appear in notes.
- Morgan L.: "Mentioned two young kids, so may not want the on-call load."
- Taylor W.: in Technical Screen since 2026-09-10 (21 days as of 2026-10-01).
- The JD draft has no pay range for a Denver (Colorado) role, and uses coded
  terms (rockstar, ninja, digital native, young, recent grads need not apply,
  native English speaker, top-tier university).

Use `--as-of 2026-10-01` with the scripts to reproduce the documented numbers.

`expected/` holds the outputs of every bundled script on this data with
`--as-of 2026-10-01`, so you can compare a run against a known result.
