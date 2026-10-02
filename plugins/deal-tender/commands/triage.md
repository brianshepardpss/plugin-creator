---
description: Rank stale and past-close deals, draft follow-ups, and propose CRM updates for approval. Pass "sample" to try it with no account.
argument-hint: "[sample | path/to/deals.csv]"
---

Run the pipeline-triage skill on: $ARGUMENTS

- If the argument is `sample`, use the bundled sample data.
- If it is a file path, treat it as a Pipedrive deals CSV export.
- If it is empty, use the Pipedrive connector if one is available; otherwise
  ask whether to use a CSV export or the sample.

Do not write anything to Pipedrive until the user approves the change list.
