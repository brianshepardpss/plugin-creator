#!/usr/bin/env python3
"""Create a plugin skeleton that passes `claude plugin validate --strict`.

Usage:
  python3 scaffold.py <dest-dir> --name <kebab-slug> --display "<Display Name>"
      --description "<one sentence>" --author "<name>" --email <email>
      [--url <author url>] [--repo <https://github.com/owner/repo>]
      [--skills skill-a,skill-b] [--surface code|cowork] [--keywords a,b]

Creates (never overwrites existing files):
  .claude-plugin/plugin.json, README.md, LAUNCH.md, skills/<each>/SKILL.md,
  evals/<each>-basic/{prompt.md,graders/criteria.md}, samples/README.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

RESERVED = re.compile(r"^(claude|anthropic|cc-plugin)-|^(claude|anthropic|claude-code)$")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"  keep   {path}")
        return
    path.write_text(text)
    print(f"  create {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--name", required=True)
    ap.add_argument("--display", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--repo", default="")
    ap.add_argument("--skills", default="")
    ap.add_argument("--surface", choices=["code", "cowork"], default="code")
    ap.add_argument("--keywords", default="")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.name) or RESERVED.search(a.name):
        sys.exit(f"invalid or reserved plugin name: {a.name}")
    d = Path(a.dest)
    author = {"name": a.author, "email": a.email}
    if a.url:
        author["url"] = a.url
    manifest = {
        "name": a.name,
        "displayName": a.display,
        "version": "0.1.0",
        "description": a.description,
        "author": author,
        "license": "MIT",
        "keywords": [k for k in a.keywords.split(",") if k],
        "skills": ["./skills/"],
    }
    if a.repo:
        manifest["homepage"] = a.repo
        manifest["repository"] = a.repo
    write(d / ".claude-plugin" / "plugin.json", json.dumps(manifest, indent=2) + "\n")

    skills = [s.strip() for s in a.skills.split(",") if s.strip()]
    for s in skills:
        write(d / "skills" / s / "SKILL.md", f"""---
name: {s}
description: Use when TODO situation, or when the user says "TODO phrase", "TODO phrase". Produces TODO.
---

# TODO title

1. TODO step.
""")
        write(d / "evals" / f"{s}-basic" / "prompt.md", f"""---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

TODO: a realistic user request that should trigger the {s} skill, using samples/.
""")
        write(d / "evals" / f"{s}-basic" / "graders" / "criteria.md", """---
type: llm
weight: 1
---

PASS if TODO observable outcome.
FAIL if TODO.
""")

    write(d / "samples" / "README.md",
          "Clearly fake sample data so the hero workflow runs with no account.\n")
    surface = ("Claude Code" if a.surface == "code" else "Claude Cowork, claude.ai and Claude Code")
    install = (f"/plugin marketplace add <owner>/<marketplace-repo>\n/plugin install {a.name}@<marketplace>")
    write(d / "README.md", f"""# {a.display}

{a.description}

Works in: {surface}.

## Install

```
{install}
```

## Try it in 60 seconds

TODO: the hero command, run on the bundled sample data.

## What it does

TODO: one line per skill.

## Privacy

TODO: what data leaves your machine (normally: nothing beyond your Claude
conversation and any service you connect yourself).

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

Not affiliated with or endorsed by TODO vendor.
""")
    write(d / "LAUNCH.md", f"""# Launch plan: {a.display}

- Positioning (one line):
- Audience and where they are (specific communities, with links):
- Directory listings: own marketplace, Anthropic plugin directory, community directories.
- Post drafts (one per channel, written for that channel's norms):
- Day-30 signal and threshold:
""")
    print(f"\nScaffolded {a.name} at {d}. Next: fill the TODO placeholders, then run "
          f"`claude plugin validate {d} --strict`.")


if __name__ == "__main__":
    main()
