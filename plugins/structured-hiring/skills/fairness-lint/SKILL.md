---
name: fairness-lint
description: Use when the user wants interview feedback, a job posting, interview questions or a recruiting email checked for bias or legal risk, or says "is this feedback okay", "check this JD for biased language", "is this interview question legal", "can I ask this in an interview", "scan our scorecards for culture fit comments", "inclusive language check". Flags protected-class proxies, non-job-related remarks and unlawful questions with line, reason and a suggested fix.
---

# Fairness lint

1. Read `guardrails.md` in this directory.
2. Get the text: a file path, a paste, or the output of another skill.
   Remove emails, phone numbers and addresses before going further.
3. Pick the mode:
   - `feedback` for scorecards, debrief notes, interviewer comments
   - `jd` for job descriptions and postings
   - `questions` for interview questions or scripts
   - `outreach` for candidate emails and messages
4. Save the text to a temporary file (or pipe it) and run:
   `python3 fairness_lint.py <file> --mode <mode>`
   from this skill's directory. Never skip the script and lint by eye only.
5. Show the script's table as is. Then add, in this order:
   - Anything the patterns cannot catch that you notice: coded proxies
     ("polish", "presence", "not a fit for the team", gendered pronouns for
     the ideal hire, assumptions about commute or schedule). Label these
     "reviewer notes", separate from the script's flags.
   - For `jd` and `questions` mode: a corrected version with every flagged
     phrase rewritten to the job-related requirement.
   - For `feedback` mode: do NOT rewrite the interviewer's words. List the
     flagged remarks as "exclude from the decision" and suggest the
     job-related question the interviewer should answer instead.
6. Close with: "Flags mean a human should look, not that anyone is biased.
   AI-drafted, human decision required."

Never: label a person as biased; infer anyone's emotions or intent; use
demographic data; or say text is "compliant" or "legal". Say "no flags
found" and that counsel owns legal sign-off.
