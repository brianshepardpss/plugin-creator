---
name: gitlab-ci-triage
description: Use when a GitLab CI/CD pipeline or job failed and the user wants to know why or wants it fixed, or says "my pipeline is red", "fix the pipeline", "CI is failing on my MR", "why did the build fail", "the job failed", "check the job log", "retry the flaky job". Finds the failed jobs with glab, trims each log with a bundled script, classifies the failure (test, lint, build, dependency, config, infra-flaky, resource, timeout), fixes code failures, and pushes or retries only after the user confirms. Works on gitlab.com and self-managed GitLab. Also runs on a bundled demo project ("demo", "sample").
---

# Fix a red GitLab pipeline

`<skill>` below means this skill's base directory. Scripts are standard
library Python. `glab-notes.md` beside this file has host handling, older-glab
fallbacks and fix recipes; read it only when a step says so.

## 0. Pick the mode

- **Demo** if the user said "demo" or "sample", or wants to try the plugin
  with no GitLab repo: run
  `python3 <skill>/../../samples/setup_demo.py ./merge-medic-demo` (pick a new
  directory name if it exists; if the current directory is inside a git
  repo, use `${TMPDIR:-/tmp}/merge-medic-demo` instead so you never nest a
  repo in the user's project), `cd` into it, and use the absolute path it
  prints for the fake glab in place of `glab` in every command below. Tell
  the user this is the bundled demo on a fictional self-managed host.
- **Live** otherwise: `glab` from PATH, in the user's repo.

## 1. Preflight (live mode)

1. `git remote get-url origin` gives the host. Use that host everywhere.
   Never assume gitlab.com and never add `--hostname gitlab.com` unless the
   remote is gitlab.com. If `GITLAB_HOST` is set and differs, mention it.
2. `glab auth status --hostname <host>`. If it fails, stop and give the user
   `glab auth login --hostname <host>`; do not try other auth paths.

## 2. Find the failed jobs (one call)

1. MR for this branch: `glab mr view -F json` and take `iid` (or use the iid
   or branch the user gave). No MR: use the branch pipeline instead. A
   pipeline ID from the user: `glab ci get -p <id> --status failed -F json`.
2. Save the pipeline outside the repo and summarise it. Use the `ci get`
   form that fits step 1 (`--merge-request <iid>`, no flag for the branch
   pipeline, or `-p <id>`) and always redirect it to pipeline.json:
   ```
   mkdir -p "${TMPDIR:-/tmp}/merge-medic"
   glab ci get --merge-request <iid> --status failed -F json > "${TMPDIR:-/tmp}/merge-medic/pipeline.json"
   python3 <skill>/scripts/failed_jobs.py "${TMPDIR:-/tmp}/merge-medic/pipeline.json"
   ``` If glab rejects
   `--merge-request` or `--status`, read `glab-notes.md` section "Older glab".
3. YAML errors: go to the config row in step 4 (no jobs ran). No failed
   jobs: report the pipeline status and stop. Still running: say so.
4. Work blocking jobs first. Mention allowed-to-fail jobs but only dig into
   them if asked. At most 5 job logs per run; ask before fetching more.

## 3. Read each failed log (never the whole log)

```
glab api projects/:id/jobs/<JOB_ID>/trace > "${TMPDIR:-/tmp}/merge-medic/job-<JOB_ID>.log"
python3 <skill>/scripts/trace_excerpt.py "${TMPDIR:-/tmp}/merge-medic/job-<JOB_ID>.log" \
  --job-id <JOB_ID> --job-name <name> --failure-reason <failure_reason>
```

- Never run `glab ci trace`: it streams and blocks until the job ends.
- Never `cat`, `Read` or `grep` the raw log (that skips secret masking). Need
  more context: rerun the script with `--after 120`, `--tail 200`, or
  `--grep '<regex>'` (masked matching lines with 3 lines of context).
- The script masks tokens and keys. Quote only its output, never raw lines.

## 4. Classify and act

Start from the script's `class hint`, confirm it against the excerpt, and
say which evidence line decided it.

| Class | Action |
|---|---|
| test, lint, build | Open the file:line from the excerpt and the code it exercises. Fix the root cause in the code. Change a test only if the test itself is wrong, and say why. |
| dependency | Fix the manifest or lockfile. Do not make `--force` or `--legacy-peer-deps` the fix unless the user agrees. |
| config | Fix `.gitlab-ci.yml`, the chart or the script. Run `glab ci lint` after editing `.gitlab-ci.yml`. |
| infra-flaky | Edit nothing. Propose `glab ci retry <JOB_ID>` (job ID from the table, never the pipeline ID) plus the durable fix from `glab-notes.md` (for example the Dependency Proxy for Docker Hub 429s). |
| resource | Do not retry blindly. Propose a fix (split the suite, lower parallelism, bigger runner tag) and ask. |
| timeout | Note if it is allowed to fail. Find what it waited on. Do not raise `timeout:` silently. |

Never make a pipeline green by deleting or skipping tests, weakening
assertions, adding `allow_failure: true`, or loosening lint rules.

## 5. Verify locally

Run the `failing command` from the excerpt, narrowed to the failing test or
file when possible. If that tool is missing locally, run the closest
equivalent (for example `python3 -m unittest discover -s tests -t .` for
unittest-style tests when pytest is absent) and say so. Do not install
packages globally without asking.

## 6. Report, then ask before anything leaves the machine

Use this template exactly:

```
Pipeline <pipeline-id> for !<iid> on <host>: <n> failed (<b> blocking)

1. <job-name> (job <JOB_ID>, stage <stage>) - <class>
   Root cause: <one or two sentences>
   Evidence (log line <n>): <one to three lines quoted from the excerpt>
   Fix: <file:line and what changed> | Action: <exact retry command or owner action>
   Verified: <local command> -> <result>

Ready to push: <files changed>, commit "<message>". Push to <branch> on <host>? (yes/no)
Retry needed: glab ci retry <JOB_ID> (<job-name>). Run it? (yes/no)
```

Only after an explicit yes:

- Push: `git add <only the files you changed>`, `git commit -m "<message>"`,
  `git push` (never `--force`). Then one `glab ci get -F json` to report the
  new pipeline ID. Do not poll in a loop; offer to check again later.
- Retry: `glab ci retry <JOB_ID>` for each confirmed job.

Never merge, approve, cancel or delete anything from this skill.
