---
name: plugin-evals
description: Use when testing a Claude plugin, or when the user says "write evals", "test my plugin", "does my skill actually help", "benchmark the plugin", or "why did the eval fail". Writes eval cases from the brief's scenarios, runs `claude plugin eval` with a no-plugin baseline, and turns failures into fixes.
---

# Prove the plugin works, and that it beats no plugin

## Case layout

```
evals/<case>/prompt.md           frontmatter + the user's request
evals/<case>/graders/<name>.md   one file per check
```

prompt.md frontmatter: `max_turns` (10-20), `allowed_tools` (only what the
case needs, e.g. `[Read, Glob, Grep, Skill, Bash]`), optional `runs`,
`timeout_seconds`, `model`, `tags`.

Each run starts in an EMPTY working directory with only the plugin loaded.
The plugin's own files (samples, scripts) are reachable through the skill's
base directory, so a prompt like "try it on the sample data" works if the
skill knows where its samples live. For files that must sit in the
workspace, add `case.yaml` with `context.scaffold_script: fixture.sh` (runs
only with `--scaffold`) or `context.add_dirs: [resources]` (read-only).

Grader frontmatter (`type:` plus options; the body of an `llm` grader is its
criteria):

```
type: tool_used                      # the skill fired
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'
arm: with-only                       # don't score this in the no-plugin arm
---
type: regex                          # exact value in the final reply
pattern: '20\.28\s*%'
target: last_message                 # or trace, files, {source: file, path: out.md}
---
type: file_exists
path: '**/*.ics'
---
type: llm
focus: last_message
```

`regex` supports `match: not_contains` and `match: "count:N"`, and
`flags: i`. `file_exists` sees only files created during the run. Prefer
the free deterministic graders for anything exact; use `llm` for quality.

## Which cases to write

One per brief scenario, at least three, and always:

1. **Hero case:** the hero workflow on `samples/`. Graders check the
   artifact exists and the key facts are right.
2. **Exact-math case** (if the plugin computes numbers): a `regex` grader
   for the exact value the bundled script produces. Run the script yourself
   first and copy its output into the grader.
3. **Guardrail case:** a request the plugin must refuse, warn about or
   soften. The `llm` grader names the forbidden behaviour explicitly.
4. **Trigger case:** a natural phrasing with no skill name in it, graded
   with `tool_used` on Skill, so you know the description triggers.

Write prompts the way users talk, not the way the skill is titled.

## Run

```
claude plugin eval <plugin-dir> --runs 3 --threshold 0.8 -j 3
```

Ablation (a no-plugin baseline) is on by default for a plugin target; read
the delta. A case where the baseline scores as well as the plugin is not
testing the plugin; make it harder or drop it. Cases run Bash and Write
only if granted (`--allow-tools Bash Write`). MCP servers are mocked unless
you record mocks or pass `--mocks off` for trusted servers.

## Fix loop

For each failing case, read the transcript in the HTML report and classify:

- Skill never loaded: the description does not match how users ask. Rewrite
  it with their words.
- Skill loaded, wrong output: the procedure is ambiguous. Add the literal
  output template or a script.
- Grader wrong: fix the grader, and say so; never loosen a grader just to
  pass.

Re-run until every case clears the threshold. Commit the evals with the
plugin; directory reviewers and users trust a plugin that ships its tests.
