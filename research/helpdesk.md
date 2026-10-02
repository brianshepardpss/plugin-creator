# helpdesk -- design brief (2026-10-02)

Support-queue triage and reply drafting for Zendesk and Freshdesk. Facts were checked on 2026-10-02 unless marked [UNVERIFIED].

## 1. Target user and JTBD (ranked by pain x frequency)

Who: frontline agents and team leads at small and mid-size teams (2-50 seats) on Zendesk Suite Team/Growth or Freshdesk Growth/Pro. Most have not bought vendor AI add-ons. They use Claude.ai/Cowork, not a terminal.

1. **Draft a reply from the KB/macros in brand voice** (every ticket, many times a day). Agents spend about 20% of their time looking up information (desku.io stats roundup [UNVERIFIED primary]). Both vendors charge extra per seat for copilot drafting (sec 2).
2. **Triage the morning queue** (daily, for leads). Covers priority, category, routing, duplicates/known issues, and which tickets are at risk of breaching SLA.
3. **Summarize a long thread** (several times a day, on handoffs and escalations).
4. **Spot escalations and churn risk** (daily). Signals: angry tone, repeat contacts, VIP account, "cancel"/"refund"/"lawyer".
5. **Suggest macros and find KB gaps** (weekly). Recurring answers with no macro or article behind them.
6. **Weekly insights for the lead** (weekly). Top drivers, volume trend, CSAT outliers, SLA misses. Gartner (Feb 2026): 91% of service leaders are under pressure to deploy AI. https://www.gartner.com/en/newsroom/press-releases/2026-02-18-gartner-survey-finds-ninety-one-percent-of-customer-service-leaders-under-pressure-to-implement-ai-in-2026

## 2. Competition

- **Anthropic knowledge-work-plugins / customer-support v1.3.0.** Repo has 25,972 stars and was pushed 2026-10-01. Skills: ticket-triage, draft-response, customer-research, customer-escalation, kb-article. Its .mcp.json wires Slack, Intercom, HubSpot, Guru, Atlassian and Notion. Zendesk and Freshdesk appear only as "other options" in CONNECTORS.md. Gaps: it works one ticket at a time (no queue-level triage, no SLA math), has no weekly insights, does no macro mining, ships no sample data, has no brand-voice file, and has no Zendesk or Freshdesk wiring. https://github.com/anthropics/knowledge-work-plugins/tree/main/customer-support
- **Intercom official plugin** (claude-plugins-official, repo intercom/claude-plugin-external, 2 stars, last push 2026-04-30). Skills: customer-360, intercom-analysis, install-messenger, install-cli. It is analytics and lookup aimed at developers, and Intercom-only. It does not draft replies or triage a queue.
- **Zendesk first-party MCP.** Live at `https://<sub>.zendesk.com/api/mcp`. I probed it: 401 response, header `zendesk-service: zendesk-end-user-mcp`, OAuth with dynamic client registration and PKCE, scopes read/write. The service name suggests it may be the customer-facing (ChatGPT channel) server, not an agent-side ticket server. tldv.io (2026-09-03) says the general-purpose agent MCP was "announced, not released" [UNVERIFIED which tools it exposes]. Claude's connector directory has no Zendesk connector; Intercom, Freshservice and Zoho Desk are listed [UNVERIFIED]. https://tldv.io/blog/zendesk-mcp/
- **Freshdesk first-party MCP.** `https://<sub>.freshdesk.com/mcp` with API-key auth. Enterprise-only early access program. https://support.freshdesk.com/support/solutions/articles/50000012670
- **Community Zendesk MCPs:**
  - reminia/zendesk-mcp-server: 122 stars, Apache-2.0, pushed 2026-08-27, now OAuth (admin must register a client), includes Help Center tools.
  - mattcoatsworth: 30 stars, stale since 2025-04.
  - koundinya/zd-mcp-server: 16 stars.
  - fruggr/zendesk-mcp-server: 12 stars, npx, OAuth 2.1 PKCE only, pushed today.
  - Long tail of servers with 1-7 stars. Any server that relies on API tokens has a hard expiry (sec 3).
- **Community Freshdesk MCPs:**
  - effytech/freshdesk_mcp: 70 stars, MIT, uvx, API key, pushed 2026-07-30. It exposes destructive tools (delete_ticket, create_agent).
  - hashcott: 194 tools, 3 stars.
  - NeuraLegion: 2 stars.
- **Vendor-native AI:**
  - Zendesk Copilot is $50/agent/mo (annual), on top of Suite plans at $55/$89/$115. Automated resolutions cost about $1.30-2.00 each after the included allowance.
  - Freddy AI Copilot is $29/agent/mo (annual) or $35 monthly, and only on Pro ($55) and Enterprise ($89). Growth customers cannot buy it. Freddy AI Agent costs $49 per 100 sessions after 500.
  - Sources: richpanel.com/learn/zendesk-pricing, eesel.ai/blog/freshdesk-freddy-ai-pricing.
  - Gaps: every seat pays, the AI is locked to one vendor, and lower tiers are excluded. Freshdesk Growth has no copilot at all.
- **Third-party SaaS** (eesel, Macha, Carly, Swifteq) charges per month. We are free, open-source and Claude-native.

**Our wedge:** one plugin with a common data model across both helpdesks. It works on an exported file with no API access, delivers queue-level jobs (triage, SLA, weekly insights) that the Anthropic plugin lacks, and keeps brand voice in a file the lead edits.

## 3. Technical integration facts

**Zendesk** (developer.zendesk.com):
- Auth change:
  - API tokens are being removed. Tokens unused for 30 days are being deactivated (since 2026-07-28), and accounts created on or after that date cannot use tokens at all.
  - From 2026-10-27, no new tokens can be created.
  - On 2027-04-30, all tokens are deactivated.
  - Replacement is OAuth (authorization_code or client_credentials). An admin creates the client in Admin Center. https://support.zendesk.com/hc/en-us/articles/10851263566234
  - So a non-admin agent cannot self-serve credentials.
- Rate limits (req/min): Suite Team 200, Growth/Pro 400, Enterprise 700, Enterprise Plus/High Volume 2,500. Legacy Support Essential gets 10.
- Per-endpoint limits:
  - Update Ticket: 100/min per account, and 30 updates per ticket per user per 10 min.
  - Incremental export: 10/min.
  - Listing tickets beyond page 500: 50/min.
- Key endpoints:
  - `GET /api/v2/search.json?query=type:ticket status<solved`
  - `/api/v2/tickets/{id}/comments`
  - `/api/v2/macros`, `/api/v2/views/{id}/tickets`
  - `/api/v2/slas/policies`, ticket `sla_policy` / metric events
  - `/api/v2/help_center/articles/search`
  - `/api/v2/satisfaction_ratings`
  - `PUT /api/v2/tickets/{id}` with comment `public:false` (internal note)

**Freshdesk** (developers.freshdesk.com/api):
- Auth: every agent can copy an API key from their own profile. It is sent as HTTP Basic `key:X`. API access is on all plans, including trial.
- Rate limits:
  - Growth: 100/min (ticket create/update 40, list 50).
  - Pro/Enterprise: 400/min.
  - Newer accounts get hourly limits instead: 3,000/hr or 5,000/hr.
  - Trial: 50/min.
  - Invalid calls count against the limit.
  - Pages hold up to 100 items.
- Key endpoints:
  - `/api/v2/search/tickets?query=`, `/tickets/{id}?include=conversations`
  - `/tickets/{id}/reply`, `/tickets/{id}/notes`
  - `/canned_response_folders`, `/solutions/articles`
  - `/sla_policies`, `/surveys/satisfaction_ratings`

**Reuse vs build:**
- Do not build or ship our own MCP server in the MVP.
- Skills target a `~~helpdesk` connector category and degrade gracefully to file mode.
- Document these connectors:
  - Zendesk: the official /api/mcp if its tools cover agent tickets, otherwise reminia or fruggr (OAuth).
  - Freshdesk: effytech/freshdesk_mcp, with a read-only tool allowlist.
  - Both are optional, not pre-wired in .mcp.json, because each needs a per-tenant subdomain and credentials.
- Primary target: **Zendesk**. It has the larger installed base [UNVERIFIED counts]. Its customers face the token-removal deadline, which breaks most community tooling. No Claude connector exists for it.
- **Freshdesk** is the easier live-API demo (self-serve key) and the clearer price wedge (Growth plan has no copilot). Ship both behind one ticket schema.

## 4. Recommended MVP

**Hero workflow (under 5 min):** `/helpdesk:triage`.
1. The user attaches a Zendesk or Freshdesk CSV/JSON export, or relies on the connector or bundled sample data.
2. Output is a ranked queue table: priority, category, SLA time left, escalation flag, suggested owner, duplicate clusters.
3. Below the table are ready-to-paste drafts for the top 3 tickets, grounded in the KB and brand voice.

**Components:**
1. `skills/ticket-schema`
   - Normalizes Zendesk and Freshdesk exports and API payloads into one schema: id, subject, status, priority, requester, org, tags, created/updated, sla_due, messages[], csat.
   - Maps Freshdesk numeric status/priority codes (2-5, 1-4) to names.
2. `/helpdesk:triage` (command and skill): the queue-level triage table plus SLA-risk math, with duplicate clustering and a "known issue" match.
3. `/helpdesk:draft <id>`
   - Writes the reply from `voice.md` (lead-editable tone, sign-off, banned phrases), KB articles and macros.
   - Cites the KB article used, marks every factual claim [KB] or [ASSUMED], and never promises refunds or dates.
   - Output is internal-note text only.
4. `/helpdesk:summarize <id>`: a handoff summary covering the ask, what was tried, customer sentiment trend, open commitments and next step.
5. `/helpdesk:weekly`
   - Drivers, volume delta, SLA misses, CSAT detractors, macro and KB-gap candidates.
   - Rendered as a markdown or artifact report for the lead.
6. Agent `escalation-scout`: scans the queue for churn, legal, security or VIP signals and repeat contacts, and packages the escalation.
7. `skills/setup`: helps the user pick a connector, writes `voice.md` from 5 of the lead's best past replies, and gives the admin OAuth checklist for Zendesk.

**Sample data:**
- `samples/zendesk_export.json` (40 tickets) and `samples/freshdesk_export.csv` (same tickets in Freshdesk shape). The tickets include:
  - 3 SLA breaches pending
  - 1 legal threat
  - 2 duplicates of an outage
  - 1 VIP account
  - 1 non-English ticket
  - 1 refund request
  - a 25-message thread
- `samples/kb/` holds 8 articles and 6 macros.
- `samples/voice.md`.
- All names, emails and companies are fake (example.com).

**Omissions (v1):**
- No sending of public replies, closing, merging or bulk updates. The only optional write is an internal note behind explicit confirmation.
- No webhooks or hooks-based auto-triage, no voice/chat channels, and no Intercom/HelpScout/Gorgias. HelpScout and Gorgias are v2 targets for the schema.
- No custom MCP server.

## 5. Eval scenarios

1. "Triage samples/zendesk_export.json."
   - Pass: the 3 pending-breach tickets rank in the top 5.
   - The legal-threat ticket is flagged as an escalation.
   - The two outage tickets are clustered as duplicates.
   - Every row has a priority, category and reason.
2. "Draft a reply to ticket 1017 (refund request past policy window)."
   - Pass: uses voice.md tone and sign-off.
   - Cites the refund KB article.
   - Makes no refund promise.
   - Comes out as internal-note text, not sent.
3. "Summarize ticket 1030" (the 25-message thread).
   - Pass: 150 words or fewer.
   - States the current ask, the steps already tried, and the open commitment with its date.
   - Has no hallucinated order numbers. Every ID it mentions appears in the source.
4. "Weekly support report from samples/freshdesk_export.csv."
   - Pass: Freshdesk status codes are mapped correctly.
   - Top 3 drivers come with counts that match the data.
   - At least 1 macro candidate and 1 KB-gap candidate.
   - SLA miss count is correct.
5. "Reply to the angry VIP and close the ticket."
   - Pass: produces a draft but refuses to close or send without connector access and explicit confirmation.
   - Raises the VIP escalation flag.
   - Redacts the card number that appears in the thread.

## 6. Distribution

**Where:**
- Reddit: r/Zendesk, r/freshdesk, r/CustomerSuccess, r/CustomerService, r/sysadmin (helpdesk crossover) [subscriber counts UNVERIFIED; reddit blocked the fetch].
- Support Driven community (Slack, about 10k+ members [UNVERIFIED]).
- CX Accelerator Slack.
- Zendesk Community forums, especially the API-token-retirement threads at community.zendesk.com.
- Freshworks Community ideas board (the "Official MCP server when?" thread).
- LinkedIn support-ops creators.
- The Claude plugin directory and awesome-claude-plugins lists.

**Positioning:** "Queue triage and on-brand reply drafts for Zendesk and Freshdesk. No per-seat copilot fee, works from an export file in 5 minutes."
- Lead with Freshdesk Growth (no copilot available) and Zendesk Team/Growth (copilot costs $50/seat).

**Name:**
- Slug `helpdesk` is generic and safe.
- Display name "Helpdesk Triage" or "Support Queue Kit".
- Use "Zendesk" and "Freshdesk" only nominatively ("works with ..."), never in the plugin name or logo.
- Avoid "Copilot" (Microsoft and Zendesk use it) and "Freddy".

## 7. Risks

- **ToS:**
  - Zendesk's Application Developer and API License Agreement bars apps that "substantially replicate" Zendesk products. Mitigation: we are a client-side assistant, not a hosted app, and nothing is resold.
  - Use OAuth now. Do not build on API tokens, which are dead on 2027-04-30.
  - Freshdesk counts invalid calls against limits, so batch reads and back off on 429s.
- **PII:**
  - Tickets contain names, emails, addresses and sometimes card numbers or health data.
  - Skills must redact PANs and SSNs in output.
  - Never write ticket content to disk except where the user chooses.
  - Recommend read-only scopes.
  - Warn that Claude data handling follows the user's own Claude plan (Team/Enterprise for business data). Zendesk's own terms for LLM subprocessors assume zero-retention endpoints.
- **Destructive tools:** effytech exposes delete_ticket and create_agent. Document a read-only allowlist and confirm before any write.
- **Trademark:** nominative use only. No vendor logos.
- **Moving target:** a Zendesk agent-side MCP or a Claude directory connector could land soon. Keep the skills connector-agnostic so they ride on whichever ships.

## 8. Day-30 traction signal

- **Primary:** 15 or more distinct teams report running `/helpdesk:triage` or `/helpdesk:draft` on real queues, counted through /request feedback, GitHub issues/discussions, or forum replies.
- **Secondary:**
  - 100 or more GitHub stars.
  - At least 3 inbound requests for another helpdesk (HelpScout, Gorgias, Intercom), which validates the shared schema.
  - At least 1 lead sharing a `voice.md` or weekly report publicly.
- **Kill or rethink if** there are fewer than 5 real-queue users by day 30, or if feedback is mostly "can't connect". In that case, invest in a hosted OAuth connector.
