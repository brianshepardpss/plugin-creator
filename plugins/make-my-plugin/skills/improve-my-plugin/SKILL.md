---
name: improve-my-plugin
description: Use when someone's own custom plugin got something wrong or they want it to do more, or they say "it keeps getting X wrong", "change my assistant", "it should also", "update my plugin", or "it doesn't sound like me". Edits the user's plugin from plain-language feedback, retests it, and repackages it with a new version number.
---

# Improve the user's plugin from feedback

1. Find the plugin folder (ask if there are several) and its WORKFLOW.md.
2. Ask for the specific case: what they gave it, what it produced, what it
   should have produced. One concrete example beats a general complaint.
3. Decide where the fix belongs and say it in plain words:
   - It didn't start when asked: add their phrasing to the description.
   - Wrong structure: change the output template.
   - Wrong tone or wording: add or swap an example in `examples/`.
   - Broke a rule: turn the rule into an explicit check step.
   - Wrong number: fix `calc.py` and its rule; never patch numbers in prose.
4. Update WORKFLOW.md to match, so the description of the task and the
   plugin never drift apart.
5. Re-run their failing case and show before and after.
6. Bump the version in `.claude-plugin/plugin.json` (1.0.0 -> 1.1.0) and
   repackage with the build-my-plugin skill's `package.py`. Tell them to
   install the new file over the old one.
