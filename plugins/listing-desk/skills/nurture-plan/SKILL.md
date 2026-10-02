---
name: nurture-plan
description: Use when an agent wants to stay in touch with past clients and their sphere, or says "build my nurture plan", "12-month touch plan", "sphere of influence calendar", "stay in touch with past clients", "home anniversary reminders", or uploads a CRM or phone contact export CSV. Builds a 12-month touch calendar by tier (A/B/C) with home anniversaries, birthdays and monthly themes, respects email/text permissions, flags contacts to reconnect with first, and drafts one template per theme. Drafts only.
---

# 12-month sphere nurture plan

## 1. Inputs

- Contact CSV exported from the agent's CRM or phone (sample:
  `../../samples/sphere_contacts.csv`). Useful columns: Name, Email, Phone,
  Tier, Relationship, Home Purchase Date, Birthday Month, Last Contact,
  Email OK, Text OK. Missing Tier means C.
- Start month (default next month). Ask only if the agent mentions one.
- If the export has no tier column, offer to tier with the agent: A = past
  clients and top referrers, B = warm sphere, C = everyone else. Let the
  agent decide each person; do not tier by age, family or anything personal.

## 2. Build the calendar (script)

```
python3 <base>/nurture.py <contacts.csv> --start YYYY-MM \
  --out nurture/plan.md --csv-out nurture/calendar.csv
```

The rules (cadence per tier, themes, channels, date spreading) are in the
script's docstring; edit the script's TIERS/THEMES only if the agent asks.
Use the script's counts and dates exactly.

## 3. Draft the templates

Write `nurture/templates.md` with one short template per theme used in the
plan plus "home anniversary", "birthday" and "reconnect" templates:

- Email: subject under 60 characters, 40-100 words, `{first_name}`
  merge field, one soft ask, unsubscribe line.
- Text (only for contacts with Text OK = Y): under 250 characters, ends
  "Reply STOP to opt out."
- Call: 3 talking points, not a script.
- Market-update templates use placeholders like `{median_sale_price}` for
  the agent to fill from their own MLS stats. Do not invent market numbers.
- No tax, legal or lending advice ("homeowner records checklist", not "you
  can deduct...").
- Run the Fair Housing checker on the templates:
  `python3 <base>/../fair-housing-check/fair_housing.py nurture/templates.md`
  and fix every FLAG.

## 4. Reply

```
## Sphere nurture plan: <start> to <end>
Contacts <n> (A <n>, B <n>, C <n>); <touches> touches; busiest month <month> (<n>).

Reconnect first: <names and why, from the script>

| Month | Touches | Calls | Emails | Texts | Theme |
...

This month's to-do: <the first month's rows: date, contact, channel, touch>

Files: nurture/plan.md, nurture/calendar.csv (import into your CRM or
calendar), nurture/templates.md
```

## Guardrails

- Drafts only. Never send, import or upload to a CRM; the agent does that.
- Texts only to Text OK = Y contacts; email only to Email OK = Y contacts.
  Contacts with neither get "mail or in person".
- Do not echo contact details back in chat beyond names.
