# Sample data

Everything here is fake. Quillfern is a fictional booking-software company;
every person, company, email address and card number is made up
(example.com/.org/.net, test card number).

- `zendesk_export.json`: 40 tickets in Zendesk API shape (tickets with
  `comments`, `slas` and `metric_set`, plus `users`, `organizations`,
  `groups` sideloads). `exported_at` is 2026-10-02T09:00:00Z.
- `freshdesk_export.csv`: the same 40 tickets as a Freshdesk UI export
  (Description only, no replies). Deliberately messy: some rows carry numeric
  status/priority codes, and there is one blank row.
- `kb/`: 8 help articles, `known-issues.md` and 6 macros in `macros.json`.
- `voice.md`: an example brand-voice file.
- `generate.py`: maintainers regenerate the two exports with it.

What is planted: 3 tickets about to breach SLA (1004, 1009, 1012), a legal
threat (1021), two tickets about the same SMS outage (1036, 1038), a VIP
account with a pasted card number (1026), a Spanish ticket (1033), a refund
request past the 14-day window (1017) and a 25-message thread (1030).
