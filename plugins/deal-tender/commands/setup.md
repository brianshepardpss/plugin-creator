---
description: Set up DealTender - check for the Pipedrive connector or a CSV export, and save your stale threshold, stage probabilities, currency and email tone.
argument-hint: "[path/to/deals.csv]"
---

Set up DealTender for this user. Ask one question at a time; accept "skip".

1. Data source. Check whether Pipedrive connector tools (getDeals, getStages)
   are available.
   - Yes: call getStages once and write `stages.json` in the working folder
     (shape: the plugin's `samples/stages.json`; keep stage ids).
   - No: say the connector is optional. In Cowork or claude.ai: Settings >
     Connectors > add Pipedrive (or a custom connector with URL
     https://mcp.pipedrive.ai/mcp). In Claude Code this plugin already
     declares it; run /mcp and sign in to Pipedrive. Meanwhile CSV mode
     works: Deals list view > ... > Export filter results > CSV. If a path was
     given ($ARGUMENTS), run the csv-mode skill on it.
2. If there is no `stages.json`: ask for each pipeline's stages, win
   probability % and rotting days, and write `stages.json`.
3. Ask for: default stale threshold in days (default 14), commit threshold
   probability (default 80), base currency, and an fx rate to the base for
   each other currency they use (their own rates; DealTender never looks
   rates up), email tone in a few words, and the name to sign drafts with.
4. Write `dealtender-settings.json` in the working folder:
   `{"stale_days": 14, "commit_probability": 80, "base_currency": "USD",
   "fx_to_base": {"EUR": 1.1}, "tone": "...", "sender_name": "...",
   "field_map": {}}`. Do not add an `as_of` date.
5. Confirm what was saved and suggest: "/deal-tender:triage" next.

Never ask for or store a Pipedrive API token; the connector signs in with
OAuth.
