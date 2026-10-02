#!/usr/bin/env python3
"""Analyzer Loop environment check. Standard library only.

As a SessionStart hook: silent unless the project root has a pubspec.yaml. Then prints at
most a few lines of context: which `dart` the Dart language server (LSP) will start, its
version, and whether it satisfies pubspec.yaml `environment: sdk:`. Warns when an FVM or
puro pin (.fvmrc, .fvm/fvm_config.json, .puro.json) names a different Flutter than the
SDK on PATH. Never edits files, never uses the network.

Manual use (the /analyzer-loop:doctor command): python3 env_check.py --verbose [project-dir]

Version rule: the lower bound of `sdk:` is read from "^X.Y.Z" or ">=X.Y.Z"; the check is
numeric per part (3.13.5 >= 3.12.0). Upper bounds are ignored (pub enforces them).
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKIP = {".dart_tool", "build", ".git", "node_modules", ".fvm"}


def ver(s):
    return tuple(int(x) for x in re.findall(r"\d+", s)[:3]) if s else ()


def sdk_lower_bound(pubspec_text):
    m = re.search(r"^environment:\s*\n((?:[ \t]+.*\n?)*)", pubspec_text, re.M)
    if not m:
        return None
    s = re.search(r"^\s+sdk:\s*['\"]?([^'\"\n]+)", m.group(1), re.M)
    if not s:
        return None
    lb = re.search(r"(?:\^|>=)\s*(\d+\.\d+(?:\.\d+)?)", s.group(1))
    return lb.group(1) if lb else None


def pinned_flutter(root):
    for rel, key in ((".fvmrc", "flutter"), (".fvm/fvm_config.json", "flutterSdkVersion"), (".puro.json", "env")):
        p = root / rel
        if p.exists():
            try:
                return rel, str(json.loads(p.read_text()).get(key, "")).strip()
            except Exception:
                return rel, ""
    return None, None


def main():
    args = [a for a in sys.argv[1:] if a != "--verbose"]
    verbose = "--verbose" in sys.argv
    root = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    pubspec = root / "pubspec.yaml"
    if not pubspec.exists():
        nested = [q for q in list(root.glob("*/pubspec.yaml")) + list(root.glob("*/*/pubspec.yaml"))
                  if not SKIP.intersection(q.parts)]
        if nested and not shutil.which("dart"):
            print("Analyzer Loop: found Dart/Flutter packages here but `dart` is not on PATH, so the Dart "
                  "language server (LSP) cannot start. Add <flutter>/bin to PATH and restart Claude Code.")
        elif verbose:
            print(f"No pubspec.yaml in {root}; nothing to check.")
        return 0

    lines = []
    dart = shutil.which("dart")
    if not dart:
        lines.append("Analyzer Loop: `dart` is not on PATH, so the Dart language server (LSP) cannot start. "
                     "Install Flutter (includes dart) or add <flutter>/bin to PATH, then restart Claude Code. "
                     "Skills fall back to `flutter analyze` if `flutter` is available.")
        print("\n".join(lines))
        return 0

    try:
        r = subprocess.run([dart, "--version"], capture_output=True, text=True, timeout=10)
        m = re.search(r"Dart SDK version: (\S+)", r.stdout + r.stderr)
        have = m.group(1) if m else "unknown"
    except Exception:
        have = "unknown"
    need = sdk_lower_bound(pubspec.read_text(errors="replace"))
    real = os.path.realpath(dart)
    status = "ok"
    if need and have != "unknown" and ver(have) < ver(need):
        status = "too old"
        lines.append(f"Analyzer Loop: WARNING `dart` on PATH is {have} ({real}) but pubspec.yaml needs sdk >= {need}. "
                     "The LSP and `dart analyze` will report false errors until PATH points at a newer SDK.")
    rel, pin = pinned_flutter(root)
    if rel:
        sdk_hint = "fvm" if "fvm" in rel else "puro"
        if sdk_hint not in real and ".fvm" not in real:
            lines.append(f"Analyzer Loop: {rel} pins Flutter '{pin or '?'}' but `dart` resolves to {real}. "
                         f"Run tools via `{sdk_hint} flutter ...` / `{sdk_hint} dart ...`, and point PATH at the pinned SDK "
                         "so the LSP analyzes with the same version.")
    if not (root / ".dart_tool" / "package_config.json").exists():
        lines.append("Analyzer Loop: no .dart_tool/package_config.json yet; run `flutter pub get` (or `dart pub get`) "
                     "so the analyzer can resolve packages.")
    if not lines or verbose:
        lines.insert(0, f"Analyzer Loop: dart {have} at {real}" + (f", pubspec sdk >= {need} ({status})" if need else ""))
    if verbose:
        f = shutil.which("flutter")
        lines.append(f"flutter on PATH: {os.path.realpath(f) if f else 'not found'}")
        lines.append("LSP command: dart language-server --protocol=lsp (from this plugin's .lsp.json)")
        lines.append("Dart MCP server: not bundled. If Google's dart-flutter plugin is installed, its "
                     "mcp__*dart* tools are used when present; otherwise the CLI is used.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
