# Listing Desk

Listing appointment prep and listing launch for US residential real estate
agents, inside Claude: a CMA from the MLS CSV export you already have,
MLS remarks, social posts and a just-listed email, with a Fair Housing check
on every word. Plus contract deadlines with a calendar file, open-house
follow-up drafts and a 12-month sphere plan. No new subscription, no API
keys, no scraping.

For solo agents and small teams (5-40 deals a year) who already have an MLS
login and want the paperwork side of a listing done in minutes, not hours.

Works in: Claude Cowork, claude.ai and Claude Code.

## Install (60 seconds)

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install listing-desk@plugin-creator
```

In Cowork or claude.ai, add the plugin from the same marketplace in
Settings > Plugins.

## Try it in 60 seconds, no account

```
/listing-kit sample
```

(In Claude Code the full name is `/listing-desk:listing-kit sample`. In
Cowork you can also just say "run the listing kit on the sample".)

On a fictional 40-row MLS export and subject house you get, in a
`listing-kit/` folder:

- **CMA -- not an appraisal**: column mapping to RESO field names, the dirty
  rows it dropped (by MLS number), 6 closed comps, an adjustment table with
  every dollar shown, and a 3-tier range (sample: Low $386,000 / Market
  $389,000 / High $391,000, from a $388,775 median adjusted price).
- **MLS public remarks** under the 1,000-character cap, **3 social posts**
  and a **just-listed email** -- built only from the property facts.
- **Fair Housing report** on all of that copy. Anything flagged is rewritten
  before you see it, and the seller's own wording that could not be used
  ("great for families", "safe, quiet neighborhood", "offer 3% to the buyer's
  agent") is listed with the reason.

Then try:

- "Is this OK? Charming 3/2 perfect for young families, quiet Christian
  neighborhood, walking distance to St. Mary's, safe area, no section 8."
- "Build the deadline calendar for this contract" with
  `samples/purchase_contract.txt` (the PDF and a scanned copy are in
  [sample-pdfs](https://github.com/brianshepardpss/plugin-creator/tree/main/lab/sample-pdfs))
- "Follow up with my open house sign-ins" with `samples/open_house_signins.csv`
- "Make me a 12-month plan to stay in touch with my sphere" with
  `samples/sphere_contacts.csv`

## Use it on your own listing

1. In your MLS, search closed, active and pending sales near the subject
   (same subdivision or ZIP, last 6-12 months) and export to CSV with the
   usual fields (status, prices, dates, address, subdivision, beds, baths,
   sqft, lot, year built, garage, pool, concessions). Any MLS system works;
   headers are matched to RESO names and you can map any it misses.
2. Drop the CSV into the chat with the subject's facts and seller notes,
   and say "listing kit".
3. Tell Claude your adjustment rates (per sqft, bedroom, bath, garage,
   pool, year, lot). It copies the default `adjustments.json` into your
   output folder, edits the copy and re-runs, so the adjustments match what
   you would defend.

## What it does

| Skill | Say | You get |
|---|---|---|
| listing-kit | "/listing-kit", "prep my listing appointment" | The whole package above |
| cma | "run a CMA from this export" | Comps, adjustment table, 3-tier range (script math) |
| listing-copy | "write the MLS remarks", "just listed post" | Remarks within the cap, posts, email, flyer text |
| fair-housing-check | "is this Fair Housing compliant?" | FLAG / REVIEW per phrase, class, reason, rewrite |
| contract-timeline | "what are the deadlines on this contract" | Key terms, deadlines with business-day/holiday working, .ics |
| follow-up | "follow up with my sign-ins" | Segments, 3 dated touches each, email/text drafts |
| nurture-plan | "12-month plan for my sphere" | Tiered touch calendar CSV, anniversaries, templates |
| request | "I wish this could..." | A feature request you can file yourself |

Every number (prices, adjustments, percentiles, deadlines, character
counts, touch dates) comes from a bundled standard-library Python script,
and the formula is in that script's header.

## Guardrails built in

- **Fair Housing**: the phrase checker runs on every generated piece of
  copy, not as an optional step, and Claude does a context review on top.
  Requests to pick neighborhoods or schools by a client's race, religion,
  national origin, family status, disability or age, or by "safety", are
  declined with a criteria-based search offered instead.
- **MLS rules**: no buyer-agent compensation, contact info or showing
  instructions in public remarks.
- **CMA, not appraisal**: every CMA is labelled "CMA -- not an appraisal".
- **Contracts**: every deadline is marked VERIFY against the executed
  contract; no legal advice, no drafting of notices or disclosure forms.
- **Outreach**: drafts only, nothing is sent. Texts only to people who
  consented, with STOP language; emails carry an unsubscribe line. Buyer
  drafts remind you to sign a written buyer agreement before touring.

The phrase list catches known problem wording; it is not legal advice and
cannot catch everything. Your broker has the final say.

## Privacy

Nothing leaves your machine except your normal Claude conversation. There
is no telemetry, no API key and no third-party service. Your MLS export is
read for the task at hand; the only copies are the CMA files written to your
own output folder (cma.md, cma_adjustments.csv, cma.json). Nothing is
aggregated or used to build a dataset. Do not republish comp data, which
your MLS licenses to you.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file on GitHub. Nothing is sent automatically.

## License

MIT. Sample data is fictional.

Not affiliated with or endorsed by any MLS, RESO, or the makers of Matrix,
Flexmls or Paragon; nor by Google, Microsoft, Apple or Meta (Instagram,
Facebook). Product names only describe file formats and destinations the
plugin works with.
