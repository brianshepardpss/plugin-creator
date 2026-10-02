# Optional live connectors

Helpdesk Triage never requires a connector. Skills refer to "the helpdesk
connector" generically and fall back to export files. Facts checked
2026-10-02; this area moves fast, so re-check vendor docs before relying on
any of it. The plugin bundles no MCP server and no `.mcp.json`, because each
helpdesk needs a per-tenant subdomain and credentials.

## Rules for any connector

- Read-only first. Grant write only if the team wants internal notes.
- Credentials go into the connector's own settings or your local MCP
  config, never into chat.
- Allow only these tools: list/search tickets, get ticket, get comments or
  conversations, get ticket fields, and (optional) add private note.
  Block delete, create, update, reply and agent/contact management tools.
  In Claude Code you can deny them in `.claude/settings.json`, for example
  `"permissions": {"deny": ["mcp__freshdesk__delete_ticket",
  "mcp__freshdesk__create_ticket_reply", "mcp__freshdesk__update_ticket"]}`.
- Rate limits: Zendesk Suite Team 200 req/min, Growth/Professional 400,
  Enterprise 700. Freshdesk Growth 100/min, Pro/Enterprise 400/min, trial
  50/min; failed calls count. Fetch in pages of 100 and stop on HTTP 429.

## Zendesk

- **Official Zendesk MCP (remote, OAuth):** `https://<subdomain>.zendesk.com/api/mcp`.
  Uses OAuth with dynamic client registration. In Claude.ai or Cowork add
  it under Settings > Connectors > Add custom connector. As of 2026-10-02
  it identifies itself as an end-user service and may not expose
  agent-side ticket tools; if its tool list has no ticket search or
  comments, use an export file instead.
- **Community servers (local; Claude Code or Claude Desktop only, not the
  Cowork web app):**
  - `fruggr/zendesk-mcp-server` (`npx -y @fruggr/zendesk-mcp-server <subdomain>`),
    OAuth 2.1 with PKCE, `read` scope is enough for triage.
  - `reminia/zendesk-mcp-server`: OAuth with an admin-registered client;
    scopes `tickets:read users:read hc:read` for read-only. Its
    `create_ticket_comment` tool is PUBLIC by default; always pass
    `public: false`, or leave `tickets:write` out entirely.
- **API tokens are being retired.** Tokens unused for 30 days are being
  deactivated (since 2026-07-28), new tokens cannot be created from
  2026-10-27, and all tokens stop working on 2027-04-30. Do not set up
  anything new on API tokens; use OAuth.

### Zendesk admin OAuth checklist (send this to your admin)

1. Admin Center > Apps and integrations > APIs > OAuth Clients > Add OAuth client.
2. Name it "Helpdesk Triage (read-only)", client kind as the server's
   README says (public for PKCE servers), redirect URL exactly as the
   server documents.
3. Scopes: read only (`read`, or `tickets:read users:read hc:read`). Add
   write only for internal notes.
4. Save the identifier; agents sign in with their own Zendesk login when the
   connector opens the OAuth window. Non-admin agents cannot create this
   client themselves.

## Freshdesk

- **Official Freshdesk MCP:** `https://<subdomain>.freshdesk.com/mcp` with
  API-key auth; Enterprise-only early access as of 2026-10-02.
- **Community server (local):** `effytech/freshdesk_mcp` via `uvx`, env
  `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN`. Every agent can copy their
  own API key from Profile settings; API access is on all plans, including
  trial. It exposes destructive tools (`delete_ticket`, `update_ticket`,
  `create_ticket_reply`); allow only `get_tickets`, `get_ticket`,
  `search_tickets`, `get_ticket_conversation`, `get_ticket_fields`, and
  `create_ticket_note` (notes are private) if you want internal notes.

## Writing an internal note by API (reference)

- Zendesk: `PUT /api/v2/tickets/{id}` with
  `{"ticket": {"comment": {"body": "...", "public": false}}}`. This is the
  only update the plugin ever makes: send the comment and nothing else (no
  status, assignee or tags), and always set `public: false`.
- Freshdesk: `POST /api/v2/tickets/{id}/notes` with
  `{"body": "...", "private": true}`.
