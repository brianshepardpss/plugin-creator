#!/usr/bin/env python3
"""Cut a GitLab CI job log down to the part that explains the failure.

Usage:
  glab api projects/:id/jobs/<job-id>/trace | python3 trace_excerpt.py - --job-id <id> --job-name <name>
  python3 trace_excerpt.py job.log [--failure-reason R] [--tail 80] [--after 40] [--json]

What it does, in order (standard library only, nothing leaves your machine):
  1. Cleans the raw trace: drops runner timestamps (FF_TIMESTAMPS prefixes),
     section_start/section_end markers, ANSI colour codes and carriage-return
     progress-bar overwrites. Line numbers in the output refer to the raw log.
  2. Masks secrets before anything is printed: GitLab tokens (glpat-, glrt-,
     gldt-, glcbt- ...), AWS key IDs and secrets, Authorization/PRIVATE-TOKEN
     headers, credentials in URLs, *PASSWORD/*SECRET/*TOKEN=... assignments,
     JWTs and private key blocks.
  3. Finds the first error block: the earliest line matching the most
     specific failure signature (see SIGNATURES), plus --before lines of
     context and up to --after lines following it (stops at the next
     `$ command` or section end).
  4. Adds the last --tail lines (default 80) not already shown.
  5. Collapses runs of 4+ near-identical lines (same text once digits are
     ignored) to first 2 + last 1 + a count, so polling loops and progress
     spam cost almost nothing.
  6. Prints a class hint (test, lint, build, dependency, config, infra-flaky,
     resource, timeout, unknown) from the matched signature, the job's
     failure_reason and the exit code. The hint is a starting point; the
     caller confirms it by reading the excerpt.
  7. With --grep REGEX, prints only masked lines matching REGEX (with 3
     lines of context) instead of the excerpt; use it to dig further
     without ever reading the raw log.
"""
import argparse
import json
import re
import sys

TS = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z [0-9a-f]{2}[OE]\+? ?")
SECTION = re.compile(r"section_(start|end):(\d+):([\w.\-]+)(?:\[[^\]]*\])?\r?(?:\x1b\[0K)?")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b[@-_]")
CMD = re.compile(r"^\$ (.+)")
EXIT = re.compile(r"ERROR: Job failed: exit code (\d+)")

MASKS = [
    (re.compile(r"\b(gl(?:pat|rt|rtr|dt|ptt|ft|imt|agent|soat|ffct|oas|cbt|wt))-[0-9A-Za-z_.\-]{8,}"), r"\1-[MASKED]"),
    (re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA|ANVA|AIPA)[0-9A-Z]{16}\b"), "[MASKED-AWS-KEY-ID]"),
    (re.compile(r"(?i)(aws_secret_access_key\s*[=:]\s*)\S+"), r"\1[MASKED]"),
    (re.compile(r"(?i)((?:authorization|proxy-authorization)\s*:\s*(?:bearer|basic|token)\s+)\S+"), r"\1[MASKED]"),
    (re.compile(r"(?i)((?:private|job|deploy)-token\s*:\s*)[^\s'\"]+"), r"\1[MASKED]"),
    (re.compile(r"(https?://)[^/\s:@]+:[^@\s/]+@"), r"\1[MASKED]@"),
    (re.compile(r"\b([A-Z0-9_]*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY|APIKEY|PRIVATE_KEY)[A-Z0-9_]*)=(?!\[MASKED)(\S+)"),
     r"\1=[MASKED]"),
    (re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                r"sk-an[t]-[A-Za-z0-9_-]{10,}|npm_[A-Za-z0-9]{30,}|pypi-[A-Za-z0-9_-]{30,}|"
                r"glsa_[A-Za-z0-9_]{20,}|AIza[0-9A-Za-z_-]{30,})"), "[MASKED-TOKEN]"),
    (re.compile(r"(?i)(_authToken\s*=\s*)\S+"), r"\1[MASKED]"),
    (re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}"), "[MASKED-JWT]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*"), "[MASKED-PRIVATE-KEY]"),
]

# (category, label, regex). Earlier entries win when several match.
SIGNATURES = [
    ("infra-flaky", "registry pull rate limit (HTTP 429)", r"toomanyrequests|429 Too Many Requests|pull rate limit"),
    ("infra-flaky", "runner system failure", r"ERROR: Job failed \(system failure\)|runner system failure|"
                                             r"ERROR: Preparation failed"),
    ("resource", "disk full", r"[Nn]o space left on device"),
    ("resource", "out of memory (process killed)", r"(?:^|\s)Killed\s+.*|OOMKilled|JavaScript heap out of memory|"
                                                   r"\bMemoryError\b|Cannot allocate memory|exit code 137\b"),
    ("timeout", "job timeout", r"execution took longer than|[Jj]ob's timeout|timed out after the job timeout"),
    ("config", "CI / YAML / deploy config error", r"YAML parse error|error converting YAML|yaml: line \d+|"
                                                  r"jobs config should|config contains unknown keys|"
                                                  r"Invalid CI config|Error: (?:UPGRADE|INSTALLATION) FAILED|"
                                                  r"unbound variable|variable .* is not set"),
    ("dependency", "npm peer dependency conflict (ERESOLVE)", r"npm (?:ERR!|error) (?:code )?ERESOLVE"),
    ("dependency", "package resolution failure", r"ResolutionImpossible|No matching distribution found|"
                                                 r"Could not find a version that satisfies|npm (?:ERR!|error) code E404|"
                                                 r"Could not resolve dependencies for project|"
                                                 r"lockfile .*(?:out of date|needs to be updated)|frozen-lockfile|"
                                                 r"go: .*(?:unknown revision|cannot find module)"),
    ("test", "pytest failure", r"^=+ (?:FAILURES|ERRORS) =+$|^FAILED \S+::|^E\s{3,}\S"),
    ("test", "unittest failure", r"^(?:FAIL|ERROR): test\w* \("),
    ("test", "jest/vitest failure", r"^Tests:\s+\d+ failed|^\s*(?:FAIL|\u00d7)\s+\S+\.(?:test|spec)\.[jt]sx?"),
    ("test", "go test failure", r"^--- FAIL: |^FAIL\s+\S+\s+[\d.]+s$"),
    ("test", "JUnit/Maven/Gradle test failure", r"Tests run: \d+, Failures: [1-9]|There were failing tests|"
                                                r"\d+ tests completed, \d+ failed"),
    ("test", "rspec failure", r"^\d+ examples?, [1-9]\d* failures?|^rspec \./"),
    ("lint", "lint errors", r"\d+ problems? \(\d+ errors?|^\s*\d+:\d+\s+error\s|Found \d+ errors?\.|"
                            r"^\S+:\d+:\d+: [EFW]\d{3} |offenses? detected|would reformat|"
                            r"Code style issues found"),
    ("build", "type check / compile error", r"error TS\d+:|error\[E\d+\]|: error: |cannot find symbol|"
                                            r"COMPILATION ERROR|^SyntaxError|Found \d+ errors? in \d+ files?"),
    ("infra-flaky", "network error", r"Could not resolve host|Temporary failure in name resolution|"
                                     r"Connection timed out|connection reset by peer|TLS handshake timeout|"
                                     r"i/o timeout|Failed to connect to"),
    ("unknown", "generic error line", r"\b(?:ERROR|Error|error|FATAL|fatal|Exception|Traceback)\b"),
]
SIGS = [(c, l, re.compile(r, re.M)) for c, l, r in SIGNATURES]
NOISE = re.compile(r"probably didn't start properly|Health check error|Health check container logs|"
                   r"No HOST or PORT found|DeprecationWarning|error_bad_lines|ERROR: Job failed: exit code|"
                   r"--root-user-action|^\*+$")
REASON_CLASS = {
    "job_execution_timeout": "timeout", "stuck_or_timeout_failure": "infra-flaky",
    "runner_system_failure": "infra-flaky", "scheduler_failure": "infra-flaky",
    "api_failure": "infra-flaky", "data_integrity_failure": "infra-flaky",
    "runner_unsupported": "infra-flaky", "missing_dependency_failure": "dependency",
    "unmet_prerequisites": "config", "script_failure": None,
}
# Runner set-up/tear-down sections: kept out of the tail unless the error is in them.
BOILERPLATE = {"_runner_header", "_marker", "prepare_executor", "prepare_script", "get_sources", "restore_cache", "download_artifacts",
               "upload_artifacts_on_success", "upload_artifacts_on_failure", "archive_cache",
               "archive_cache_on_failure", "cleanup_file_variables", "resolve_secrets"}
RETRY_HELPS = {"infra-flaky": "yes", "timeout": "maybe", "resource": "no (needs less memory/disk or a bigger runner)"}


def clean(raw):
    """Return list of (raw_line_no, text, section) with markers, ANSI and secrets removed."""
    out, masked, section, sections = [], 0, "_runner_header", []
    for n, line in enumerate(raw.split("\n"), 1):
        line = TS.sub("", line)
        markers = SECTION.findall(line)
        for kind, _, name in markers:
            if kind == "start":
                section = name
                sections.append(name)
            else:
                section = None
        line = SECTION.sub("", line)
        if "\r" in line:
            parts = [p for p in line.split("\r") if ANSI.sub("", p).strip()]
            line = parts[-1] if parts else ""
        line = ANSI.sub("", line).rstrip()
        for rx, rep in MASKS:
            line, k = rx.subn(rep, line)
            masked += k
        out.append((n, line, "_marker" if markers and not line else section))
    while out and not out[-1][1]:
        out.pop()
    return out, masked, sections


def find_signal(lines):
    hits = []
    for cat, label, rx in SIGS:
        for i, (_, text, _) in enumerate(lines):
            if text and not NOISE.search(text) and rx.search(text):
                hits.append((cat, label, i))
                break
    return hits


def collapse(block):
    """Collapse runs of >= 4 lines that are identical once digits are ignored."""
    out, i = [], 0
    norm = [re.sub(r"\d+", "#", t) for _, t, _ in block]
    while i < len(block):
        j = i
        while j + 1 < len(block) and norm[j + 1] == norm[i] and block[i][1]:
            j += 1
        run = j - i + 1
        if run >= 4:
            out += [block[i], block[i + 1], (None, f"[... {run - 3} similar lines collapsed ...]", None), block[j]]
        else:
            out += block[i:j + 1]
        i = j + 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", help="trace file, or - for stdin")
    ap.add_argument("--job-id", default="?")
    ap.add_argument("--job-name", default="?")
    ap.add_argument("--failure-reason", default="")
    ap.add_argument("--before", type=int, default=5)
    ap.add_argument("--after", type=int, default=40)
    ap.add_argument("--tail", type=int, default=80)
    ap.add_argument("--grep", metavar="REGEX",
                    help="instead of the excerpt, print masked lines matching REGEX with 3 lines of context")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    raw = sys.stdin.buffer.read() if a.file == "-" else open(a.file, "rb").read()
    lines, masked, sections = clean(raw.decode("utf-8", errors="replace"))
    total = len(lines)
    if a.grep:
        rx = re.compile(a.grep)
        keep = set()
        for i, (_, t, _) in enumerate(lines):
            if rx.search(t):
                keep |= set(range(max(0, i - 3), min(total, i + 4)))
        print(f"== job {a.job_id} {a.job_name}: {len(keep)} lines around matches of /{a.grep}/ "
              f"(secrets masked: {masked}) ==")
        prev = None
        for i in sorted(keep):
            if prev is not None and i != prev + 1:
                print("   ... |")
            print(f"{lines[i][0]:>6} | {lines[i][1]}")
            prev = i
        return

    exit_code = None
    for _, t, _ in lines:
        m = EXIT.search(t)
        if m:
            exit_code = int(m.group(1))
    hits = find_signal(lines)
    cat, label, anchor = hits[0] if hits else ("unknown", "no error signature found", max(total - 1, 0))
    reason_cat = REASON_CLASS.get(a.failure_reason)
    if reason_cat and reason_cat != cat:
        cat, label = reason_cat, f"{label}; job failure_reason={a.failure_reason}"
    if exit_code == 137 and cat in ("unknown", "test"):
        cat, label = "resource", label + "; exit code 137 = killed (usually out of memory)"

    command = None
    for i in range(min(anchor, total - 1), -1, -1):
        m = CMD.match(lines[i][1])
        if m:
            command = m.group(1)
            break
    failed_section = lines[anchor][2] if lines else None

    start = max(0, anchor - a.before)
    end = anchor + 1
    while end < total and end - anchor <= a.after:
        t = lines[end][1]
        if CMD.match(t) or (lines[end][2] != lines[anchor][2] and lines[end][2] is not None):
            break
        end += 1
    keep = set(range(start, end))
    skip_boiler = failed_section not in BOILERPLATE
    keep |= {i for i in range(max(0, total - a.tail), total)
             if not (skip_boiler and lines[i][2] in BOILERPLATE)}
    groups, cur = [], []
    for i in sorted(keep):
        if cur and i != cur[-1] + 1:
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)

    others = [f"{c}: {lbl} (line {lines[i][0]})" for c, lbl, i in hits[1:] if c not in ("unknown", cat)][:4]
    result = {
        "job_id": a.job_id, "job_name": a.job_name, "failure_reason": a.failure_reason or None,
        "class_hint": cat, "signature": label,
        "anchor_line": lines[anchor][0] if lines else None,
        "failing_command": command, "failed_section": failed_section, "exit_code": exit_code,
        "retry_may_help": RETRY_HELPS.get(cat, "no (fix the cause first)"),
        "raw_lines": total, "secrets_masked": masked, "other_signals": others,
        "sections": sorted(set(sections), key=sections.index),
    }
    shown = []
    for g in groups:
        if shown or g[0] > 0:
            first = shown[-1][0] + 1 if shown and shown[-1][0] else 1
            if g[0] > 0 and lines[g[0]][0] > first:
                last = lines[g[0]][0] - 1
                span = f"line {first}" if last == first else f"lines {first}-{last}"
                shown.append((None, f"[... {span} omitted ...]", None))
        shown += collapse([lines[i] for i in g])
    result["lines_shown"] = sum(1 for n, _, _ in shown if n is not None)
    if a.json:
        result["excerpt"] = [(n, t) for n, t, _ in shown]
        print(json.dumps(result, indent=2))
        return

    print(f"== job {a.job_id} {a.job_name}" + (f" (failure_reason: {a.failure_reason})" if a.failure_reason else "") + " ==")
    print(f"log: {total} lines -> {result['lines_shown']} shown; failed in section: {failed_section or '-'}")
    print(f"failing command: {command or '-'}")
    print(f"exit code: {exit_code if exit_code is not None else '-'}")
    print(f"class hint: {cat} ({label}; first match at line {result['anchor_line']})")
    print(f"retry may help: {result['retry_may_help']}")
    print(f"other signals: {'; '.join(others) if others else 'none'}")
    print(f"secrets masked: {masked}")

    print("--- excerpt (raw log line numbers) ---")
    for n, t, _ in shown:
        print(f"{'' if n is None else n:>6} | {t}")


if __name__ == "__main__":
    main()
