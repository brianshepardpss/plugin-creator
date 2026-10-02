---
name: ats-update
description: Use when the user asks to change anything in their applicant tracking system, or says "move <candidate> to onsite", "advance her to the next stage", "reject the other two", "archive these candidates", "update their status", "add a note in Greenhouse", "update the stage in Ashby", "schedule the interview in the ATS". Shows each change and gets a separate yes before every write; rejection emails become drafts only.
---

# ATS update (confirmed writes only)

## 0. Guardrails

Read `../fairness-lint/guardrails.md`, section 6 especially. You are the
user's hands, not the decider: never suggest who to advance or reject, and
never act on "the weakest ones", "whoever scored lowest" or similar
selections; ask the user to name each candidate.

If the user says "reject" or "decline" and it is unclear whether they want
an ATS status change, an email, or both, ask before planning.

## 1. Resolve, read-only

1. Check which ATS MCP is connected (Greenhouse or Ashby; tools whose names
   contain greenhouse or ashby). If none: say so, and give the user the
   exact steps to do it by hand in their ATS. Do not try anything else.
2. For each named candidate, look up the application on the named job with
   read-only tools only (search/get/list). If a name matches more than one
   person or job, ask which one.
3. Find the target stage or rejection reason the ATS offers. Do not invent
   one; list the options if the user's wording does not match exactly.

## 2. Confirm each change separately

Show a numbered plan, one change per line:

```
Planned ATS changes (nothing has been changed yet)
1. Alex R. -- Senior Backend Engineer: Technical Screen -> Onsite
2. Sam K.  -- Senior Backend Engineer: reject, reason "<ATS reason>", no email from the ATS
3. Taylor W. -- Senior Backend Engineer: reject, reason "<ATS reason>", no email from the ATS
Rejection emails: drafted separately for your review; nothing will be sent.
```

Then ask about change 1 only: "Make change 1? (yes / no)". Wait for an
explicit yes. Execute it, report the result, then ask about change 2, and so
on. A "yes to all" still means one confirmation per write tool call: in
Claude Code and Cowork the plugin's hook will also ask before each call;
do not try to avoid it. Never set an ATS option that emails the candidate;
if the tool sends email by default and cannot be turned off, say so and ask.

## 3. Candidate emails

For rejections or stage-change notices, use the outreach-drafts skill to
write one draft per candidate (Gmail drafts if connected). Never send.

## 4. Report

List what changed, what was skipped, and any errors. Tell the user that each
write was logged (tool name, time, ids only; no names or notes) in the
plugin's data folder as `ats-actions.log` when hooks are active (Claude Code
and Cowork). End with: "Drafts only; nothing was sent. AI-drafted, human decision required."
