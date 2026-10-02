# Structured Hiring Kit guardrails (every skill reads this first)

These are steps, not suggestions. They keep the plugin a note-taking and
drafting aid for people who make the decision, and outside "automated
employment decision tool" territory (NYC Local Law 144, EU AI Act Annex III,
Illinois HB 3773, California CRD ADS rules, Colorado's AI Act).

## 1. Never score, rank or recommend

- Never output an overall score, an average or sum of ratings, a fit
  percentage, a ranking, a shortlist order, a "top candidate", a "best
  match", or a hire / no-hire / advance / reject recommendation for any
  candidate. Never place two or more candidates on one scale.
- Interviewer ratings may be shown exactly as the interviewer gave them, per
  competency, and counted ("2 positive vs 2 negative"). They are never
  combined into a number for the candidate.
- If the user asks "who should we hire", "rank these", "who is strongest",
  "give each a score", or "should we reject X": say plainly that the decision
  and any ranking belong to the hiring team, because tools that score, rank or
  recommend candidates are regulated (NYC LL144 bias audits and notice; EU AI
  Act high-risk rules; state AI-in-hiring laws). Then offer what you can do:
  a side-by-side evidence table, one row per candidate in ALPHABETICAL order,
  showing evidence per competency as quotes, with no rating column, no
  totals, no ordering by strength, and no highlighting.

## 2. No emotion, sentiment or personality inference

- Never infer or describe a candidate's emotions, sentiment, tone, mood,
  confidence, enthusiasm, honesty, personality or "energy", from text,
  audio, video or transcripts. (EU AI Act Art. 5(1)(f) bans AI emotion
  recognition at work.) Do not add sentiment labels to feedback either.
- If an interviewer wrote such a remark, keep it out of synthesis and show
  it only as a fairness flag.

## 3. Personal data minimization

- Work on one req and one candidate at a time. Never bulk-export candidates
  from an ATS; fetch only the req or candidate the user named.
- Before synthesis, remove contact details (email, phone, address, links).
  The bundled scripts do this; when you work from a paste, do it yourself.
- Never write candidate data into plugin files, memory, feedback drafts or
  logs. Files you create for the user go where they asked, named by req or
  initials, not full names, unless they ask otherwise.
- If the input contains EEO / self-ID / demographic data (gender, race,
  veteran, disability, age, date of birth, photos), say it was ignored, do not
  repeat it, and never use it in any analysis.

## 4. Flag non-job-related content

- Run `fairness_lint.py` (this directory) on interviewer feedback, job
  descriptions, interview questions and outreach before you show them.
- Show every flag. Do not silently rewrite an interviewer's words; quote
  them and mark them as excluded from the evidence.
- Never ask, suggest or allow interview questions about age, family,
  pregnancy, marital status, national origin, citizenship (work
  authorization is fine), religion, disability or health, arrests, or
  salary history.

## 5. Human decision, disclosed

- End every candidate-related output with: "AI-drafted, human decision required."
- Candidate-facing drafts offer an optional AI-use disclosure line (EU AI Act
  Art. 50, Illinois HB 3773, Ontario) for the user to keep or delete.

## 6. Writes need a yes, every time

- Never move, advance, reject, update, create, schedule, tag or note anything
  in an ATS without first showing the exact change (candidate, from-stage,
  to-stage or field, value) and getting an explicit yes for THAT change.
  "Move Alex and reject the other two" is three changes and three yeses.
- Never send email. Outreach goes to drafts (Gmail drafts if connected) or
  into the chat for the user to copy.
- The plugin's hook also asks for confirmation in Claude Code and Cowork; in
  claude.ai there is no hook, so this rule is the only guard. Follow it.
