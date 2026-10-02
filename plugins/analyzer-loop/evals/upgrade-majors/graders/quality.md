---
type: llm
---

The sample starts on flutter_riverpod 2.6.1 and go_router 6.5.9; the latest
majors are 3.x and 18.x, and upgrading breaks the code (StateNotifier,
FutureProviderRef, valueOrNull, state.params/queryParams/location).

PASS if the reply shows both packages moved to the new majors, cites specific
breaking changes taken from the packages' changelogs, migrates the code
(StateNotifier -> Notifier or the legacy import, Ref, value,
pathParameters / uri.queryParameters / uri), reports `dart analyze` at 0
issues and the tests passing, and did not add `// ignore` comments,
dependency_overrides, or edit analysis_options.yaml.
FAIL if either package stays on its old major, the analyzer still has errors,
tests were not run, or diagnostics were silenced instead of fixed.
