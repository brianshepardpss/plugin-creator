# Getting deal data into DealTender

Every skill runs the same script, `scripts/dealtender.py` at the plugin root
(two directories up from any skill's directory). It always reads a deals CSV.
Pick the source in this order.

## 1. The bundled sample (no account)

Use when the user says "sample", "demo", "try it", or has no data yet. Pass the
word `sample` instead of a path. The script then uses `samples/stages.json`,
`samples/settings.json`, `samples/persons.csv`, `samples/activities.csv` and
the sample's fixed date, 2026-10-05. Say once that the data is fictional.

## 2. A Pipedrive CSV export the user provides

1. Run `python3 <plugin>/scripts/dealtender.py load <file>` first.
2. If it says MISSING REQUIRED COLUMNS or warns about status values, write `map.json` mapping the user's
   header text to the canonical keys it lists (for example
   `{"Etapp": "stage", "Tehingu nimi": "title"}`) and pass `--map map.json`
   to every later command. Status values in another language go in the
   same file: `{"status_values": {"Offen": "open", "Gewonnen": "won"}}`.
   Ask the user only if a header is truly ambiguous.
3. Stage probabilities and rotting days are not in a deals export. Look for
   `dealtender-settings.json` and `stages.json` next to the CSV or in the
   working folder (written
   by `/deal-tender:setup`). If absent, the script uses a 14-day threshold and
   the forecast cannot weight deals: tell the user and offer setup.
4. Export tip for users: Pipedrive list view of Deals > "..." > Export
   filter results > CSV. Include the columns Last activity date, Next activity
   date, Expected close date, Pipeline, Stage, Status.

## 3. The Pipedrive connector (live)

The official Pipedrive remote MCP server (`https://mcp.pipedrive.ai/mcp`,
OAuth sign-in, BETA) exposes tools such as `getDeals`, `getDeal`,
`updateDeal`, `searchDeals`, `getStages`, `getActivities`, `addActivity`,
`getNotes`, `addNote`, `getPersons`, `searchPersons`, `getOrganizations`.
In Claude Code they may be prefixed (for example
`mcp__plugin_deal-tender_pipedrive__getDeals`); in Cowork and claude.ai they
come from the user's Pipedrive connector. Tool names and fields can change
while the server is BETA: adapt to what the tool list actually shows.

Fetch, then hand the data to the script:

1. `getStages` (all pipelines). Write `stages.json` in the working folder in
   the shape of `samples/stages.json`, keeping each stage's `id`,
   `deal_probability` as `probability` and `rotten_days`.
2. `getDeals` with status `open` (and `won` for the forecast's period),
   paging until done. Prefer list calls over `searchDeals`: search costs
   about twice as much of the daily API budget.
3. Write `deals_live.csv` with these headers: `Deal - ID, Deal - Title,
   Deal - Value, Deal - Currency, Deal - Pipeline, Deal - Stage,
   Deal - Status, Deal - Owner, Deal - Organization, Deal - Contact person,
   Deal - Probability, Deal - Expected close date, Deal - Deal created,
   Deal - Last stage change, Deal - Last activity date,
   Deal - Next activity date, Deal - Won time`. Translate ids to names using
   the stages you fetched. If the deal objects lack last/next activity dates,
   call `getActivities` per flagged-candidate deal (done = latest due date,
   not done = earliest due date) rather than for every deal.
4. Run the script on `deals_live.csv` exactly as for a CSV export.
5. For meeting prep and logging, also write (only the rows you need):
   - `persons.csv`: `Person - ID, Person - Name, Person - Organization,
     Person - Email, Person - Phone, Person - Job title`
   - `activities.csv`: `Activity - ID, Activity - Subject, Activity - Type,
     Activity - Due date, Activity - Done (Done / To do), Activity - Deal ID,
     Activity - Deal, Activity - Contact person, Activity - Organization,
     Activity - Note`. Put each note from `getNotes` here too, as Type
     `note`, Done `Done`, Due date = the note's add date, Note = its text
     (strip HTML).
   Pass them with `--persons persons.csv --activities activities.csv`.

## Rate limits and failures

Pipedrive gives each company a daily token budget (30,000 x plan multiplier
x seats; Lite 1, Growth 2, Premium 5, Ultimate 7) plus a 2-second burst
limit, and returns HTTP 429 when either runs out. On a 429 or "rate limit"
error: stop calling tools, tell the user the budget resets at midnight in
their Pipedrive data-centre time zone, and offer CSV mode. Never loop on
retries.
