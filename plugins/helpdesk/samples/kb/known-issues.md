---
id: known-issues
title: Known issues (status page mirror)
---
# Known issues

## KI-2026-10-02-sms
- Status: investigating (since 2026-10-02 06:00 UTC)
- Summary: SMS reminders delayed or not sent for some carriers. Reminders are queued and will send when the carrier recovers.
- Category: outage
- Match keywords: sms, text reminder, text reminders, reminder service down
- Customer guidance: point to status.quillfern.example.com and kb-105; do not promise a fix time.
- Owner: Tier 2 (incident commander Casey Escalante)

## KI-2026-09-ENG-4471
- Status: fix scheduled for the 2026-10-06 release
- Summary: Google Calendar sync can push the same booking twice, creating duplicate events.
- Category: calendar-sync
- Match keywords: double booking, double bookings, duplicate events, booking shows twice
- Customer guidance: keep one-way sync on until the fix ships.
- Owner: Tier 2
