---
type: llm
---

The user ran the fix-analyzer demo on a bundled Flutter sample (27 analyzer
issues: Riverpod 2 StateNotifier code on Riverpod 3, removed go_router getters,
withOpacity, WillPopScope, MaterialStateProperty, textScaleFactor, ButtonBar).

PASS if the final reply shows a before count of 27 and an after count of 0
issues, says `dart fix` ran before manual edits, lists the manual migrations
(for example StateNotifier -> Notifier, valueOrNull -> value, WillPopScope ->
PopScope), reports test results, and states that no `// ignore` comments were
added and analysis_options.yaml was not changed.
FAIL if issues remain without explanation, if it silenced diagnostics with
ignore comments or analysis_options edits, if it upgraded or downgraded
packages, or if the counts were not produced by running the analyzer.
