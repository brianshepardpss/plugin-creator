---
name: reply-draft
description: Use when an agent wants a reply written for a support ticket, or says "draft a reply to ticket 1017", "answer this customer", "write a response using our macros", "how should I reply to this", or "reply to the angry customer". Writes an on-brand draft grounded in the team's KB articles, macros and voice.md, with every factual claim marked [KB] or [ASSUMED]. Output is internal-note text; nothing is sent.
---

# Draft a reply

Script: `../ticket-schema/scripts/helpdesk.py` (SCRIPT). Samples:
`../../samples/` (KB in `kb/`, voice in `voice.md`).

## Procedure

1. Load the ticket thread (redacted) and its facts:
   ```
   python3 SCRIPT ticket <input> <id> [--kb <dir>]
   ```
   Input/KB/voice selection is the same as in the queue-triage skill. If
   the user pasted the thread instead, pipe it through
   `python3 SCRIPT redact` first and work from that.
2. Read `voice.md` (theirs, else the sample) and follow it exactly:
   greeting, sign-off, tone, banned phrases, language rule.
3. Find grounding: read the KB articles and `macros.json` whose category
   matches the ticket's category, plus `known-issues.md`. Prefer an
   existing macro's wording, adapted. If nothing in the KB answers the
   question, say so and write a holding reply plus an internal question for
   the lead, instead of inventing an answer.
4. Policy windows and dates: if a policy depends on elapsed time (refund
   window, trial length), compute it with
   `python3 SCRIPT days <from YYYY-MM-DD> <to YYYY-MM-DD>` and show the
   result. Never do date math in your head.
5. Write the output in exactly this shape:

   ```
   **Draft - internal note, not sent** (ticket <id>, <category>, language <xx>)

   <reply text in the brand voice>

   ---
   Sources: <KB id + title, macro id> used
   Claims: <each factual claim in the reply> [KB kb-xxx] or [ASSUMED - check]
   Before sending: <anything the agent must verify or get approved>
   ```
6. Offer the next step: "Copy it into the ticket yourself, or, if your
   helpdesk connector is connected, I can add it as an internal note after
   you confirm." Follow "Posting an internal note" below only on an explicit
   yes.

## Rules that are never broken

- Never promise a refund, credit, discount, compensation amount or fix date
  unless a KB article states it applies to this case. Outside a policy
  window, say the request is being reviewed by the named owner (from the
  KB) and when they will answer, if the KB states it.
- Never ask for, repeat or include a full card number, CVV, password or
  SSN. If the customer posted one, add to "Before sending": "Customer
  posted a card number; redact it in the helpdesk and advise them not to
  send card details."
- Never close, solve, merge, change status or send a public reply, even if
  asked ("reply and close it"). Say plainly that this plugin only drafts,
  and the agent sends and closes in the helpdesk.
- Escalation flags (legal, security, vip): put "Escalate to <owner> before
  sending" at the top of "Before sending". For legal threats, keep the
  reply factual, do not admit fault or liability, and route to the lead.
- Quote only identifiers (order, invoice, bug IDs, amounts, dates) that the
  `ticket` output lists under "Identifiers present".

## Posting an internal note (optional, connector only)

1. Show the exact note text and the ticket id, and ask: "Post this as an
   internal (private) note on ticket <id>? yes/no".
2. Only after "yes": Zendesk, use the connector's comment tool with
   `public: false` (some community servers default to public, so always set
   it); Freshdesk, use the add-note tool with `private: true`.
3. Never use reply, delete or status tools, and never use an update tool
   for anything except this one private note (Zendesk adds notes through a
   ticket update that carries only the comment with `public: false`; send
   no other field). If the connector has no private-note path, stop and say so.
