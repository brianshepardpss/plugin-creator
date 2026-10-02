# Research brief: `pipedrive` plugin (working name "DealTender for Pipedrive")
Date: 2026-10-02. [U] = unverified.

## 1. Target user and jobs-to-be-done
User: SMB founder or 1-10 rep sales team on Pipedrive (Lite/Growth, $14-$39/seat), deal-pipeline selling (agencies, B2B services, SaaS, trades). Lives in email + calls; hates CRM data entry. Pipedrive: 105k+ companies, 180+ countries.

Ranked pain x frequency:
1. Log call/meeting/email into the right deal (daily, high pain). Evidence: KWP small-business `crm-autopilot` premise "owners don't want a better CRM, they want to stop opening one"; reviews cite data quality "only as good as busy humans entering it" (breakcold, cotera). 35% of official-MCP interactions are writes (Pipedrive, Aug 2026).
2. Stale/rotting deal triage + follow-up drafts (daily/weekly, high). Pipedrive has native "rotting" flags but no drafting/action; review complaints about weak follow-up tooling (nethunt, getstealery).
3. Monday pipeline/forecast summary (weekly, med-high). Native AI Sales Assistant gives suggestions only, OpenAI-backed, no autonomous action; forecast view is per-pipeline.
4. Meeting prep from deal + person + org + history (several/week, med).
5. Hygiene: missing next activity, past close dates, dupes (weekly, med).

Demand proof: 6% of Pipedrive paying customers connected the official MCP in its first month; 93% of MCP usage is on Anthropic surfaces (Pipedrive newsroom 2026-08-18).

## 2. Competition and gaps
- Official Pipedrive MCP (remote, OAuth, all plans): https://mcp.pipedrive.ai/mcp. Launched 2026-06-30 (BETA in KB), in Claude connector directory since 2026-08-18. Read/search deals, persons, orgs, leads, activities; create/update deals, persons, activities, notes; lead conversion. No delete, no email, no scheduling/triggers. Tool list not published in detail [U]. This is plumbing, not workflow.
- Anthropic knowledge-work-plugins (26k stars, github.com/anthropics/knowledge-work-plugins): `sales` (38 skills, ~~CRM placeholder; bundled MCPs HubSpot, Salesforce, Close, monday; Pipedrive only listed as "other option" in CONNECTORS.md). `small-business` `crm-autopilot` covers HubSpot/Monday/Salesforce/Zoho; its smb-onboard examples literally script "we don't have a Pipedrive connector yet... Zapier or export a CSV". Stale vs. reality -> gap.
- claude-plugins-official (37k stars, 315 plugins): `hubspot-sales` (HubSpot-built: call-prep, daily-brief, follow-up, log-call, pipeline-pulse, import-contacts), `monday-crm`, `salesforce-development`, `carta-crm`. No Pipedrive plugin. Risk: Pipedrive ships one (see 7).
- Community MCPs (github): WillDent/pipedrive-mcp-server 60 stars, MIT, TS, v2 reads + preview-first writes; Wirasm/pipedrive-mcp 14 (stale since 2025-05); nubiia-dev/mcp-pipedrive 12 (300+ tools, too many); ckalima/pipedrive-mcp-server 9 (155 tools, gated deletes); comma-compliance/pipedrive-mcp 8 (75 tools, custom-field resolution, active). Plugins: Talentir/pipedrive-claude-plugin 0, p-wegner/pipedrive-skill 0. Aggregators: Composio, Pipedream, Zapier, n8n.
- Pipedrive AI (native): summaries, email gen (Premium+), win probability; no Claude, no cross-tool context.
Gap: nobody ships the opinionated Pipedrive workflow layer (HubSpot-sales equivalent) for Claude, nor a no-account CSV mode.

CRM target check: HubSpot/Salesforce/monday already have vendor plugins; Close is bundled in KWP sales; Attio (official MCP, 40+ tools) and folk (official MCP) are smaller, startup-skewed, and their users self-build; Zoho is covered by KWP small-business; Copper is small, Google-Workspace niche, no official MCP [U]. Pipedrive = largest SMB-pure base with a proven Claude-heavy MCP audience and zero workflow plugin. Recommendation: build Pipedrive. Design core skills CRM-agnostic over a normalized deal schema so Close/Attio/folk ports are cheap later.

## 3. Technical facts (verified unless [U])
- Base: https://{company}.pipedrive.com/api/v2/... (v1 still for notes, leads, some others).
- Auth: personal API token (Settings > Personal preferences > API), header `x-api-token`; one active token per user, rotating breaks integrations; full access to that user's data. OAuth 2.0 required for public Marketplace apps (install/uninstall flows, review).
- Rate limits (token-based since 2024-12 new / 2025-03..05 existing): daily budget = 30,000 x plan multiplier (Lite 1, Growth 2, Premium 5, Ultimate 7) x seats, cap 100M, resets local-DC midnight; 429 when out. Cost: get one 2, list 20, search 40, update 10, delete 6; v2 cheaper. Burst per 2s per user: API token 20/40/100/120, OAuth 80/160/400/480; search 10/2s all plans. Headers x-ratelimit-limit/remaining/reset. Budget example: 1-seat Lite = 30k tokens/day = ~1,500 list calls; ample, but search-heavy agents can burn it -> prefer list+filter over search.
- v2 endpoints: deals, persons, organizations, activities, products, pipelines, stages, search, *Fields. Notes: v1 /notes [U still v1]. Useful deal fields: stage_id, status, value, expected_close_date, last_activity_date, next_activity_date, update_time, stage_change_time; stage rotten_flag/rotten_days [U field names]. Custom fields come back as 40-char hash keys -> must map via /dealFields.
- Reuse vs build: REUSE official remote MCP (OAuth, permission-scoped, audit trail, directory-listed, zero install in Cowork/claude.ai). Do not bundle a community MCP. Optional fallback for Claude Code power users: tiny zero-dep script (curl/Node) with API token for read-only bulk pulls if official tools lack list-with-filter [U, test].

## 4. MVP
Hero workflow (<5 min): "Pipeline triage" -> paste/connect -> ranked list of stale/at-risk deals with reason, a drafted follow-up per deal, and proposed CRM updates as a diff the user approves. Works two ways: (a) official Pipedrive connector; (b) no account: user drops a Pipedrive deals CSV export (or our sample) and gets the same report, writes become a "paste into Pipedrive" change list.

Components (6):
1. skill `pipeline-triage` (hero): rotting + no-next-activity + past-close-date + stage-age scoring; follow-up drafts; read-only by default.
2. skill `log-touch`: call notes / email / transcript -> resolve person -> deal (never auto-create deal), propose note + activity + stage/value/close-date changes, show diff, write on approval.
3. skill `forecast-brief`: weighted pipeline by stage probability, commit vs best case, movement since last week, slipped deals; Monday-ready text.
4. skill `meeting-prep`: deal + person + org + last 5 notes/activities -> one-page brief with open questions.
5. skill `csv-mode`: normalize Pipedrive export headers (e.g. "Deal - Title", "Deal - Stage" style [U exact headers]) into the internal schema; used by 1/3/4 when no connector.
6. command `/pipedrive-setup`: detect connector, else offer CSV; capture stale threshold, pipelines, currency, tone.
MCP: none bundled; .mcp.json references official https://mcp.pipedrive.ai/mcp only if Claude Code needs it [U whether plugin may declare a directory connector]. Hooks: none.
Fixtures: `fixtures/deals_export.csv` (40 synthetic deals, 2 pipelines, mixed currencies, custom fields, 8 stale, 3 past close), `persons.csv`, `orgs.csv`, 3 call-note transcripts, 2 email threads, expected outputs. All fictional names/domains (example.com).
Omissions: no bulk deletes/merges, no sending email (drafts only), no lead scoring/enrichment, no Marketplace OAuth app, no scheduling (point users to Cowork scheduled tasks), no products/line items, no multi-CRM.

## 5. Eval (5 prompts)
1. "Which of my deals are going stale?" on fixture CSV -> pass: all 8 stale + 3 past-close flagged, no false positives on deals with future next activity; ranked by value x age; each has a reason.
2. "Log this call" + transcript naming "Dana at Acme" with 2 Acme deals -> pass: asks which deal or picks via title match with stated reason; proposes note + next activity with date; no write without approval; never creates a deal.
3. "Give me my forecast for this quarter" -> pass: weighted total matches fixture math within rounding; separates currencies; lists slipped deals.
4. "Prep me for my 2pm with Northwind" -> pass: brief cites only fixture facts (no invented contacts/values), includes last touch date and 3 questions.
5. Live connector, "move Globex to Proposal and set close date Nov 15" -> pass: resolves stage by name within the right pipeline, shows diff, one update call, confirms result; on 429 explains budget and stops retrying.

## 6. Distribution
- Channels: Pipedrive Community forum (community.pipedrive.com) [U guidelines on promo], Pipedrive Developers' Community, r/sales, r/smallbusiness, r/CRM, r/ClaudeAI, LinkedIn Pipedrive consultant/partner network, Indie Hackers. Submit to claude-plugins-official and our marketplace `plugin-creator` (brianshepardpss).
- Positioning: "The Pipedrive connector gives Claude access. This gives it a sales ops routine: triage, log, forecast, prep. Try it on a CSV in 2 minutes, no login."
- Name: avoid "Pipedrive" in product name/logo (Pipedrive is a registered TM of Pipedrive OU); use nominative "for Pipedrive" in description. Candidates: DealTender, Stale Deal Desk, Pipeline Tender [U TM search]. Repo slug `pipedrive` is fine as descriptor; add "not affiliated" line.
- Pipedrive Marketplace: listing requires a public OAuth app with install/uninstall flow + review; a Claude plugin with no own backend does not qualify. Defer; possible later as thin OAuth app or by approaching Pipedrive partnerships (their MCP team wants workflows).

## 7. Risks
- Pipedrive (or Anthropic KWP) ships an official Pipedrive skills plugin; KWP docs are stale but will update. Mitigate: ship fast, CSV mode, CRM-agnostic core.
- Official MCP is BETA; tool set may change or lack list-with-filter, forcing many search calls (40 tokens each) [U].
- Writes to customer CRM: wrong-deal logging erodes trust -> diff+approve always.
- Token budget on Lite single-seat; burst limits on search.
- Hallucinated CRM facts in drafts/prep; CSV header variance by locale/custom fields.
- Trademark/affiliation confusion.

## 8. Day-30 traction signal
Go: >=150 installs (marketplace + repo clones), >=40 GitHub stars, >=10 unsolicited user reports/issues from real Pipedrive accounts, and >=3 people asking for a second CRM or scheduled mode. Kill/pivot: <30 installs and no live-account usage reports.

Sources: pipedrive.com/en/newsroom (MCP launch 2026-06-30; Claude directory 2026-08-18), support.pipedrive.com/en/article/mcp-claude, pipedrive.readme.io (rate limiting, authentication, API v2, marketplace approval), github.com/anthropics/knowledge-work-plugins, github.com/anthropics/claude-plugins-official, github.com/HubSpot/hubspot-mcp-plugins, usecarly.com, breakcold.com, folk.app.
