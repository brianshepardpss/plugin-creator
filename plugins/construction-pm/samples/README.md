# Sample data (all fictional)

Everything here was written for this plugin. The project ("Marlowe Creek
Clinic TI"), companies and people are invented. The spec sections are our
own text in CSI SectionFormat style, not copied from any real project
manual or master guide specification.

| File | Used by |
|---|---|
| spec/08_71_00_door_hardware.txt | submittal-register, rfi (hardware set HW-3, long-lead locks) |
| spec/09_91_23_interior_painting.txt | submittal-register (older "1.03 SUBMITTALS" style, mockup in QA) |
| spec/23_05_93_tab.txt | submittal-register (deadlines "within N days after Notice to Proceed") |
| schedule.csv | submittal-register need dates, lookahead (P6-style dates, blank row) |
| notes/walk-notes.txt | rfi (door 104 frame vs hardware conflict) |
| notes/daily-voice-transcript.txt | daily-report (messy voice memo, unforeseen footing) |
| notes/oac-meeting-transcript.txt | meeting-minutes (OAC meeting No. 7) |
| logs/rfis.csv | rfi (mixed date formats, one blank row) |
| logs/actions.csv | meeting-minutes (open items from meetings 5 and 6) |
| rates.csv | change-order-narrative (fictional burdened rates) |

`expected/` holds the outputs the bundled scripts produce on these files
(as-of dates 2026-10-02 and 2026-10-05). The evals assert values from them.
Regenerate with the commands in each skill if you change a sample.

The spec samples are plain text, which is what a PDF's text layer gives.
For your own project, drop in PDFs; the skill extracts their text first.

Differences from the design brief: the spec samples ship as text rather
than PDF (Cowork and claude.ai read PDFs directly; the skill saves their
text before parsing), and there are no sample jobsite photos (the
daily-report skill handles photos the user attaches).
