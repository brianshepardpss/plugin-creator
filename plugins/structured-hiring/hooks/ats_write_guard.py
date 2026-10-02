#!/usr/bin/env python3
"""ATS write guard for Greenhouse, Ashby and Lever MCP tools.

Called by hooks/hooks.json with the hook event JSON on stdin.

  pre   PreToolUse: if the tool name is not clearly read-only, return
        permissionDecision "ask" so the user must approve this one call, and
        log a "requested" line. Read-only tools pass silently.
  post  PostToolUse: log an "executed" line for non-read-only tools.

  mail  PreToolUse on email tools: any send / reply / forward call needs the
        user's explicit approval (outreach is drafts-only; the user may still
        approve sending their own non-hiring email). Draft, read and label
        tools pass.
  selftest  run built-in checks on sample events and print PASS/FAIL.

Read-only means the action name (after the last "__") contains no WRITE_WORDS
word and starts with or contains a READ_WORDS word. Everything else --
move, advance, reject, update, create, schedule, change_application_stage,
add_note_to_candidate, get_or_create_candidate, unknown names -- is treated
as a write. Unknown is a write on purpose (fail closed).

Log: $CLAUDE_PLUGIN_DATA/ats-actions.log (JSON lines), falling back to
~/.structured-hiring/ats-actions.log. It records time, phase, tool name and
the names of the input fields plus any *id values. It never records names,
emails, notes, rejection text or other free text.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

READ_WORDS = {"list", "get", "search", "filter", "describe", "find", "read", "fetch",
              "retrieve", "lookup", "query", "count", "view", "show"}
WRITE_WORDS = {"create", "update", "delete", "remove", "move", "advance", "reject", "archive",
               "change", "set", "add", "post", "put", "patch", "schedule", "cancel", "send",
               "submit", "upsert", "edit", "hire", "offer", "merge", "transfer", "consider",
               "tag", "assign", "unreject", "restore", "write", "apply", "note"}
SEND_WORDS = {"send", "reply", "forward"}


def words(tool):
    action = tool.split("__")[-1]
    action = re.sub(r"([a-z])([A-Z])", r"\1_\2", action).lower()
    return [w for w in re.split(r"[^a-z]+", action) if w]


def is_read(tool):
    w = words(tool)
    return bool(w) and not (set(w) & WRITE_WORDS) and bool(set(w) & READ_WORDS)


def is_send(tool):
    return bool(set(words(tool)) & SEND_WORDS)


def selftest():
    cases = [("mcp__plugin_structured-hiring_ashby__get_submitted_feedback", True),
             ("mcp__plugin_structured-hiring_ashby__change_application_stage", False),
             ("mcp__plugin_structured-hiring_greenhouse__list_scorecards", True),
             ("mcp__plugin_structured-hiring_greenhouse__get_or_create_candidate", False),
             ("mcp__greenhouse__candidate_search", True),
             ("mcp__greenhouse__rejectApplication", False),
             ("mcp__greenhouse__mystery_tool", False)]
    bad = 0
    for tool, want in cases:
        ok = is_read(tool) == want
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'} read={want!s:5} {tool}")
    for tool, want in [("mcp__claude_ai_Gmail__send_message", True), ("mcp__claude_ai_Gmail__reply", True),
                       ("mcp__claude_ai_Gmail__create_draft", False), ("mcp__claude_ai_Gmail__forward", True)]:
        ok = is_send(tool) == want
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'} send={want!s:5} {tool}")
    print(f"{bad} failure(s)")
    return bad


def ids(inp):
    out = {}
    if isinstance(inp, dict):
        for k, v in inp.items():
            if re.search(r"(^|_)id$|Id$|_ids$|Ids$", k) and isinstance(v, (str, int, list)):
                out[k] = v
    return out


def log(entry):
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or str(Path.home() / ".structured-hiring")
    try:
        Path(base).mkdir(parents=True, exist_ok=True)
        with open(Path(base) / "ats-actions.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "pre"
    if phase == "selftest":
        sys.exit(1 if selftest() else 0)
    try:
        ev = json.load(sys.stdin)
    except ValueError:
        ev = {}
    tool = ev.get("tool_name", "")
    if phase == "mail":
        if tool and is_send(tool):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "Structured Hiring Kit: this would SEND an email. Candidate outreach is "
                    "drafts-only; approve only if you are sending this yourself on purpose.")}}))
        return
    if not tool or is_read(tool):
        return
    inp = ev.get("tool_input") or {}
    log({"time": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
         "phase": "requested" if phase == "pre" else "executed", "tool": tool,
         "fields": sorted(inp) if isinstance(inp, dict) else [], "ids": ids(inp)})
    if phase == "pre":
        action = tool.split("__")[-1]
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Structured Hiring Kit write guard: '{action}' changes your ATS. "
                "Approve only if this exact change (shown above) is what you want. "
                "Each write needs its own approval; it will be logged without candidate details."),
        }}))


if __name__ == "__main__":
    main()
