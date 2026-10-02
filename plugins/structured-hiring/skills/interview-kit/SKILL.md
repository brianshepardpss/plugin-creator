---
name: interview-kit
description: Use when the user is opening a role and needs a structured interview loop, or says "build an interview kit", "what should we ask a <role> candidate", "interview questions for", "make a scorecard", "design our interview loop", "rubric for this role", "who on the panel asks what". Turns intake notes or a job description into 4-6 competencies, behavioral and situational questions with probes, anchored 1-4 rubrics and a panel split, laid out to paste into Greenhouse or Ashby scorecards.
---

# Interview kit

## 0. Guardrails

Read `../fairness-lint/guardrails.md`. Kits must contain no questions about
age, family, pregnancy, national origin, citizenship (work authorization is
fine), religion, disability, arrests or salary history, and no personality,
"culture fit" or "energy" competencies.

## 1. Intake (ask only what is missing, in one message)

- Role, level, team, and what this person must deliver in the first 6-12 months.
- Must-have vs nice-to-have skills (only must-haves become competencies).
- Interview stages available and who is on the panel (names or roles).
- Anything the company already uses (scorecard template, values list).
If the user says "just draft it", assume a standard loop: hiring manager
screen, one skills screen, a 3-4 session onsite, and say so.

## 2. Draft the kit

- 4-6 competencies, each observable and job-related, with a one-sentence
  definition. Turn values into behaviours ("Ownership: drives outcomes beyond
  the assigned task"), never into "fit".
- Per competency: at least 2 behavioral questions ("Tell me about a time..."),
  at least 1 situational question (a realistic scenario from this job), and
  2-3 probes per question (what you did, what happened, what you'd change).
- Anchored rubric per competency, 1-4: 1 Strong No, 2 No, 3 Yes, 4 Strong
  Yes; each anchor describes observable evidence, not adjectives.
- Panel split: each competency has exactly one owning session; a second
  session may list it as `secondary` only if the user wants deliberate
  overlap for a critical competency. 1-3 competencies per session.
- Same questions for every candidate for the role. Note the time per question.

## 3. Check it

Write the kit as JSON (shape below) to `kit-<role-slug>.json` in the user's
folder (or a temp file if they only want it in chat), then run from this
skill's directory:

`python3 kit_check.py <kit.json> --require-questions`

Fix every FAIL and every WARN that is not a deliberate choice, and re-run
until there are 0 FAIL. Show the final check output.

```json
{"role": "", "req_id": "", "rating_scale": {"1": "Strong No", "2": "No", "3": "Yes", "4": "Strong Yes"},
 "competencies": [{"name": "", "definition": "", "anchors": {"1": "", "2": "", "3": "", "4": ""},
   "questions": [{"type": "behavioral", "text": "", "probes": ["", ""], "minutes": 10}]}],
 "sessions": [{"name": "", "stage": "", "interviewer": "", "competencies": [""], "secondary": []}]}
```

## 4. Present (literal template)

```
# Interview kit: <Role>

Loop: <session> (<minutes> min, <interviewer>) -> ... 

## Panel split
| Session | Interviewer | Owns | Secondary |

## <Competency> -- owned by <session>
Definition: ...
Rubric: 1 Strong No: ... | 2 No: ... | 3 Yes: ... | 4 Strong Yes: ...
Behavioral
1. <question> (<min> min)
   Probes: ...; ...
Situational
1. ...

## Paste into your ATS
Greenhouse: Job Setup > Interview Plan > <stage> > Edit Scorecard. Add each
competency as an attribute under the "Skills" (or "Qualifications") category,
not "Personality Traits". Put the questions in the Interview Kit for that
interview. Ashby: add each competency as a scored field in the interview's
feedback form, with the rubric as the field description.

## Interviewer reminders
- Ask every candidate the same questions; take notes on what they said and did.
- Submit the scorecard within 24 hours, before talking to other interviewers.
- Rate each competency against the anchors; leave it blank if not observed.
- Do not ask about age, family, origin, religion, health, arrests or pay history.

kit_check: <fail/warn summary>
AI-drafted, human decision required.
```

## 5. After

Offer: "When interviews are done, run /debrief-prep with this kit file so
missing coverage is detected."
