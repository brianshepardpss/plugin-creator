# Construction PM Toolkit

The free project-engineer sidekick for small GCs and specialty subs who run
jobs out of Excel, Word, email and PDFs (or on a Procore tier without the AI
add-ons). Spec sections to a cited submittal register in minutes; RFIs,
daily reports, OAC minutes, change order backup and 3-week look-aheads from
the notes you already have. Your files stay in your Claude session.

For: project managers, project engineers and superintendents at US general
contractors and subs, roughly $2M-$50M a year.

Works in: Claude Cowork, claude.ai and Claude Code. No account, API key or
other subscription needed.

## Install (60 seconds)

Claude Code:

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install construction-pm@plugin-creator
```

Cowork / claude.ai: add the marketplace `brianshepardpss/plugin-creator` in
plugin settings and install "Construction PM Toolkit".

## Try it on the sample job

```
/register sample
```

It reads three fictional spec sections (08 71 00 Door Hardware, 09 91 23
Interior Painting, 23 05 93 TAB) and a 40-activity schedule, and writes
`submittals.csv`: 23 rows, each citing its section and article, with
action/informational/closeout category, Submit By dates computed from the
schedule (working shown), LONG-LEAD flags on the electrified hardware and
or-equal flags. Then:

```
/rfi sample        # door 104 frame vs hardware set HW-3, logged as RFI-006
/daily sample      # voice memo -> daily report, unforeseen footing flagged
```

Or just talk to it: "write up the OAC minutes from this transcript", "price
this as a change order: 3 painters 2 days, $1,240 material, 10% OH 5% fee",
"make my three week look-ahead".

## What it does

| Skill | You say | You get |
|---|---|---|
| submittal-register | "build my submittal register" | submittals.csv, cited to spec article, dated from your schedule |
| rfi | "draft an RFI about..." | one-question RFI with spec/drawing cite, logged to rfis.csv with days open |
| daily-report | "write my daily from this voice memo" | structured daily, manpower totals, notice events flagged, gaps marked "not recorded" |
| meeting-minutes | "minutes from this OAC transcript" | carry-forward minutes (old items keep numbers), actions.csv updated |
| change-order-narrative | "price this added scope as a CO" | change order request in our own template, math by script with working |
| lookahead | "3-week look-ahead" | week-by-week table with submittal/RFI constraints and procurement watch |
| delay-notice | "the owner delayed us, what notice do I owe?" | points you to your contract, quotes its notice clauses if you paste them, drafts a neutral notice letter |
| request | "I wish this could..." | a feature request draft you can file yourself |

Commands: `/register`, `/rfi`, `/daily`. Agent: `register-checker` does a
second completeness pass on a draft register.

Inputs: spec PDFs with a text layer (scanned pages need OCR first), notes,
voice-memo transcripts, photos, and CSV exports from your scheduling tool
(Primavera P6, Microsoft Project or a spreadsheet). Outputs are CSV files
that open in Excel and Markdown drafts you paste into Word or email.

## What it will not do

- State contract deadlines, notice periods or entitlement as fact. It flags
  possible notice events and tells you to check your contract today.
- Reproduce AIA forms (G701, G702/G703, A201). It uses its own templates.
- Make engineering, code or OSHA compliance calls.
- Write to Procore, Autodesk Construction Cloud or any other system.

Everything it produces is a draft for professional review, not legal advice.

## Privacy

Your specs, contracts and notes stay in your Claude conversation and the
files it writes in your working folder. The plugin makes no network calls,
has no telemetry and connects to no service. The bundled scripts are
standard-library Python you can read.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file at https://github.com/brianshepardpss/construction-pm/issues. Nothing
is sent automatically.

## License

MIT. Sample data is fictional and written for this plugin.

Not affiliated with or endorsed by Procore Technologies, Inc.
Not affiliated with or endorsed by Autodesk, Inc.
Not affiliated with or endorsed by The American Institute of Architects (AIA).
Not affiliated with or endorsed by the Construction Specifications Institute (CSI); MasterFormat is a CSI trademark.
Not affiliated with or endorsed by Oracle (Primavera P6) or Microsoft (Project, Excel, Word).
