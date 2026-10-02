# Launch plan: Construction PM Toolkit

Nothing here is posted without owner approval, one post at a time.

## Positioning

The free project-engineer sidekick for builders without Procore Premier:
spec book to submittal register in minutes, nightly daily report in 3.
Your files stay yours.

Proof point for every post: the register on the sample job (23 cited rows,
Submit By dates with the working shown, electrified hardware flagged
long-lead because spec 1.7.B says 10-12 weeks). Show the CSV, not a pitch.

## Audience and where they are

| Channel | Why | Norms |
|---|---|---|
| r/ConstructionManagers | PEs/PMs; threads on reviewing submittals faster and sharing AI prompts | Mods have discussed banning software-selling posts. Give-first: share the method and prompts, free/open, no signup, answer every comment. Read the sidebar rules the day of posting. |
| r/Construction, r/Estimators | broader field + CO pricing crowd | Same; lead with the CO math backup for r/Estimators |
| ContractorTalk forum | small GCs and subs | Post in the software/business section, not general; disclose authorship |
| CSI chapter newsletters / LinkedIn groups | spec writers and submittal people care about register accuracy | Short article: "How we parse PART 1 submittal articles" |
| AGC / ABC / ASA local chapters (young constructors groups) | PEs in years 1-5 own the register | Offer a 15-minute lunch-and-learn, not an ad |
| LinkedIn construction-tech voices | reach | Native post with a 30-second screen recording |
| Procore Community forum | users below Premier tier | Only if rules allow third-party tools; position as "for your files", no integration claims |

## Post drafts

### r/ConstructionManagers (give-first, method post)

Title: How I get a first-pass submittal register out of spec sections in ~5 minutes (free, method + files inside)

> PEs: the register is the 1-3 day job at the start of every project, and
> the one where a missed long-lead item bites you in month four.
>
> What I do now: pull every paragraph inside the PART 1 "ACTION /
> INFORMATIONAL / CLOSEOUT SUBMITTALS" articles, then grep the rest of the
> section for "submit" and "mockup" (that is where the hardware
> consultant's inspection report and the paint mockup hide), then date each
> item backward from the schedule: need date - lead time - review - one
> resubmittal buffer. Every row keeps its article cite so the reviewer can
> check it.
>
> I packaged that as a free Claude plugin (MIT, no account, runs on your
> files, nothing uploaded anywhere else). It also drafts RFIs with the spec
> cite and keeps an RFI log, turns voice memos into dailies without making
> up headcount, and flags "possible notice event - check your contract"
> instead of pretending to know your contract.
>
> Sample output on a fake clinic TI is in the repo. Not selling anything.
> I would like to hear where it gets the register wrong on your specs.
> github.com/brianshepardpss/construction-pm

### ContractorTalk (software section)

Title: Free tool for small GCs: submittal log, RFIs and daily reports from your own PDFs and notes

> Disclosure: I built this. It is free and open source.
>
> If you run jobs out of Excel and email, this is a set of Claude skills
> that does the paperwork side: reads your spec sections and builds the
> submittal log with due dates off your schedule, writes RFIs and keeps the
> log, turns a voice memo at the truck into a daily report, writes OAC
> minutes with numbered action items, and prices change orders with the
> math shown line by line (your rates, your markups).
>
> What it will not do: tell you what your contract says about notice or
> what you are owed. It flags things like "hit an unknown footing" and
> tells you to check your contract the same day.
>
> Try it on the built-in sample job first: /register sample.

### LinkedIn (native post, with 30-second screen recording)

> Spec sections in. Submittal register out. Every row cites its article.
>
> 23 submittals from three sample sections, Submit By dates computed from
> the schedule (working shown in the file), electrified hardware flagged
> long-lead because the spec says 10-12 weeks.
>
> Free and open source for small GCs and subs who do not have enterprise
> construction AI. It runs on your files in Claude. Nothing to subscribe to.
>
> Also: RFIs with spec cites, dailies from voice memos, carry-forward OAC
> minutes, change-order backup with the math shown.
>
> #construction #projectengineer #submittals #contech

### CSI chapter newsletter (short article pitch)

Subject: Article offer - "Reading PART 1 like a parser: a free submittal register tool"

> 400 words on where submittal requirements hide outside the SUBMITTALS
> articles (QA mockups, field quality control reports, Part 2 "submit with"
> notes), why each register row should cite its article, and a free tool
> that does a first pass. Happy to adjust to your editorial guidelines; no
> product pitch beyond a link.

## Directory listing text

Construction PM Toolkit - Spec sections to a cited submittal register in
minutes, plus RFIs, daily reports, meeting minutes, change order backup and
3-week look-aheads, all from your own files. For PMs, project engineers and
supers at small GCs and subs. Flags possible notice events instead of
interpreting contracts. Free, MIT, no account, no data leaves your session.
Keywords: construction, submittals, RFI, daily report, CSI MasterFormat.

Listings: own marketplace (brianshepardpss/plugin-creator), Anthropic
plugin directory, community plugin directories.

## Day-30 signal

Measured on github.com/brianshepardpss/construction-pm, 30 days after the
first post.

- Continue if: >= 40 stars OR >= 150 unique cloners, AND >= 5 inbound
  /request issues or comments from self-identified PEs/PMs/supers, with at
  least 2 asking for the same next job (Procore sync or look-ahead).
  Plus one r/ConstructionManagers post not removed and net-positive
  (>= 25 upvotes).
- Kill or pivot if: < 10 stars and zero practitioner issues.
- Thresholds are fixed now and are not lowered after launch.
