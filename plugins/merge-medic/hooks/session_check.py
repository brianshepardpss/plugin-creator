#!/usr/bin/env python3
"""SessionStart check: is this a GitLab repo, and is glab ready for it?

Silent unless there is something to fix. Reads only local state (git
remote, GITLAB_HOST, the glab config file, `glab --version`); the one
network call is `glab auth status --hostname <host>`, made only when glab is
installed and the remote looks like GitLab.

Host resolution, in order: the `origin` remote's host; GITLAB_HOST if there
is no remote. A host counts as GitLab when it is gitlab.com, contains
"gitlab", equals GITLAB_HOST, appears in glab's config, or the repo has a
.gitlab-ci.yml at its root. GitHub, Bitbucket,
Azure DevOps and Codeberg remotes are ignored.

Prints Claude Code hook JSON: `systemMessage` (one line for the user) when
setup is incomplete, `additionalContext` (for Claude) when everything is
ready. Set MERGE_MEDIC_SESSION_CHECK=off to disable. Standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_GLAB = (1, 119, 0)  # first release with `glab mr note create --draft` and `glab mr note publish`
NOT_GITLAB = re.compile(r"(^|\.)(github\.com|bitbucket\.org|dev\.azure\.com|visualstudio\.com|codeberg\.org)$")


def run(args, cwd, timeout=4):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def host_of(url):
    m = re.match(r"^(?:[a-z+]+://)?(?:[^@/]+@)?([^/:]+)", url.strip())
    return m.group(1).lower() if m else None


def glab_config_hosts():
    dirs = [os.environ.get("GLAB_CONFIG_DIR"), os.environ.get("XDG_CONFIG_HOME") and
            str(Path(os.environ["XDG_CONFIG_HOME"]) / "glab-cli"),
            str(Path.home() / ".config" / "glab-cli"),
            str(Path.home() / "Library" / "Application Support" / "glab-cli"),
            os.environ.get("APPDATA") and str(Path(os.environ["APPDATA"]) / "glab-cli")]
    hosts = set()
    for d in filter(None, dirs):
        f = Path(d) / "config.yml"
        if f.is_file():
            try:
                text = f.read_text(errors="replace")
            except OSError:
                continue
            block = re.search(r"^hosts:\s*\n((?:[ \t]+.*\n?)*)", text, re.M)
            if block:
                hosts |= {h.lower() for h in re.findall(r"^[ \t]{4}([A-Za-z0-9.\-]+):\s*$", block.group(1), re.M)}
    return hosts


def version_tuple(text):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(int(x) for x in m.groups()) if m else None


def emit(user=None, context=None):
    out = {}
    if user:
        out["systemMessage"] = user
    if context:
        out["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": context}
    if out:
        print(json.dumps(out))


def main():
    if os.environ.get("MERGE_MEDIC_SESSION_CHECK", "").lower() == "off":
        return
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    cwd = data.get("cwd") or os.getcwd()
    rc, url = run(["git", "remote", "get-url", "origin"], cwd, timeout=3)
    env_host = host_of(os.environ.get("GITLAB_HOST", "")) if os.environ.get("GITLAB_HOST") else None
    host = host_of(url) if rc == 0 and url else env_host
    if not host or NOT_GITLAB.search(host):
        return
    rc_top, top = run(["git", "rev-parse", "--show-toplevel"], cwd, timeout=3)
    has_ci = rc_top == 0 and (Path(top) / ".gitlab-ci.yml").is_file()
    if not (host == "gitlab.com" or "gitlab" in host or host == env_host or has_ci
            or host in glab_config_hosts()):
        return

    login = f"glab auth login --hostname {host}"
    glab = shutil.which("glab")
    if not glab:
        emit(user=f"Merge Medic: this repo's remote is GitLab ({host}) but glab is not installed. "
                  f"Install it (https://gitlab.com/gitlab-org/cli#installation, e.g. `brew install glab`), "
                  f"then run `{login}`. To try the plugin without an account: /gl-fix-pipeline demo")
        return
    _, vout = run([glab, "--version"], cwd)
    ver = version_tuple(vout)
    notes = []
    if ver and ver < MIN_GLAB:
        notes.append(f"glab {'.'.join(map(str, ver))} is older than {'.'.join(map(str, MIN_GLAB))}; "
                     f"draft review comments need an upgrade (`brew upgrade glab`)")
    rc, _ = run([glab, "auth", "status", "--hostname", host], cwd, timeout=8)
    if rc != 0:
        notes.append(f"glab is not logged in to {host}: run `{login}` (token scopes: api, write_repository)")
    if notes:
        emit(user="Merge Medic: " + "; ".join(notes) + ".")
        return
    emit(context=f"Merge Medic: origin is GitLab host {host} (self-managed hosts work the same way); "
                 f"glab {'.'.join(map(str, ver)) if ver else '?'} is authenticated. Use glab, not gh, "
                 f"for merge requests and pipelines in this repo.")


if __name__ == "__main__":
    main()
