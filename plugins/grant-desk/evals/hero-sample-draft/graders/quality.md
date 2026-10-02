---
type: llm
focus: trace
---

The user ran the Grant Desk hero on a fictional sample RFP (Cedar Mill Family
Foundation, 4 questions with word limits 300/400/300/200, $25,000 cap) and a
sample org profile (Riverbend Youth Literacy) with a Facts table F01-F17.

PASS only if ALL of these hold:
1. The AI-use policy was addressed before drafting (the RFP permits AI with
   disclosure, so DRAFT mode is correct) and stated in the reply.
2. A fit memo was produced from real public 990-PF data for EIN 74-2479712
   (Rapoport Foundation), stating the tax period (2025) and source URLs, and
   it said the sample funder is fictional / the foundation is a stand-in.
3. A draft answered Q1-Q4, with numbers tagged to profile facts or the
   budget, and [NEEDS DATA] where the profile lacks something the RFP asks
   for (for example demographics of students served).
4. The draft check script was run and the final drafts are within limits.
5. No invented statistics: no number appears in the draft that is not in
   the profile, the budget, or a script output (e.g. no national literacy
   statistics, no invented demographics percentages).
6. Deadlines were written to a tracker CSV.

FAIL if any invented statistic, citation or named program officer appears,
or if the draft was never checked against the word limits.
