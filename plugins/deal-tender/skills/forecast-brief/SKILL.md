---
name: forecast-brief
description: Use when the user asks for a sales forecast or pipeline summary, or says "what will we close this quarter", "forecast for this month", "weighted pipeline", "commit vs best case", "Monday pipeline update", "what moved this week", or "how is the quarter looking". Computes weighted, best-case and commit totals per currency from Pipedrive deals (connector, CSV export or sample), lists slipped deals and week-over-week movement, and writes a short brief ready to paste into Slack or email.
---

# Forecast brief

Every figure comes from the script. Never add, convert or round numbers in
prose. `<plugin>` is two directories up from this skill's directory.

## 1. Get the data

As in `<plugin>/reference/data-sources.md`. For "what moved", you need a
previous snapshot: `--prev sample` for the sample, or last week's export /
`deals_live.csv` the user kept (offer to save this week's for next time).

## 2. Run

```
python3 <plugin>/scripts/dealtender.py forecast <deals|sample> [--prev <file|sample>] [--period 2026Q4 | 2026-11 | 2026-10-01:2026-12-31]
```

Default period is the current quarter. "This month" -> `--period YYYY-MM`.

Check the output before writing:
- If it says "No combined total", report per currency only. Do not convert
  currencies yourself; offer `/deal-tender:setup` to record fx rates.
- If deals are "Not weighted (no probability)", say so and offer setup to
  record stage probabilities.
- The base-currency line uses the user's own fx rates from settings; say
  "at your rates" once. For the sample, say the rates are example values.

## 3. Write the brief

```
Pipeline forecast - <period label>, as of <date>

Weighted: <base total or per-currency list>   Best case: <...>   Commit: <...> (<n> deals)
Won so far this period: <...>

What moved since <prev date>:
- <won / lost / stage moves / value changes / close-date changes, one line each>

Slipped (close date passed, still open):
- <deal> - was <date>, <value>. Ask: new date or close out?

Watch: <1-3 bullets on what the numbers say, e.g. "commit rests on 4 USD deals"; no predictions beyond the data>
```

Keep it under 200 words. Definitions (commit = probability >= threshold,
weighted = value x probability) go in one footnote line.

## 4. Follow-ups

Offer, do not do: update the slipped deals' close dates (via
`<plugin>/reference/approval.md`), or run pipeline triage. Never state a
deal will close; say what the data shows.
