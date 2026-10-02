#!/usr/bin/env python3
"""Create the Merge Medic demo project: a small git repo whose `origin`
points at a fictional self-managed GitLab host, plus the fake `glab` that
replays recorded API responses for it. No GitLab account or network needed.

Usage:
  python3 setup_demo.py [DEST] [--branch feature/late-fees|fix/csv-export-encoding]

DEST defaults to ./merge-medic-demo. Re-running on an existing DEST is
refused so nothing is overwritten.

What you get:
  - branches main, feature/late-fees (MR !42, red pipeline 1873) and
    fix/csv-export-encoding (no MR yet)
  - origin fetch URL https://gitlab.example-corp.test/platform/invoice-api.git
    (self-managed, fictional); pushes go to a local bare repo inside .git/
  - the fake glab at samples/bin/glab (call it by absolute path)
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "demo-repo"
HOST = "gitlab.example-corp.test"
REMOTE = f"https://{HOST}/platform/invoice-api.git"
DATES = {
    "main": "2026-09-28T10:00:00+00:00",
    "feature/late-fees": "2026-09-30T14:20:00+00:00",
    "fix/csv-export-encoding": "2026-10-01T09:05:00+00:00",
}
MESSAGES = {
    "main": "Initial invoice CSV export",
    "feature/late-fees": "Add late fees to invoice export",
    "fix/csv-export-encoding": "Write CSV export with a UTF-8 BOM so Excel shows accents\n\n"
                               "Finance reported mangled customer names when opening the\n"
                               "export in Excel. Related to issue #17.",
}


def git(dest, *args, date=None):
    env = dict(os.environ)
    env.update(GIT_AUTHOR_NAME="Demo Dev", GIT_AUTHOR_EMAIL="demo.dev@example.test",
               GIT_COMMITTER_NAME="Demo Dev", GIT_COMMITTER_EMAIL="demo.dev@example.test")
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    r = subprocess.run(["git", *args], cwd=dest, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def overlay(src, dest):
    for p in src.rglob("*"):
        if p.is_file():
            t = dest / p.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest", nargs="?", default="merge-medic-demo")
    ap.add_argument("--branch", default="feature/late-fees",
                    choices=["main", "feature/late-fees", "fix/csv-export-encoding"])
    a = ap.parse_args()
    dest = Path(a.dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"{dest} already exists and is not empty; pick another DEST.")
    dest.mkdir(parents=True, exist_ok=True)

    git(dest, "init", "-q", "-b", "main")
    git(dest, "config", "user.name", "Demo Dev")
    git(dest, "config", "user.email", "demo.dev@example.test")
    overlay(SRC / "main", dest)
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", MESSAGES["main"], date=DATES["main"])
    for br, folder in (("feature/late-fees", "feature-late-fees"),
                       ("fix/csv-export-encoding", "fix-csv-export-encoding")):
        git(dest, "checkout", "-q", "-b", br, "main")
        overlay(SRC / folder, dest)
        git(dest, "add", "-A")
        git(dest, "commit", "-q", "-m", MESSAGES[br], date=DATES[br])

    bare = dest / ".git" / "merge-medic-fake" / "remote.git"
    bare.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    git(dest, "remote", "add", "origin", REMOTE)
    git(dest, "remote", "set-url", "--push", "origin", str(bare))
    git(dest, "push", "-q", "origin", "main", "feature/late-fees")
    git(dest, "checkout", "-q", a.branch)
    if a.branch != "fix/csv-export-encoding":
        git(dest, "branch", "-q", "--set-upstream-to", f"origin/{a.branch}")

    glab = HERE / "bin" / "glab"
    print(f"Demo project ready: {dest}")
    print(f"Branch:            {a.branch}")
    print(f"GitLab host:       {HOST} (fictional self-managed; pushes go to a local bare repo)")
    print(f"Fake glab:         {glab}")
    print("Use the fake glab by absolute path for every glab call in this demo, e.g.")
    example = ("ci get --merge-request 42 --status failed -F json" if a.branch == "feature/late-fees"
               else "mr view -F json   (no MR yet for this branch)")
    print(f"  cd {dest} && {glab} {example}")


if __name__ == "__main__":
    main()
