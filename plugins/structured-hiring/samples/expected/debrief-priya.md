# Debrief packet: Priya N. -- Senior Backend Engineer (REQ-1042)

As of 2026-10-01. AI-drafted, human decision required. This packet organizes interviewer evidence. It does not score, rank or recommend, and interviewers' overall votes are left out so the discussion starts from evidence.

> Privacy: 2 email/phone/link value(s) were removed from interviewer text.

## 1. Scorecard status

- Submitted: 6 of 7 interviews.
- MISSING: Gabe T. (Debugging & operations, interviewed 2026-09-28) -- 3 day(s) since the interview.
- Late: Chen H. (Technical screen) submitted 2 days after the interview; memory-based notes are less reliable.

## 2. Evidence matrix (competency x interviewer)

| Competency | Interviewer (session) | Rating | Evidence |
|---|---|---|---|
| System Design | Ana Q. (System design) | Yes | "Designed the fleet telemetry ingest for 40k robots: partitioned by robot id, put a durable queue in front of the writer, and named back-pressure and replay as the two failure modes to handle. Picked at-least-once delivery and explained the idempotency key." |
| System Design | Ben O. (System design) | No | "Did not estimate write throughput until I asked; when asked, 40k robots x 10 msgs/s was computed as 40k msgs/s and not corrected. Storage retention was never discussed." |
| System Design | Dev M. (Architecture deep dive) | Strong Yes | "Walked through the billing queue migration in detail: dual writes, a shadow reader, and a rollback switch; quantified the lag budget at 2 seconds." |
| System Design | Farah S. (Architecture deep dive) | No | "The migration story was strong but when I changed the constraint to multi-region she kept a single primary and could not say how a region failover would work." |
| Code Quality & Testing | Chen H. (Technical screen) | Strong Yes | "Solid coder, would be great." |
| Debugging & Operations | -- | -- | NO EVIDENCE |
| Communication | Ana Q. (System design) | Yes | "Drew the design in stages and paused to check that I followed before going deeper; restated my constraint about cost before answering." |
| Communication | Ben O. (System design) | Yes | "Clear structure, explained the queue choice well." |
| Ownership | Elena V. (Hiring manager screen) | Yes | "Described leading the move of the billing queue off a single Postgres table after two incidents; she wrote the RFC, ran the cutover and owned the on-call runbook afterwards." |
| Ownership | Dev M. (Architecture deep dive) | Yes | "Owned the post-incident review and the follow-up work for the billing outage." |
| Ownership | Farah S. (Architecture deep dive) | Yes | "Clear example of owning the billing runbook after the incident." |
| Collaboration | Elena V. (Hiring manager screen) | Yes | "Disagreed with a staff engineer on event schema versioning; set up a short spike to compare both options and adopted his approach when the data favored it." |

## 3. Where interviewers disagree

- **System Design**: 2 positive vs 2 negative.
  - Ana Q. (Yes): "Designed the fleet telemetry ingest for 40k robots: partitioned by robot id, put a durable queue in front of the writer, and named back-pressure and replay as the two failure modes to handle. Picked at-least-once delivery and explained the idempotency key."
  - Dev M. (Strong Yes): "Walked through the billing queue migration in detail: dual writes, a shadow reader, and a rollback switch; quantified the lag budget at 2 seconds."
  - Ben O. (No): "Did not estimate write throughput until I asked; when asked, 40k robots x 10 msgs/s was computed as 40k msgs/s and not corrected. Storage retention was never discussed."
  - Farah S. (No): "The migration story was strong but when I changed the constraint to multi-region she kept a single primary and could not say how a region failover would work."

## 4. Coverage gaps

- **Debugging & Operations**: no evidence. Gabe T. (Debugging & operations) has not submitted.
- Code Quality & Testing: evidence from one interviewer only (Chen H.).
- Collaboration: evidence from one interviewer only (Elena V.).

## 5. Ratings without supporting evidence

- STRONG RATING, THIN EVIDENCE: Chen H. rated Code Quality & Testing "Strong Yes" with 5 word(s) of evidence: "Solid coder, would be great."
- thin evidence: Ben O. rated Communication "Yes" with 7 word(s) of evidence: "Clear structure, explained the queue choice well."
- thin evidence: Farah S. rated Ownership "Yes" with 10 word(s) of evidence: "Clear example of owning the billing runbook after the incident."

## 6. Fairness flags (non-job-related remarks)

- [high] Dev M. (notes): "young" in "Great culture fit -- she brings the young energy this team needs. Email [email removed] if" -- age: Age-coded wording (ADEA protects 40+). Fix: Describe the job-related behaviour instead.
- [medium] Ben O. (notes): "Seemed nervous" in "Seemed nervous at the start, warmed up later." -- demeanor-emotion: Inference about emotion, demeanor or personality. These are unreliable signals, and AI systems may not infer emotions at work (EU AI Act Art. 5(1)(f)). Fix: Record what the candidate said or did against the rubric.
- [medium] Dev M. (notes): "culture fit" in "Great culture fit -- she brings the young energy this team needs. E" -- culture-fit: 'Culture fit' and gut-feel remarks are not job-related and are a common proxy for similarity bias. Fix: Replace with evidence against a named competency, or with 'values alignment' tied to a written value.

## 7. Questions for the debrief (seeds; edit before use)

1. System Design: Ana Q., Dev M. saw it positively and Ben O., Farah S. negatively. What did each of you observe, and which observation maps to which rubric anchor?
2. Debugging & Operations has no evidence. Do we wait for the missing scorecard, add a follow-up, or decide without it and record that?
3. Chen H.: what specific behaviour supports "Strong Yes" on Code Quality & Testing?
4. Set aside the flagged remarks (Ben O., Dev M.). Is the remaining job-related evidence enough?

## 8. Decision memo (the hiring team fills this in)

- Decision and decider: ______ (made by people, after discussion)
- Evidence relied on, by competency: ______
- Open risks and how they will be checked (references, follow-up interview): ______
- Flagged remarks excluded from the decision: ______
- Missing scorecards and how they were handled: ______

AI-drafted, human decision required.
