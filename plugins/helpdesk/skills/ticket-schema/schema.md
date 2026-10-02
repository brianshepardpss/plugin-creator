# Field mapping

Read this only when an export does not load cleanly or a user asks how a
field is derived.

| Schema field | Zendesk API JSON | Freshdesk API JSON | CSV header aliases (case-insensitive) |
|---|---|---|---|
| id | `id` | `id` | Ticket ID, ID, Ticket #, # |
| subject | `subject` | `subject` | Subject, Title |
| status | `status` (new/open/pending/hold/solved/closed) | `status` code 2-7 | Status (name or code) |
| priority | `priority` (low/normal/high/urgent) | `priority` code 1-4 | Priority (name or code) |
| requester | `requester_id` -> `users[]` sideload | `requester` (include=requester) | Full name / Requester / Contact; Email / Requester email |
| org | `organization_id` -> `organizations[]` (tags used for VIP) | `company` (include=company) | Company Name, Organization, Company |
| tags | `tags[]` | `tags[]` | Tags (comma, or space-separated for Zendesk) |
| created_at / updated_at | `created_at` / `updated_at` | same | Created time / Created at; Last update time / Updated at |
| solved_at | `metric_set.solved_at` (include=metric_sets) | `stats.resolved_at` (include=stats) | Resolved time, Solved at, Closed time |
| sla_due | earliest `slas.policy_metrics[].breach_at` (include=slas) | `fr_due_by` until first response, then `due_by` | Due by Time, Next SLA breach, SLA due, Due date |
| sla_paused | all policy metrics have stage `paused` | status pending/hold | status pending/hold |
| assignee / group | `assignee_id` -> users, `group_id` -> groups | `responder_id`, `group_id` (ids only) | Agent / Assignee; Group |
| csat | `satisfaction_rating.score` good/bad (offered/unoffered = none) | survey rating 103..-103 (>100 good, 100 neutral, <0 bad) | Satisfaction Rating text ("Extremely Happy", "Unhappy") |
| messages | `comments[]` (`public:false` = internal note) | `description_text` + `conversations[]` (`incoming`, `private`) | Description only |

Derived by the script (not stored in either tool): `category` (keyword rules
in `scripts/categories.json`), `language`, escalation `flags`,
`known_issue`, `repeat_of`, `sla_minutes_left`, `score`. Formulas are in the
docstring at the top of `scripts/helpdesk.py`.

## Useful read endpoints (for connector builders)

- Zendesk: `GET /api/v2/search.json?query=type:ticket status<solved`,
  `GET /api/v2/tickets/{id}.json?include=slas,metric_sets`,
  `GET /api/v2/tickets/{id}/comments.json`, `GET /api/v2/macros`,
  `GET /api/v2/help_center/articles/search.json?query=`,
  `GET /api/v2/satisfaction_ratings`.
- Freshdesk: `GET /api/v2/search/tickets?query="status:2"`,
  `GET /api/v2/tickets/{id}?include=conversations,requester,stats`,
  `GET /api/v2/canned_response_folders`, `GET /api/v2/solutions/articles/{id}`,
  `GET /api/v2/surveys/satisfaction_ratings`.
