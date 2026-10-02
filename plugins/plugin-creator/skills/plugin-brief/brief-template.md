# <Plugin display name> -- design brief

Date: <YYYY-MM-DD>. Slug: `<kebab-slug>`. Surface: Claude Code | Cowork + claude.ai | both.

## 1. Target user and jobs to be done
Who, how many, how often. Jobs ranked by pain x frequency, each with evidence
(link, number or quote).

## 2. Competition
| Option | What it does | Price | What it lacks |
Official Anthropic plugins first, then vendor-native AI, community plugins and
MCP servers (with stars and last update), then the spreadsheet/ChatGPT status quo.

## 3. Technical facts
Data the user already has and its formats. APIs: auth model, who can get
credentials, plan tiers, rate limits, official MCP server (yes/no, URL, auth).
Decision: reuse / build / file-only, and why.

## 4. MVP
- Hero workflow (under 5 minutes, works on samples/ with no account):
- Skills, commands, agents (one line each):
- MCP / LSP / hooks decisions:
- Sample data to bundle (columns, sizes, deliberate dirty rows):
- Deliberate omissions:

## 5. Eval scenarios
Five prompts, each with observable pass criteria. Include at least one
guardrail case (the plugin must refuse or warn) and one exact-math case if the
plugin computes numbers.

## 6. Distribution
Communities where these users already are (specific), positioning one-liner,
name and trademark check.

## 7. Risks and guardrails
Legal, compliance, privacy, liability, ToS, technical. For each, the concrete
rule a skill will follow.

## 8. Day-30 signal
The metric and threshold that justify v2, and the one that means stop.
