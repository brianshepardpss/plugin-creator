# Pipeline CSV headers (read only if pipeline.py cannot find a column)

pipeline.py recognises these headers, case-insensitive:

| Needed | Recognised headers |
|---|---|
| candidate | Candidate, Candidate Name, Name, Applicant |
| stage | Current Stage, Stage, Status, current_stage, Pipeline Stage |
| stage entered date | Stage Entered, Entered Stage, stage_entered, Date Entered Stage, Last Stage Change, Moved To Stage At, Stage Changed At |

If the export uses other names, rename the header row in a temp copy (do not
edit the user's file) and run again. Where to find exports:

- Greenhouse: Reports > Pipeline / "Candidate Pipeline" report, or the job's
  candidates list > Export to Excel. Use "Date of last activity" only if no
  stage-entry date exists, and say the days are approximate.
- Ashby: Candidates > filter by job > export, or the Pipeline report.
- Lever: Opportunities > filter by posting > export CSV ("Stage", "Stage Changed At").

Closed stages excluded from stuck and median: Rejected, Withdrawn, Hired,
Archived, Declined, Offer Declined.
