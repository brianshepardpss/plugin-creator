# Queue triage, as of 2026-10-02T09:00:00Z (exported_at)
Source: zendesk export, 40 tickets, 16 open (new/open/pending/hold).
SLA breached: 0. SLA due within 4h: 3. Escalations (legal/security/vip): 4. Duplicate clusters: 1.

| # | Ticket | Subject | Pri | Category | SLA left | Flags | Owner | Dup | Why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1026 | THIRD TIME asking - card charged but plan dow... | urgent | billing | 8h30m | churn, anger, vip, pii-redacted | Team lead | - | SLA due in 8h30m; urgent priority (score 110) |
| 2 | 1004 | Bookings not appearing in Google Calendar | high | calendar-sync | 0h45m | - | Tier 2 | - | SLA due in 0h45m; high priority (score 95) |
| 3 | 1009 | New vet can't see her schedule | high | staff-permissions | 2h30m | - | Tier 1 | - | SLA due in 2h30m; high priority (score 95) |
| 4 | 1021 | Deleted client notes - consulting my lawyer | high | data-loss | 22h00m | legal, anger | Team lead | - | SLA due in 22h00m; high priority (score 95) |
| 5 | 1012 | Export is missing prices | normal | data-export | 3h15m | - | Tier 2 | - | SLA due in 3h15m (score 80) |
| 6 | 1040 | Unknown login from another country | normal | access | 23h30m | security, repeat | Team lead | - | SLA due in 23h30m (score 75) |
| 7 | 1037 | Cancel our subscription | normal | cancellation | 22h05m | churn, vip | Team lead | - | SLA due in 22h05m (score 70) |
| 8 | 1036 | SMS reminders not sending since this morning | high | outage | 5h40m | - | Tier 2 | C1 | SLA due in 5h40m; high priority; known issue KI-2026-10-02-sms (score 45) |
| 9 | 1038 | Clients didn't get text reminders today | high | outage | 6h55m | - | Tier 2 | C1 | SLA due in 6h55m; high priority; known issue KI-2026-10-02-sms (score 45) |
| 10 | 1032 | Booking form custom question for parents | normal | booking-form | 9h20m | repeat | Tier 1 | - | SLA due in 9h20m (score 40) |
| 11 | 1039 | Time zone wrong again on reminders | normal | timezone | 23h10m | repeat | Tier 2 | - | SLA due in 23h10m (score 40) |
| 12 | 1017 | Refund for annual renewal | normal | billing | 1d01h | churn, repeat | Billing | - | routine (score 37) |
| 13 | 1033 | No se sincroniza el calendario de Google | normal | calendar-sync | 11h10m | lang:es | Tier 2 | - | SLA due in 11h10m (score 30) |
| 14 | 1030 | Double bookings after Google Calendar sync | normal | calendar-sync | 1d03h | - | Tier 2 | - | waiting 10d; known issue KI-2026-09-ENG-4471 (score 20) |
| 15 | 1034 | Reset two-factor for former manager | normal | access | paused | - | Tier 1 | - | routine (score 10) |
| 16 | 1035 | Please add Apple Calendar | low | feature-request | 1d21h | - | Product | - | routine (score 0) |

## Duplicate clusters
- C1: tickets 1036, 1038 -> known issue KI-2026-10-02-sms

## Known-issue matches
- 1036: KI-2026-10-02-sms (investigating (since 2026-10-02 06:00 UTC))
- 1038: KI-2026-10-02-sms (investigating (since 2026-10-02 06:00 UTC))
- 1030: KI-2026-09-ENG-4471 (fix scheduled for the 2026-10-06 release)

Note: card numbers or other sensitive numbers were found and redacted in 1026. Ask an admin to redact them in the helpdesk too.
