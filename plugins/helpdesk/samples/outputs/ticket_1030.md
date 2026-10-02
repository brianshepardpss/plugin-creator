# Ticket 1030: Double bookings after Google Calendar sync
Status: open | Priority: normal | Category: calendar-sync | Language: en | Flags: -
Requester: Avery Sample (Maple Row Dental (Sample)) | Assignee: Casey Escalante | Group: Tier 2
Created: 2026-09-22T09:00:00Z | SLA due: 2026-10-03T12:00:00Z (1d03h from as-of 2026-10-02T09:00:00Z)
Known issue: KI-2026-09-ENG-4471 | Repeat of: -
Messages: 25

[1] 2026-09-22T09:00:00Z customer Avery Sample (public):
Since last week the Google Calendar sync is creating double bookings for two of our hygienists. Example bookings BK-55102 and BK-55117 both show twice.

[2] 2026-09-22T10:30:00Z agent Sam Agentson (public):
Thanks Avery. Could you disconnect and reconnect Google Calendar under Settings > Integrations and tell me if new bookings still duplicate?

[3] 2026-09-22T14:10:00Z customer Avery Sample (public):
Done, reconnected both hygienists. Still duplicates on new bookings this afternoon.

[4] 2026-09-22T15:00:00Z agent Sam Agentson (public):
Thank you. Next, please clear the browser cache and check the sync direction is set to two-way.

[5] 2026-09-23T08:45:00Z customer Avery Sample (public):
Cache cleared. Sync is two-way. Still getting doubles.

[6] 2026-09-23T09:30:00Z agent Sam Agentson (public):
Let's try one-way sync (Quillfern to Google) for a day to see if the duplicates stop.

[7] 2026-09-24T08:20:00Z customer Avery Sample (public):
One-way sync for a day: fewer doubles but still 3 yesterday.

[8] 2026-09-24T09:00:00Z agent Sam Agentson (public):
I'm escalating to our Tier 2 team. Casey will take it from here.

[9] 2026-09-24T11:00:00Z agent Casey Escalante (public):
Hi Avery, Casey here. Can you re-authorize Google access for both hygienists and confirm their calendar time zone matches the clinic time zone?

[10] 2026-09-24T15:30:00Z customer Avery Sample (public):
Re-authorized. Time zones both say America/Chicago, same as the clinic.

[11] 2026-09-25T09:10:00Z agent Casey Escalante (public):
Thanks. Please send the sync log export from Settings > Integrations > Download log for one hygienist.

[12] 2026-09-25T13:00:00Z customer Avery Sample (public):
Attached the log export for Hygienist A (sync-log-0925.csv).

[13] 2026-09-25T16:00:00Z agent Casey Escalante (public):
Got it, I see the same booking pushed twice within a second. I've filed this with engineering as ENG-4471.

[14] 2026-09-26T08:30:00Z customer Avery Sample (public):
OK. Meanwhile patients are showing up to the same slot. What should we do?

[15] 2026-09-26T09:00:00Z agent Casey Escalante (public):
As a workaround, please keep the one-way sync on and check the day view each morning for duplicates.

[16] 2026-09-28T10:15:00Z customer Avery Sample (public):
We had two patients double booked on Friday. This is costing us money.

[17] 2026-09-28T11:00:00Z agent Casey Escalante (public):
I'm sorry about Friday. I've asked engineering to prioritize ENG-4471 and will share their timeline.

[18] 2026-09-29T08:00:00Z customer Avery Sample (public):
Any timeline yet?

[19] 2026-09-29T09:30:00Z agent Casey Escalante (public):
Engineering confirmed the cause: a retry in the Google push that does not check for an existing event. They are working on the fix.

[20] 2026-09-29T12:00:00Z customer Avery Sample (public):
Good to hear. Will we get anything for the lost appointments? That's two cancelled cleanings, invoice INV-20931 covers this month.

[21] 2026-09-29T13:00:00Z agent Casey Escalante (public):
I've passed your credit question to our billing lead; I can't confirm an amount myself.

[22] 2026-09-30T08:40:00Z customer Avery Sample (public):
Thanks. Please keep me posted.

[23] 2026-09-30T10:00:00Z agent Casey Escalante (public):
Engineering has the ENG-4471 fix scheduled for the 2026-10-06 release. I'll update you by Tuesday 2026-10-06 at the latest, sooner if it ships early.

[24] 2026-09-30T10:05:00Z agent Casey Escalante (INTERNAL NOTE):
Internal: billing lead (Morgan) to decide on credit for INV-20931; do not promise an amount.

[25] 2026-10-01T16:30:00Z customer Avery Sample (public):
Thanks Casey. Two questions: can you confirm the fix will also clean up the existing duplicates, and has billing decided on the credit for INV-20931?

## Identifiers present in this ticket (quote only these)
- reference IDs: BK-55102, BK-55117, ENG-4471, INV-20931
- amounts: none
- dates written in messages: 2026-10-06
