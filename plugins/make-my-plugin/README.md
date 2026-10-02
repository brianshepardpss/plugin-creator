# Make My Plugin

Turn the way you already do a recurring task into your own Claude assistant,
with no coding. Claude asks you a few questions, learns from two or three
past examples of your work, tests itself against one of them, and hands you
a file you install with one click. From then on, "write the deposit letter
for unit 2" (or whatever your task is) gets done your way, every time.

Made for people who are experts in their work, not in software: property
managers, office managers, coaches, contractors, bookkeepers, teachers.

Works in: Claude Cowork, claude.ai and Claude Code.

## Install

In Claude Code:

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install make-my-plugin@plugin-creator
```

In Cowork or claude.ai, download `make-my-plugin.plugin` from the latest
[release](https://github.com/brianshepardpss/make-my-plugin/releases) and
install it.

## Try it in 60 seconds

Say: "Make me a plugin from the sample move-out letters." It walks through
the interview using the bundled examples from a fictional property manager,
builds a Deposit Letter Assistant, tests it on new inspection notes, and
packages it.

Then try it on your own work: `/make-my-plugin:make` and describe the task.

## What it does

| Piece | Purpose |
|---|---|
| `/make-my-plugin:make` | The whole flow: interview, build, test, package |
| capture-workflow | A short, plain-language interview that writes WORKFLOW.md |
| build-my-plugin | Builds the plugin, tests it on your own example, packages a `.plugin` file |
| improve-my-plugin | "It keeps getting X wrong" -- fixes, retests and repackages |
| share-my-plugin | Optional: a generalized, anonymized public version you can submit |

Any numbers in your task (totals, dates, prices) are computed by a small
script built from the rules you give, never guessed.

## Privacy

Your examples and your plugin stay in your Claude account and on your
machine. Nothing is shared unless you use share-my-plugin and submit the
public copy yourself, after reviewing every file.

## Feedback

Say "I wish this could..." and the request skill drafts a note for you to
send. Nothing is sent automatically.

Not affiliated with or endorsed by Anthropic.
