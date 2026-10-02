# Pulling scorecards from a connected ATS (read only when an ATS MCP is connected)

General rules: read-only tools only; fetch one candidate for one req; do not
fetch resumes, EEO data, or other candidates; convert to `schema.md` and
discard the raw response from your working notes.

## Greenhouse (official MCP, open beta)

- URL: `https://mcp.us.greenhouse.io/mcp` (Claude Code / Cowork, bundled in
  this plugin's `.mcp.json`) or `https://mcp.greenhouse.io/mcp` (claude.ai
  connector). OAuth sign-in with your own Greenhouse account. Available on
  Core, Plus and Pro plans; a Site Admin enables it under Dev Center >
  MCP Access. Default scopes are read-only, including scorecards.
- Flow: find the job by name, find the candidate's application on that job,
  list that application's scorecards, and get the interview plan or
  scheduled interviews to detect missing scorecards. Tool names vary by
  release; pick the list/get tools whose names match those nouns.
- Map: each scorecard attribute -> `ratings[attribute]`
  (definitely_not/no/mixed/yes/strong_yes labels as-is); question answers
  that name an attribute -> `evidence[attribute]`; other answers -> `notes`;
  skip `overall_recommendation`.

## Ashby (official MCP, open beta, all plans)

- URL: `https://mcp.ashbyhq.com/mcp/v1`. An org admin opts in, then each user
  signs in with OAuth and keeps their own Ashby permissions.
- Read tools used: `search_records_by_name` (candidate), `get_candidate`,
  `get_interview_plan`, `get_submitted_feedback`, `get_interview_details`.
- Write tools (`change_application_stage`, `add_note_to_candidate`,
  `create_candidate`, `consider_candidate_for_job`) are never used during
  debrief prep.

## Lever

No official MCP server as of 2026-10. Ask for a feedback CSV export or a
paste. Community servers exist (for example stefanoamorelli/lever-mcp,
AGPL-3.0); this plugin does not bundle or endorse them.

## If the ATS call fails

Say which call failed and why (not connected, permission, beta scope off),
then fall back to "export the scorecards as CSV or paste them here".
