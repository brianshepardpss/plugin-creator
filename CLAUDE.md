# plugin-creator lab

Read RUNBOOK.md first (WHERE WE ARE block), then CONVENTIONS.md.

- Owner: Press Start Studios. Commit identity (repo-local git config):
  `brian shepard <brian@press-start-studios.com>`. GitHub account:
  brianshepardpss.
- Nothing public without explicit owner approval each time: repo creation,
  pushes, releases, directory submissions, posts, eval reports published to
  claude.ai (always pass `--no-publish` to `claude plugin eval`).
- No telemetry. Feedback is the opt-in /request skill only (owner decision
  2026-10-02).
- Every plugin follows CONVENTIONS.md; `python3 lab/check.py` must pass
  before a commit that touches plugins/.
- Shared files are edited at the source and synced: shared/request/SKILL.md
  (lab/sync_request.py), plugin-brief/demand.py is copied into
  plugin-studio/skills/radar/ (keep them identical).
- Thresholds in lab/plugins.json are set before launch and never lowered
  afterwards.
