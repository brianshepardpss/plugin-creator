---
name: thread-summary
description: Use when someone needs to catch up on a long support ticket, or says "summarize ticket 1030", "TL;DR this thread", "handoff note", "what's going on with this customer", or "catch me up before I take this ticket". Produces a handoff summary of 150 words or fewer: the current ask, what was tried, sentiment trend, open commitments with dates, and the next step.
---

# Summarize a ticket thread for handoff

Script: `../ticket-schema/scripts/helpdesk.py` (SCRIPT).

## Procedure

1. Get the redacted thread with numbered messages:
   ```
   python3 SCRIPT ticket <input> <id>
   ```
   (`sample` for the bundled data. If the user pasted a thread, pipe it
   through `python3 SCRIPT redact` first.) If the output says the export
   has no reply thread (Freshdesk CSV), say the summary covers the first
   message only and suggest a JSON export or the connector.
2. Read every message, including internal notes (mark facts that come only
   from internal notes as "(internal)").
3. Write the summary in exactly this shape, 150 words or fewer in total
   (count them; trim if over):

   ```
   **Ticket <id> - handoff summary** (<n> messages, <first date> to <last date>)
   - Current ask: <what the customer wants now, from the latest customer message>
   - Tried so far: <steps already taken, in order, comma-separated>
   - Sentiment: <start> -> <now>, one reason
   - Open commitments: <who promised what, by when (exact date as written)>, or "none"
   - Next step: <one concrete action and owner>
   ```
4. Accuracy checks before showing it:
   - Every ID, amount and date you mention appears in the script's
     "Identifiers present" list or the message timestamps. Do not invent
     order or invoice numbers.
   - Commitments are only things an agent actually said they would do, with
     the date exactly as stated. Do not convert "Tuesday" into a date
     yourself; quote what is written.
   - Do not include emails, phone numbers, card details or health details.
5. Offer: "Want a reply drafted for the open questions?" (reply-draft skill).
