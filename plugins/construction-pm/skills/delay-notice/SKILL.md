---
name: delay-notice
description: Use when the user describes an owner or architect caused delay, a differing or concealed site condition, a stop-work, an acceleration request or other impact and asks what they owe or how to protect themselves, or says "what notice do I have to give", "how many days do I have to submit a claim", "the owner delayed us, what now", "write a delay notice letter", or "do we have to notify them". Explains why notice timing must come from their own contract, finds notice clauses in contract text they supply, and drafts a neutral notice letter for their review.
---

# Possible notice event: find the clause, draft the letter, never decide

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

This skill does not interpret contracts or give legal advice. It never
states that the user is entitled to time or money, and never states a
notice deadline as fact. Missing a notice period can forfeit a claim, so
the job is to get the user to their own contract and their PM or counsel
fast, with a clean draft in hand.

## Steps

1. Say this first, in plain words:
   - Notice requirements (who, how, by when, what to include) come from
     their contract and any subcontract or flow-down, not from a general
     rule. Periods can be short; for example one widely used general
     conditions form (AIA A201-2017) uses 21 days for claims, and
     subcontracts are often shorter. Theirs may differ.
   - Read the notice and claims articles of their contract today, and talk
     to their PM, owner or counsel before relying on any date.
2. Collect the facts (ask only for what is missing): what happened, when it
   was first noticed, who was told and how, which work is affected, what is
   still unknown (cost, days). Pull them from the daily report, RFIs or
   minutes if the user has them. If the user has notes in a file, run
   `python3 <skill dir>/../daily-report/scripts/notice_flags.py <file>` to catch other
   events in the same notes.
3. If the user provides contract text (pasted or a file), find the
   provisions on notice, claims, changes, differing site conditions, delay
   and time extensions. Quote each one verbatim with its article number in
   a table: | Article | Quoted text | What it asks for (who/how/when, in the
   contract's own words) |. Do not paraphrase into a rule, do not compute a
   due date from it, and do not say whether it applies. End with: "Have
   your PM or counsel confirm which of these applies and the deadline."
   If no contract text is supplied, say you cannot tell them their
   deadline and offer to search it once they paste the relevant articles.
4. Draft a neutral notice letter with this template and show it. Do not
   send anything.

```
<Company letterhead>
<Date>
VIA <method required by the contract - check: email / certified mail / portal>

To: <Owner / Architect / GC, name and address per the contract notice clause>
Project: <name, contract no.>
Subject: Notice of <delay / differing site condition / directed change /
         other event> - <short description>

On <date/time>, <what happened, facts only, with location>. <Who was
notified, how and when.>

The event has affected or may affect <work/activities>. The Contractor is
evaluating the impact on the Contract Sum and Contract Time and will
provide supporting information when available.

This letter is provided as notice under <article no. - insert from your
contract> of the Contract. [Confirm the article, recipient, delivery
method and timing with your PM or counsel before sending.]

<Request, if any: e.g. direction on how to proceed by <date>.>

[RESERVATION OF RIGHTS - insert your company's approved language.]

Sincerely,
<Name, title>
cc: <per contract>
Attachments: <daily reports, photos, RFI>
```

5. Close with a short checklist: read the notice article today; confirm
   recipient and delivery method; keep daily reports and photos of the
   event and its effects; track crew hours on affected work separately.

## Never

- "You have N days" or any date computed from a notice clause.
- "You are entitled to", "the owner owes", "this is a compensable delay".
- Advice on whether to sue, stop work or withhold work.
