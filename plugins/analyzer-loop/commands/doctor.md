---
description: Check that the Dart language server and Flutter tooling Analyzer Loop needs are installed and match this project
argument-hint: "[project dir]"
allowed-tools: Bash(python3:*), Bash(dart --version), Bash(flutter --version)
---

Check the Analyzer Loop environment for the project in $ARGUMENTS (default: the current directory).

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/env_check.py" --verbose $ARGUMENTS` and show its output verbatim.
2. Run `flutter --version` if `flutter` is on PATH and add the Flutter and Dart versions.
3. Say whether any tools whose names contain `dart` from an MCP server (for example Google's dart-flutter plugin) are available in this session. Do not install or configure one.
4. End with at most three concrete next steps, for example "add <flutter>/bin to PATH and restart Claude Code so the LSP can start", "run flutter pub get", or "use fvm dart because .fvmrc pins another version". If everything is fine, say so in one line and suggest `/analyzer-loop:fix-analyzer sample` as a demo that takes under 5 minutes.
