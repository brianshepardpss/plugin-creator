---
description: Build a debrief packet for one candidate from scorecards (sample data, a paste, an export, or your connected Greenhouse/Ashby). Never scores or ranks.
argument-hint: "[--sample | <candidate name> | <path to export>]"
---

Use the debrief-prep skill for this request: $ARGUMENTS

If the arguments are empty or contain `--sample`, run it on the bundled
sample data (Priya N., Fernhill Robotics, as of 2026-10-01) and say it is
synthetic. If the arguments name a candidate and a Greenhouse or Ashby MCP is
connected, fetch only that candidate's scorecards read-only. Otherwise ask
the user to paste the scorecards or give an export path.
