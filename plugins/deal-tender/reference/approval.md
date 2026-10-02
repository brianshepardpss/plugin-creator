# Writing to Pipedrive: the approval protocol

DealTender is read-only until the user approves a specific change list.
Follow every step, every time, including for one-field changes.

1. Build `changes.json` in the working folder:
   ```json
   {"changes": [
     {"deal_id": 101,
      "set": {"stage": "Proposal Made", "expected_close_date": "2026-10-30", "value": 48000},
      "add_note": "text of the note",
      "add_activity": {"type": "call", "subject": "Follow up on revised proposal", "due_date": "2026-10-09"}}
   ]}
   ```
   Dates come from `dealtender.py date` or from the user, never mental math.
2. Run `python3 <plugin>/scripts/dealtender.py diff <deals> --changes changes.json`.
   Fix every ERROR (unknown deal, stage not in that deal's pipeline,
   ambiguous stage) by asking the user, never by guessing or creating
   records.
3. Show the diff output and ask: "Apply these changes? (yes / yes to 1,3 /
   edit)". Stop and wait. Silence, "looks good, but..." or a new question is
   not a yes.
4. After an explicit yes, live mode: one `updateDeal` per deal (stage as
   `stage_id` from stages.json), one `addNote` per note, one `addActivity`
   per activity. Then `getDeal` once per changed deal and report the
   values Pipedrive now holds. If a call fails, stop and report what was
   and was not applied.
5. CSV mode (no connector): output the approved list as a "Paste into
   Pipedrive" checklist, one line per edit, with the deal ID and title.

Never, even if asked casually:
- create a deal, person or organization as a side effect of logging
  (`addDeal`, `addPerson`, `addOrganization`); if the user explicitly asks
  for one, show it as its own change and get its own yes;
- mark a deal won or lost, or change value or owner, unless the user said so
  in this conversation;
- send email (DealTender only drafts; the user sends);
- bulk-edit more than 10 deals in one approval; split into batches.
