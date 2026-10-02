---
name: plugin-brief
description: Use before building any Claude plugin, or when the user asks "is there demand for a plugin that does X", "what should my plugin do", "research a plugin idea", "who would use this plugin", or "is X already covered". Measures demand and existing supply with live data, then writes BRIEF.md, the design brief every later step builds from.
---

# Write a plugin brief

A plugin is only as good as its brief. The brief decides who the plugin is
for, the one workflow it must nail, and what it must refuse to do. Do not
scaffold anything until BRIEF.md exists and the user has seen its section 4.

## 1. Measure, don't guess

Run the bundled scanner from this skill's directory with the idea's name and
one or two synonyms:

```
python3 <this skill dir>/demand.py "<primary term>" "<synonym>"
```

It reports GitHub issue demand on the Claude repos (sorted by reactions),
Hacker News stories, official Anthropic plugins that already match, Smithery
MCP servers and npm MCP packages, plus a transparent gap score. Read its
caveats:

- GitHub and HN only see developer demand. For industry or business plugins,
  near-zero demand there is normal; go to step 2 for the real signal.
- A matching official plugin is the most important single fact. If one
  exists, open it (its repo is in the marketplace entry) and find what it
  lacks before going further. If it lacks nothing, say so and stop.

## 2. Research the user, not the technology

Use web search and fetch. Find, with links:

- Who does this job, how often, and what it costs them (time, money,
  mistakes). Prefer practitioner forums, industry surveys and job postings
  over vendor marketing.
- What they use today, including spreadsheets and ChatGPT, what that costs,
  and what people complain about.
- What data they already have and can export (CSV, PDF, API). The best MVPs
  run on files the user already has.
- For any API: who can get credentials (self-serve, admin-only, partner-only),
  plan tiers with API access, rate limits, and whether the vendor ships an
  official MCP server. Reuse an official MCP server before building one.
- Legal and safety rules for the domain (discrimination law, privacy,
  professional liability, trademarks, data licences).

Mark anything you could not confirm as [UNVERIFIED].

## 3. Write BRIEF.md

Use `brief-template.md` in this skill's directory. Keep it under ~1500 words.
The sections that matter most:

- **Hero workflow:** one job, end to end, under 5 minutes, runnable on
  bundled sample data with no account. If you cannot name one, the idea is
  not ready.
- **Deliberate omissions:** what v1 will not do, and why.
- **Guardrails:** concrete rules the skills must follow, traced to section 7.
- **Eval scenarios:** 5 prompts with pass criteria a grader can check.
- **Day-30 signal:** the number that would justify a v2, chosen before launch.

## 4. Check in

Show the user the hero workflow, the skill list and the omissions, and ask
for a go-ahead before scaffolding. Change the brief, not the plan in your
head, when they push back.
