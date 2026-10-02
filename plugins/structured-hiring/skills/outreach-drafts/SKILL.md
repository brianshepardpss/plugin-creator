---
name: outreach-drafts
description: Use when the user needs a candidate-facing message drafted, or says "write a sourcing message", "reach out to this candidate", "follow up with candidates who went quiet", "write the rejection email", "draft rejection emails", "candidate update email", "interview invitation". Drafts sourcing, follow-up, scheduling, status and rejection messages as drafts only (Gmail drafts if connected); never sends.
---

# Outreach drafts

## 0. Guardrails

Read `../fairness-lint/guardrails.md`. Drafts only, never sent. Use only
what the user gave you about a candidate (name, role, a public detail they
pasted); do not look people up or scrape profiles. A rejection draft is NOT
an ATS rejection: changing the candidate's status is a separate, confirmed
action (guardrails section 6).

## 1. Identify the message type and inputs

If the user says "reject" or "decline" without saying whether they mean an
email, a status change in the ATS, or both, ask: "Email draft, ATS status
change, or both?" ATS changes go through the ats-update skill.

| Type | Needs |
|---|---|
| sourcing | role, 1-2 specific reasons this person's public work matches, pay range if known |
| follow-up | what the candidate last heard and when, the next step |
| scheduling | stage, length, interviewers' roles, options or a scheduling link |
| status update | where things stand and when they will hear next |
| rejection | stage reached, whether to invite future applications |

Ask once for anything missing; otherwise use clear `[placeholders]`.

## 2. Draft (rules)

- Under 120 words for sourcing and follow-ups; plain, specific, no hype.
- Sourcing: why them (their work, not their demographics or school
  prestige), what the role is, pay range when known, an easy no.
- Rejection: kind, brief, final. Thank them for their time. Give no reasons
  that reference ratings, other candidates or any personal characteristic;
  if the user wants to give feedback, offer one job-related, factual sentence
  for them to approve. Never mention "culture fit".
- Optional AI-use line, added at the end in brackets for the user to keep or
  delete: "[Optional: We use AI tools to help draft messages and organise
  interview notes; people make all hiring decisions.]"
- Several candidates: one separate draft each; never merge recipients.

## 3. Check, then deliver

1. Save the drafts to a temp file and run
   `python3 ../fairness-lint/fairness_lint.py <file> --mode outreach`. Fix
   every flag and re-run until clean.
2. Show each draft with a Subject line.
3. If Gmail is connected and the user wants it there, create one Gmail
   DRAFT per message (create_draft), never send, and list the drafts
   created. Otherwise leave them in chat to copy.
4. If the user also asked to change ATS status (e.g. "and reject them in
   Greenhouse"), stop and follow guardrails section 6: show each change and
   get a separate yes for each before calling any write tool.

Close with: "Drafts only; nothing was sent. AI-drafted, human decision required."
