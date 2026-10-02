---
name: csv-mode
description: Use when the user shares or uploads a Pipedrive deals export (CSV) or says "here's my Pipedrive export", "load my deals CSV", "check my export", "I don't have the connector", "clean up my CRM data", "find duplicate deals", or "which deals are missing close dates". Maps the export's headers (including hash-key custom fields), reports parse problems and pipeline hygiene issues, and records stage probabilities so triage and forecast work without a login.
---

# CSV mode: load and check a Pipedrive export

`<plugin>` is two directories up from this skill's directory.

## 1. Load

```
python3 <plugin>/scripts/dealtender.py load <file.csv | sample>
```

- MISSING REQUIRED COLUMNS: build `map.json` (`{"<their header>": "<key>"}`,
  keys listed in the error), rerun with `--map map.json`, and use it for
  every later command. Localized exports (non-English headers) need this.
- Custom field (hash key) UNLABELLED: Pipedrive exports some custom fields as
  40-character ids. Ask the user what the field is (Pipedrive: Settings >
  Data fields shows each field's API key); record it in `field_map` in
  `dealtender-settings.json`.
- Status not open/won/lost (localized exports): add `status_values` to
  `map.json`, for example `{"status_values": {"Offen": "open"}}`.
- Warnings about unreadable values or dates: list the line numbers; do not
  fix the user's data silently.

## 2. Report

```
Loaded <rows> deals (<status counts>) from <file>; <blank rows> blank rows skipped.
Columns used: <short list>. Ignored: <list or none>.

Hygiene
- Possible duplicates: <pairs> -> merge in Pipedrive (Deals > ... > Merge)
- Missing expected close date: <ids>
- Zero value: <ids>
- Stage probabilities: <known from stages.json | missing - forecast can't weight>

Next: "triage my pipeline", "forecast this quarter", or "prep me for <company>".
```

Numbers and ids exactly as the script prints them.

## 3. Missing stage settings

If no `stages.json` / `dealtender-settings.json` exists for the user's data,
offer `/deal-tender:setup`, or ask for each pipeline's stages with win
probability and rotting days (Pipedrive: Pipeline > Edit pipeline) and write
`stages.json` in the shape of `<plugin>/samples/stages.json`.

## Privacy

The export stays in the user's working folder. Do not quote contact emails
or phone numbers back unless needed for the task. Never upload the file
anywhere.
