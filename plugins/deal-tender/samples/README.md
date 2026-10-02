# Sample data (all fictional)

Synthetic Pipedrive-style exports so every DealTender workflow runs with no
account. Every company, person, email (example.com) and phone (555) is made up.
"Today" for this data set is **2026-10-05** (a Monday); the scripts use that
date automatically when they read files from this folder.

| File | What it is |
|---|---|
| deals_export.csv | 40 deals, 2 pipelines, USD/EUR/GBP, one blank row, one "67,000.00" value, one duplicate deal (132), one custom field exported as a 40-char hash header |
| deals_export_prev.csv | the same pipeline one week earlier (2026-09-28), for "what moved" |
| stages.json | pipelines, stage probabilities and rotting days (what getStages returns) |
| settings.json | demo settings: stale threshold, base currency, EXAMPLE fx rates, tone |
| persons.csv, orgs.csv | contacts and organizations |
| activities.csv | done and planned activities with notes |
| calls/*.txt | 3 call notes (Acme has two open deals; Pinewood is not in the CRM) |
| emails/*.txt | 2 email threads (Initech pushes the close date; Northwind redlines) |

Expected script outputs are in `expected/`.
