---
description: Take a plugin idea from one sentence to a validated, tested plugin folder
argument-hint: <one-sentence plugin idea>
---

Build a Claude plugin for this idea: $ARGUMENTS

Work through these stages in order, using the matching skill for each. Stop
and check in with the user at the two marked points.

1. **Brief** (plugin-brief skill): run the demand scan, research the user and
   the competition, write BRIEF.md. If an official plugin already covers the
   idea and you cannot name a real gap, say so and stop.
   CHECK IN: show the hero workflow, skill list and omissions; wait for a go.
2. **Scaffold** (plugin-scaffold skill): name, surface, skeleton, then samples,
   scripts, skills, README, LAUNCH.md, in that order. Follow the
   skill-writing skill for every SKILL.md.
3. **Review**: delegate to the plugin-reviewer agent and fix what it finds.
4. **Evals** (plugin-evals skill): at least a hero, guardrail and trigger case
   (and an exact-math case if the plugin computes numbers). Run them with the
   no-plugin baseline and fix until they pass.
5. **Ship prep** (plugin-ship skill): preflight with --package, listing
   texts and launch posts.
   CHECK IN: list every outward action (repo creation, pushes, submissions,
   posts) and do none of them without an explicit yes.

End with: the plugin folder path, the eval scores with and without the
plugin, and the exact next command.
