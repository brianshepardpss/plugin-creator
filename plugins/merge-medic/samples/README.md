# Merge Medic samples

Everything here is fictional: the company, host, people, tokens and keys are
made up so the plugin can be tried, tested and evaluated with no GitLab
account and no network.

## Demo project (used by `/gl-fix-pipeline demo` and the evals)

```
python3 samples/setup_demo.py ./merge-medic-demo            # MR !42 branch, red pipeline
python3 samples/setup_demo.py ./mm-create --branch fix/csv-export-encoding   # branch with no MR yet
```

This creates a git repo for `invoice-api`, a small Python billing service,
whose `origin` is `https://gitlab.example-corp.test/platform/invoice-api.git`
(a fictional self-managed GitLab). Pushes go to a local bare repo inside
`.git/merge-medic-fake/remote.git`, so `git push` works offline.

## Fake glab

`samples/bin/glab` replays recorded GitLab responses for that project. Call
it by absolute path in place of `glab`. It enforces the real flag rules
(for example `--draft` cannot be combined with `--unique`, inline comments
must target a line inside a diff hunk, `mr note publish` needs `--yes`
when not interactive, `ci retry` takes a job ID, not a pipeline ID) and
refuses `glab ci trace`, which streams and blocks in real glab. Writes are
recorded in `<repo>/.git/merge-medic-fake/state.json`; every call is logged
to `calls.log` beside it. Nothing is sent anywhere.

## Recorded data (`gitlab/`)

| File | What it is |
|---|---|
| `pipeline-1873.json` | MR !42 head pipeline, 7 jobs: unit-tests failed (pytest), build-image failed (Docker Hub 429), e2e-smoke failed but allowed to fail (timeout), deploy-review manual |
| `pipeline-1866.json` | Branch `chore/frontend-deps`: eslint errors, npm ERESOLVE, integration tests OOM-killed (exit 137), helm YAML error |
| `pipeline-1859.json` | Pipeline with `.gitlab-ci.yml` errors and no jobs |
| `traces/<job-id>-<name>.log` | Raw job logs with ANSI codes, section markers, runner timestamps, polling spam and a few fake leaked tokens to test masking |
| `mr-42.json`, `mr-42.diff`, `mr-42-discussions.json` | The MR, its diff and its review threads (3 unresolved, 1 resolved, 1 system note) |
| `project.json` | The project |

## Expected outputs (`expected/`)

Outputs of the bundled scripts on this data, kept so changes to the scripts
can be diffed:

```
python3 skills/gitlab-ci-triage/scripts/failed_jobs.py samples/gitlab/pipeline-1873.json
python3 skills/gitlab-ci-triage/scripts/trace_excerpt.py samples/gitlab/traces/90413-unit-tests.log \
  --job-id 90413 --job-name unit-tests --failure-reason script_failure
python3 skills/gitlab-mr-review/scripts/diff_lines.py samples/gitlab/mr-42.diff
python3 skills/gitlab-mr-threads/scripts/threads.py samples/gitlab/mr-42-discussions.json
```

The demo bug: `invoice_api/late_fees.py` uses `max(...)` where the fee cap
needs `min(...)`, so `test_fee_accrues_daily` and `test_fee_is_capped` fail.
