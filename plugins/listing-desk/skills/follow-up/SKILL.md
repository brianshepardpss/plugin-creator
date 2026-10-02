---
name: follow-up
description: Use when an agent needs to follow up with leads, or says "follow up with my open house sign-ins", "write follow-up texts", "draft emails to these leads", "open house follow-up", "who should I call back", or uploads a sign-in sheet CSV or a photo of a paper sign-in sheet. Segments each person (unrepresented buyer by timeline, buyer with an agent, neighbor), schedules 3 touches with dates, and drafts the emails and texts the consent fields allow. Drafts only; never sends.
---

# Open house and lead follow-up

## 1. Get the list

- CSV from a sign-in app or CRM: use it as is. Sample:
  `../../samples/open_house_signins.csv`.
- Photo of a paper sheet: transcribe it into `follow-up/signins.csv` with the
  headers `Name,Email,Phone,Has Agent,Timeline,Consent To Text,Notes,Visit Date`.
  Leave a cell blank if unreadable; never guess an email or phone number.
  Consent To Text is `Y` only if the sheet shows the person checked it.

## 2. Plan the touches (script)

```
python3 <base>/followup.py <signins.csv> --property "<address>" \
  --out follow-up/plan.md --json-out follow-up/plan.json
```

The script removes blanks and duplicates, segments everyone, sets dates and
decides which channels are allowed. Use its plan exactly.

## 3. Draft each touch

For each person and touch in the plan, write one draft per allowed channel
into `follow-up/drafts.md`, grouped by person. Rules:

- **Text** only where the plan lists `text`. Under 300 characters, first
  name, agent first name, one question, and end with "Reply STOP to opt out."
- **Email**: subject under 60 characters, 50-120 words, one ask, signature
  placeholder `[Your name, brokerage, license #]`, and an unsubscribe line.
- **represented-buyer**: one short thank-you only. Do not ask for their
  business, offer a consultation or criticize their agent; offer to send
  details through their agent.
- **hot-buyer / warm-buyer / unknown** (unrepresented buyers): before any
  offer to tour, include one line that you will need a short written buyer
  agreement signed before touring homes together. Do not mention or draft
  compensation terms.
- **neighbor-or-looking**: offer a home value review; facts only about
  nearby sales (address-level facts from the agent's data, no judgments
  about the area).
- Personalize only from the Notes column. Do not invent details.
- Run the Fair Housing checker on the drafts before showing them:
  `python3 <base>/../fair-housing-check/fair_housing.py follow-up/drafts.md`
  and fix every FLAG.

## 4. Reply

```
## Follow-up plan: <property / event date>
<segment counts>; <skipped rows and why>

| Name | Segment | Channels | Touch dates |
...

Drafts (first touch for each person shown; all touches in follow-up/drafts.md):
**<Name>** (<segment>) -- <channel>
<draft>

Reminders: drafts only, review and send yourself; texts only to people who
consented; buyer agreement before touring.
```

## Guardrails

- Never send, schedule or upload messages or contacts; there is no send step.
- Text only with recorded consent. Every text has STOP opt-out language;
  every email has an unsubscribe line (CAN-SPAM).
- Do not repeat phone numbers or emails in the chat reply beyond what the
  agent needs; they are in the files.
