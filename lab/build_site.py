#!/usr/bin/env python3
"""Generate site/index.html (catalog) and site/built-for-you.html (Level 4
waitlist) from lab/plugins.json and each plugin's manifest.

The waitlist form posts to WAITLIST_ENDPOINT (set in lab/site.json once an
endpoint exists, e.g. the faithstack-style Firebase `subscribe` function);
until then it falls back to a prefilled email. Every outbound link carries
utm_source=site so the traction report can attribute it.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = json.loads((ROOT / "lab" / "plugins.json").read_text())
CFG_F = ROOT / "lab" / "site.json"
CFG = json.loads(CFG_F.read_text()) if CFG_F.exists() else {}
ENDPOINT = CFG.get("waitlist_endpoint", "")
OWNER = REG["owner"]
LEVEL = {1: "Plugins", 2: "Build plugins", 3: "Run a portfolio", 4: "No-code"}

CSS = """
:root{--bg:#fbfaf8;--fg:#1b1a19;--mute:#6b6862;--line:#e6e2dc;--card:#fff;--accent:#c2410c;--chip:#f3efe9}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#151413;--fg:#efece7;--mute:#a19c94;--line:#2c2a27;--card:#1c1b19;--accent:#fb923c;--chip:#262421}}
:root[data-theme=dark]{--bg:#151413;--fg:#efece7;--mute:#a19c94;--line:#2c2a27;--card:#1c1b19;--accent:#fb923c;--chip:#262421}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:40px 16px 64px}
h1{font-size:clamp(28px,5vw,44px);line-height:1.1;margin:0 0 12px;letter-spacing:-.02em}
h2{font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:var(--mute);margin:40px 0 12px}
p.lead{font-size:18px;color:var(--mute);max-width:680px;margin:0 0 20px}
pre{background:var(--chip);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow-x:auto;font-size:14px;margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:8px}
.card h3{margin:0;font-size:17px}.card p{margin:0;color:var(--mute);font-size:14px;flex:1}
.chip{display:inline-block;font-size:12px;background:var(--chip);border-radius:999px;padding:2px 10px;color:var(--mute)}
code{font-size:13px;background:var(--chip);padding:2px 6px;border-radius:5px;word-break:break-all}
a{color:var(--accent)}.btn{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:8px;padding:11px 18px;font:inherit;font-weight:600;cursor:pointer;text-decoration:none}
form{display:grid;gap:10px;max-width:520px}input,textarea{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
footer{margin-top:56px;color:var(--mute);font-size:13px}
"""


def page(title, desc, body):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<style>{CSS}</style></head><body><div class="wrap">{body}
<footer>Made by Press Start Studios. Independent project; not affiliated with or endorsed by Anthropic.
Plugins are MIT licensed. Contact: <a href="mailto:brian@press-start-studios.com">brian@press-start-studios.com</a></footer>
</div></body></html>
"""


def cards(entries):
    out = []
    for e in entries:
        mf = ROOT / "plugins" / e["slug"] / ".claude-plugin" / "plugin.json"
        if not mf.exists():
            continue
        m = json.loads(mf.read_text())
        where = "Claude Code" if e["surface"] == "code" else "Cowork, claude.ai, Claude Code"
        repo = f"https://github.com/{OWNER}/{e['repo']}?utm_source=site&utm_campaign={e['slug']}"
        out.append(f"""<div class="card"><span class="chip">{html.escape(e['audience'])}</span>
<h3>{html.escape(m['displayName'])}</h3><p>{html.escape(m['description'])}</p>
<span class="chip">{where}</span><code>/plugin install {e['slug']}@{REG['marketplace']}</code>
<a href="{repo}">Source, docs and evals</a></div>""")
    return "".join(out)


def index():
    groups = []
    for lvl in (1, 2, 3, 4):
        es = [e for e in REG["plugins"] if e["level"] == lvl]
        if es:
            groups.append(f"<h2>{LEVEL[lvl]}</h2><div class='grid'>{cards(es)}</div>")
    body = f"""<h1>Claude plugins for the gaps</h1>
<p class="lead">Focused plugins for industries and tools the official directory doesn't cover yet,
each with sample data so it works in the first five minutes, guardrails written into the skills,
and an eval suite. Built with Plugin Creator, which you can use too.</p>
<pre>/plugin marketplace add {OWNER}/{REG['marketplace']}</pre>
{''.join(groups)}
<h2>Not a developer?</h2><p class="lead">We can build one from your own examples.
<a href="built-for-you.html">See how it works</a>.</p>"""
    return page("Plugin Creator", "Claude plugins for the gaps in the official directory.", body)


def built_for_you():
    if ENDPOINT:
        form = f"""<form method="post" action="{html.escape(ENDPOINT)}">
<input type="hidden" name="list" value="built-for-you">
<input name="email" type="email" required placeholder="you@business.com" aria-label="Email">
<input name="role" placeholder="What you do (e.g. property manager)" aria-label="Role">
<textarea name="task" rows="3" placeholder="The task you repeat every week" aria-label="Task"></textarea>
<button class="btn" type="submit">Join the waitlist</button></form>"""
    else:
        form = ("<p><a class='btn' href=\"mailto:brian@press-start-studios.com?subject=Built-for-you%20plugin%20waitlist"
                "&body=What%20I%20do%3A%0A%0AThe%20task%20I%20repeat%3A%0A\">Join the waitlist by email</a></p>")
    body = f"""<h1>Your way of doing it, as a one-click Claude assistant</h1>
<p class="lead">Send us two or three past examples of something you write or prepare over and over:
deposit letters, client recaps, quotes, lesson plans, inspection reports. We turn them into a tested
Claude plugin that does it your way, then hand you the file. No coding, and your examples stay private.</p>
<h2>How it works</h2>
<div class="grid">
<div class="card"><h3>1. Send examples</h3><p>Two or three finished examples, with anything private removed.</p></div>
<div class="card"><h3>2. We build and test</h3><p>We build the plugin and test it against your own examples until it matches.</p></div>
<div class="card"><h3>3. Install in one click</h3><p>You get a .plugin file for Claude Cowork or claude.ai. Ask for changes any time.</p></div>
</div>
<h2>Join the waitlist</h2>{form}
<p class="lead" style="margin-top:20px">Prefer to do it yourself? The free
<a href="https://github.com/{OWNER}/make-my-plugin?utm_source=site&utm_campaign=built-for-you">Make My Plugin</a>
does the same interview inside Claude.</p>"""
    return page("Built For You", "Turn your own examples into a one-click Claude assistant.", body)


if __name__ == "__main__":
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(index())
    (site / "built-for-you.html").write_text(built_for_you())
    print("wrote site/index.html and site/built-for-you.html"
          + ("" if ENDPOINT else " (waitlist falls back to email: set waitlist_endpoint in lab/site.json)"))
