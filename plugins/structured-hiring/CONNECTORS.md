# Connectors

Skills refer to tool categories with the `~~category` convention used by
Anthropic's knowledge-work plugins. Everything works without any connector
(sample data, paste, CSV).

| Category | Used for | Options |
|---|---|---|
| ~~ATS | read scorecards, interview plans, pipeline; confirmed stage changes | Greenhouse official MCP (bundled: `https://mcp.us.greenhouse.io/mcp`; claude.ai connector `https://mcp.greenhouse.io/mcp`), Ashby official MCP (bundled: `https://mcp.ashbyhq.com/mcp/v1`). Lever: no official MCP; use CSV export. |
| ~~email | outreach and hiring-manager updates as drafts | Gmail connector (drafts only) |
| ~~calendar | optional: interview dates for the pipeline view | Google Calendar connector |

Both bundled ATS servers use OAuth with your own account and inherit your
ATS permissions. No API keys are stored by this plugin. Greenhouse: an admin
enables MCP access (Core, Plus, Pro plans); default scopes are read-only.
Ashby: an org admin opts in; each user signs in.

If you do not use one of them, ignore its "needs authentication" status, or
disable it with `/mcp`.
