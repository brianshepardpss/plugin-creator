#!/usr/bin/env python3
"""Summarise a GitLab pipeline's failed jobs from `glab ci get -F json`.

Usage:
  glab ci get --merge-request <iid> --status failed -F json | python3 failed_jobs.py -
  glab api "projects/:id/pipelines/<id>/jobs?scope[]=failed" | python3 failed_jobs.py -
  python3 failed_jobs.py pipeline.json [--json]

Accepts either the pipeline object glab prints (with a "jobs" list) or a
bare list of job objects from the REST API. Standard library only.

Output, in this order:
  - pipeline id, status, ref, short sha, web URL, YAML errors (if any)
  - one row per failed job: JOB_ID, NAME, STAGE, FAILURE_REASON,
    BLOCKING (no if allow_failure is true), DURATION
  - blocking jobs first, then allowed-to-fail jobs; within each group,
    pipeline stage order as the jobs appear in the JSON
  - counts: failed, blocking, allowed to fail
The reminder line spells out the job IDs for `glab ci retry`, because
pipeline IDs and job IDs are different numbers and mixing them up is the
most common retry mistake.
"""
import argparse
import json
import sys

REASON_HINT = {
    "job_execution_timeout": "timeout",
    "stuck_or_timeout_failure": "infra-flaky",
    "runner_system_failure": "infra-flaky",
    "scheduler_failure": "infra-flaky",
    "api_failure": "infra-flaky",
    "data_integrity_failure": "infra-flaky",
    "runner_unsupported": "infra-flaky",
    "missing_dependency_failure": "dependency",
    "unmet_prerequisites": "config",
    "script_failure": "read the log",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", help="JSON file, or - for stdin")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    a = ap.parse_args()
    data = json.load(sys.stdin if a.file == "-" else open(a.file))

    pipe = data if isinstance(data, dict) else {}
    jobs = data.get("jobs") or [] if isinstance(data, dict) else data
    failed = [j for j in jobs if j.get("status") == "failed"]
    order = {j["id"]: n for n, j in enumerate(jobs)}
    failed.sort(key=lambda j: (bool(j.get("allow_failure")), order[j["id"]]))
    blocking = [j for j in failed if not j.get("allow_failure")]
    allowed = [j for j in failed if j.get("allow_failure")]
    running = [j for j in jobs if j.get("status") in ("running", "pending", "created")]

    rows = [{
        "job_id": j["id"], "name": j.get("name"), "stage": j.get("stage"),
        "failure_reason": j.get("failure_reason") or "-",
        "reason_hint": REASON_HINT.get(j.get("failure_reason"), "read the log"),
        "blocking": not j.get("allow_failure"),
        "duration_s": round(j["duration"], 1) if j.get("duration") is not None else None,
        "web_url": j.get("web_url"),
    } for j in failed]
    summary = {
        "pipeline_id": pipe.get("id") or (jobs[0]["pipeline"]["id"] if jobs and jobs[0].get("pipeline") else None),
        "status": pipe.get("status"), "ref": pipe.get("ref"),
        "sha": (pipe.get("sha") or "")[:8] or None, "web_url": pipe.get("web_url"),
        "yaml_errors": pipe.get("yaml_errors"),
        "failed": len(failed), "blocking": len(blocking), "allowed_to_fail": len(allowed),
        "still_running": len(running), "jobs": rows,
    }
    if a.json:
        print(json.dumps(summary, indent=2))
        return

    print(f"pipeline {summary['pipeline_id']} ({summary['status'] or '?'}) ref {summary['ref'] or '?'} "
          f"sha {summary['sha'] or '?'}")
    if summary["web_url"]:
        print(f"url: {summary['web_url']}")
    if summary["yaml_errors"]:
        print(f"YAML ERRORS: {summary['yaml_errors']}")
        print("No jobs ran. Fix .gitlab-ci.yml and validate with `glab ci lint` before pushing.")
        return
    if summary["still_running"]:
        print(f"note: {summary['still_running']} job(s) still running or pending; results may change.")
    if not failed:
        print("No failed jobs." + (" Pipeline status is " + summary["status"] + "." if summary["status"] else ""))
        return
    print(f"failed jobs: {len(failed)} ({len(blocking)} blocking, {len(allowed)} allowed to fail)")
    w = max(len(r["name"] or "") for r in rows)
    print(f"{'JOB_ID':<9}{'NAME':<{w + 2}}{'STAGE':<9}{'FAILURE_REASON':<24}{'BLOCKING':<10}{'DURATION':<10}HINT")
    for r in rows:
        dur = f"{r['duration_s']}s" if r["duration_s"] is not None else "-"
        print(f"{r['job_id']:<9}{r['name']:<{w + 2}}{r['stage']:<9}{r['failure_reason']:<24}"
              f"{'yes' if r['blocking'] else 'no':<10}{dur:<10}{r['reason_hint']}")
    ids = " ".join(str(r["job_id"]) for r in rows)
    print(f"retry uses JOB IDs ({ids}), never the pipeline ID ({summary['pipeline_id']}).")


if __name__ == "__main__":
    main()
