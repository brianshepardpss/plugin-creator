# Normalized scorecard JSON (read when converting a paste, MCP results or an unknown CSV)

```json
{
  "req_id": "REQ-1042",
  "role": "Senior Backend Engineer",
  "interviews": [
    {
      "candidate": "Priya N.",
      "session": "System design",
      "interviewer": "Ana Q.",
      "date": "2026-09-28",
      "submitted_at": "2026-09-28",
      "ratings": {"System Design": 3, "Communication": 3},
      "evidence": {"System Design": "quote or close paraphrase of what they observed"},
      "notes": "anything not tied to a competency"
    }
  ]
}
```

Rules:

- One object per interviewer per session. A scheduled interviewer with no
  feedback yet: `"submitted_at": null`, empty `ratings` and `evidence`.
- `ratings` values: 1-4 (1 Strong No, 2 No, 3 Yes, 4 Strong Yes) or a label
  ("Strong No", "No", "Mixed", "Yes", "Strong Yes", "definitely_not",
  "strong_yes"). Map 5-point scales to labels, never to new numbers.
  Leave out a rating the interviewer did not give. Never derive a rating
  from the tone of the text.
- Interviewers' overall recommendations: leave them out.
- `evidence`: the interviewer's own words, trimmed. Remove emails, phones,
  addresses and links. Keep flagged remarks verbatim; the lint must see them.
- Dates are YYYY-MM-DD. If a date is unknown, leave it as "".
- Never include EEO/demographic fields, resumes or contact details.

Header mapping for CSVs the script does not recognise:

| Normalized | Common headers |
|---|---|
| candidate | Candidate, Candidate Name, Applicant |
| session | Interview, Interview Name, Stage, Step |
| interviewer | Interviewer, Submitted By, Author |
| date | Interview Date, Interviewed At, Scheduled |
| submitted_at | Submitted At, Feedback Submitted, Completed At |
| ratings{comp} | "<comp> - Score", "<comp> Rating", attribute columns |
| evidence{comp} | "<comp> - Notes", "<comp> Comments", question answers |
