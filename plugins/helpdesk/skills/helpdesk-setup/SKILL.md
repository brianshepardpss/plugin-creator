---
name: helpdesk-setup
description: Use when a team is setting up Helpdesk Triage for their own queue, or says "set up helpdesk", "connect Zendesk", "connect Freshdesk", "write our brand voice", "make a voice.md from my best replies", "use our own KB and macros", "add our VIP accounts", or "how do I get API access". Writes the team folder (voice.md, kb/, vip-accounts.txt), explains export or connector options, and gives the Zendesk admin OAuth checklist.
---

# Set up Helpdesk Triage for a team

Everything here is optional; the plugin works on an export file alone.
Write files only into the folder the user picks (default `./helpdesk/`),
and show each file before writing it.

## 1. Choose how tickets get in

Ask which helpdesk and plan they use, then recommend:

- **Export file (works for everyone, no admin needed).**
  - Zendesk: Admin Center > Account > Tools > Reports/Export (JSON includes
    the most), or a view exported as CSV.
  - Freshdesk: Tickets list > Export, choose CSV, tick the fields in
    `../ticket-schema/schema.md` and "Show multiline text fields" for the
    description. Note the account time zone for `--tz`.
- **Live connector (optional).** Read `connectors.md` in this skill's
  directory and walk the user through the option that fits. Recommend
  read-only scopes. Never ask the user to paste a token or key into chat;
  keys go into the connector's own settings.

## 2. Write voice.md from their best replies

1. Ask the lead for 5 replies they consider great (pasted text or ticket
   ids). Pipe pasted text through
   `python3 ../ticket-schema/scripts/helpdesk.py redact` first.
2. Extract: greeting pattern, sign-off, sentence length, formality, how
   they apologize, words they use for the product, phrases they avoid.
3. Fill this template and show it for approval before writing:

   ```
   # <Company> Support voice
   ## Tone
   - <3-5 bullets, observed from the samples>
   ## Greeting and sign-off
   - Greeting: "<pattern>"
   - Sign-off: <exact lines with {agent_first_name}>
   ## Always
   - Say what happens next and who does it.
   - Reply in the customer's language.
   - <team-specific>
   ## Never
   - Promise a refund, credit, discount or a fix date unless a help article states it.
   - Ask the customer to send a full card number or password.
   - <banned phrases observed or requested>
   ```
   Keep the two "Never" safety lines; the lead may add, not remove, them.
4. Tell the lead: edit `voice.md` any time; every draft reads it fresh.

## 3. KB, macros, known issues, VIPs

Create (or point at) `./helpdesk/kb/` with the same layout as
`../../samples/kb/`:
- `*.md` articles with frontmatter `id`, `title`, `category` (category names
  from `../ticket-schema/scripts/categories.json`; offer to edit those
  keywords to match their product).
- `macros.json`: list of `{id, title, category, body}`. Freshdesk canned
  responses and Zendesk macros can be pasted in and converted.
- `known-issues.md`: one `## <id>` section per incident with `Status`,
  `Summary`, `Category`, `Match keywords`.
- `vip-accounts.txt`: one org name, email or email domain per line.

## 4. Data handling (say this once)

Ticket content goes to Claude under the user's own Claude plan; business
data belongs on a Team or Enterprise plan with the org's approval. The
plugin writes nothing to the helpdesk except an internal note the user
explicitly confirms, and writes files only where the user chooses.

## 5. Finish

Run `/helpdesk:triage` on their export (or `sample`) with `--kb ./helpdesk/kb`
and show the first rows, so they see it working with their own files.
