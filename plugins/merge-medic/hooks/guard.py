#!/usr/bin/env python3
"""PreToolUse guard: ask the user before destructive or publishing glab
commands, and before force pushes. Never blocks outright; it returns
permissionDecision "ask" with a reason, so the user decides.

Asks before:
  glab mr merge | approve | close | delete | rebase | revoke
  glab mr note publish | delete
  glab ci delete | cancel
  glab api with -X/--method DELETE, PUT or PATCH, a POST to an
    approve/merge/publish endpoint, or a graphql mutation
  any other `glab ... delete|revoke|rotate|archive|transfer` subcommand
    (repo, release, variable, label, token, schedule, ...)
  glab variable set|update (overwrites CI/CD variables)
  git push --force / -f / --force-with-lease / --delete / +refspec / :branch
    (also behind git -C/-c options)
Looks through wrappers (env, sudo, timeout, nice, xargs, ...), `bash -c`,
`sh -c`, `eval`, $(...) and backticks. Quoted text is not a command, so
`git commit -m "glab mr merge"` passes.

Set MERGE_MEDIC_GUARD=off to disable. Standard library only.
"""
import json
import os
import re
import shlex
import sys

SPLIT = re.compile(r"\|\||&&|[;|\n]|\$\(|`")
WRAPPERS = {"env", "sudo", "doas", "command", "time", "nohup", "exec", "xargs", "timeout", "nice",
            "ionice", "stdbuf", "builtin"}
MR_ASK = {
    "merge": "merges the merge request into its target branch",
    "approve": "records your approval on the merge request",
    "close": "closes the merge request",
    "delete": "deletes the merge request",
    "rebase": "rebases (rewrites) the MR source branch on the server",
    "revoke": "revokes your approval",
}
GENERIC = {"delete", "revoke", "rotate", "archive", "transfer"}


def tokens(segment):
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def strip_globals(args):
    out, i = [], 0
    while i < len(args):
        if args[i] in ("-R", "--repo"):
            i += 2
            continue
        if args[i].startswith("--repo="):
            i += 1
            continue
        out.append(args[i])
        i += 1
    return out


def check_glab(args):
    args = strip_globals(args)
    words = [a for a in args if not a.startswith("-")]
    if not words:
        return None
    top = words[0]
    sub = words[1] if len(words) > 1 else ""
    if top == "mr" and sub == "note" and len(words) > 2 and words[2] in ("publish", "delete"):
        what = ("publishes ALL your pending (draft) review comments; everyone on the MR sees them and gets notified"
                if words[2] == "publish" else "deletes a comment")
        return f"`glab mr note {words[2]}` {what}."
    if top == "mr" and sub in MR_ASK:
        return f"`glab mr {sub}` {MR_ASK[sub]}."
    if top == "ci" and sub in ("delete", "cancel"):
        return f"`glab ci {sub}` {'deletes pipelines' if sub == 'delete' else 'cancels a running pipeline or job'}."
    if top == "variable" and sub in ("set", "update", "delete"):
        return f"`glab variable {sub}` changes CI/CD variables used by every pipeline."
    if top == "api":
        method = None
        for i, a in enumerate(args):
            if a in ("-X", "--method") and i + 1 < len(args):
                method = args[i + 1]
            elif a.startswith("--method="):
                method = a.split("=", 1)[1]
            elif a.startswith("-X") and len(a) > 2:
                method = a[2:]
        method = (method or "").upper()
        endpoint, i = "", 1
        valued = {"-X", "--method", "-f", "--raw-field", "-F", "--field", "-H", "--header", "--hostname",
                  "--input", "--form", "--jq", "-t", "--template"}
        while i < len(args):
            if args[i] in valued:
                i += 2
                continue
            if not args[i].startswith("-"):
                endpoint = args[i]
                break
            i += 1
        if method in ("DELETE", "PUT", "PATCH"):
            return f"`glab api -X {method} {endpoint}` changes or deletes data on the GitLab server."
        if endpoint == "graphql" and re.search(r"\bmutation\b", " ".join(args)):
            return "`glab api graphql` with a mutation changes data on the GitLab server."
        if re.search(r"/(approve|unapprove|merge|bulk_publish|publish)\b", endpoint) and method in ("", "POST"):
            return f"`glab api {endpoint}` approves, merges or publishes on the GitLab server."
        return None
    if sub in GENERIC or top in GENERIC:
        return f"`glab {top} {sub}` is destructive or irreversible."
    return None


GIT_GLOBAL_VALUED = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
WRAPPER_VALUED = {"-n", "-I", "-u", "-g", "-s", "-k", "-L", "-P", "-d", "--adjustment", "--signal",
                  "--kill-after", "--user", "--group"}


def check_git_push(args):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_GLOBAL_VALUED else 1
    args = args[i:]
    if not args or args[0] != "push":
        return None
    for a in args[1:]:
        if a in ("-f", "--force", "--delete", "-d", "--mirror") or a.startswith("--force"):
            return f"`git push {a}` can overwrite or delete commits on the remote branch."
        if not a.startswith("-") and (a.startswith("+") or (a.startswith(":") and len(a) > 1)):
            return f"`git push {a}` force-updates or deletes a remote branch."
    return None


def segments(command):
    """Split a shell command into simple commands, respecting quotes."""
    for line in command.split("\n"):
        try:
            lex = shlex.shlex(line, posix=True, punctuation_chars=";&|()<>")
            lex.whitespace_split = True
            toks = list(lex)
        except ValueError:
            toks = SPLIT.sub(" ; ", line).split()
        seg = []
        for t in toks:
            if t and set(t) <= set(";&|()<>"):
                if seg:
                    yield seg
                seg = []
            else:
                seg.append(t)
        if seg:
            yield seg


def strip_wrappers(toks):
    while toks:
        head = os.path.basename(toks[0])
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in ("$", "`"):
            toks = toks[1:]
        elif head in WRAPPERS:
            toks = toks[1:]
            while toks and toks[0].startswith("-"):
                toks = toks[2:] if toks[0] in WRAPPER_VALUED else toks[1:]
            if head == "timeout" and toks:
                toks = toks[1:]  # the duration
        else:
            break
    return toks


def check(command, depth=0):
    if depth > 3:
        return None
    for inner in re.findall(r"`([^`]+)`", command):  # backtick substitutions
        r = check(inner, depth + 1)
        if r:
            return r
    for seg in segments(command):
        toks = strip_wrappers([t.strip("`") for t in seg])
        if not toks:
            continue
        exe = os.path.basename(toks[0])
        if exe in ("bash", "sh", "zsh", "dash", "ksh") and "-c" in toks:
            i = toks.index("-c")
            r = check(toks[i + 1], depth + 1) if i + 1 < len(toks) else None
        elif exe == "eval":
            r = check(" ".join(toks[1:]), depth + 1)
        elif exe in ("glab", "glab.exe"):
            r = check_glab(toks[1:])
        elif exe in ("git", "git.exe"):
            r = check_git_push(toks[1:])
        else:
            r = None
        if r:
            return r
    return None


def main():
    if os.environ.get("MERGE_MEDIC_GUARD", "").lower() == "off":
        return
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""
    reason = check(cmd)
    if not reason:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"Merge Medic guard: {reason} Approve only if you meant to do this now.",
    }}))


if __name__ == "__main__":
    main()
