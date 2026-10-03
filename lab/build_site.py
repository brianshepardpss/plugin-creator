#!/usr/bin/env python3
"""Generate docs/index.html (catalog), docs/built-for-you.html (Level 4
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
POSTHOG_KEY = CFG.get("posthog_key", "")
POSTHOG_HOST = CFG.get("posthog_host", "https://us.i.posthog.com")
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
table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mute);font-weight:500}
.thanks{display:none;font-weight:600}
"""


def posthog(page_name):
    if not POSTHOG_KEY:
        return ""
    return f"""<script>
!function(t,e){{var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){{function g(t,e){{var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){{var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}},u.people.toString=function(){{return u.toString(1)+".people (stub)"}},o="init capture register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset identify get_distinct_id".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])}},e.__SV=1)}}(document,window.posthog||[]);
posthog.init({json.dumps(POSTHOG_KEY)}, {{api_host: {json.dumps(POSTHOG_HOST)}, person_profiles: "never", persistence: "memory"}});
posthog.register({{site_page: {json.dumps(page_name)}}});
document.addEventListener("click", function (e) {{
  var el = e.target.closest("[data-track]");
  if (el) posthog.capture(el.getAttribute("data-track"), {{plugin: el.getAttribute("data-plugin") || null, href: el.getAttribute("href") || null}});
}});
</script>"""


def page(title, desc, body, name="index"):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<style>{CSS}</style>{posthog(name)}</head><body><div class="wrap">{body}
<footer>Made by Press Start Studios. Independent project; not affiliated with or endorsed by Anthropic.
Plugins are MIT licensed. Contact: <a href="mailto:brian@press-start-studios.com">brian@press-start-studios.com</a></footer>
</div></body></html>
"""


def md_section(md, heading):
    """Return the body of '## heading' from a README, or ''."""
    lines, out, on = md.splitlines(), [], False
    for ln in lines:
        if ln.startswith("## "):
            if on:
                break
            on = ln[3:].strip().lower().startswith(heading.lower())
            continue
        if on:
            out.append(ln)
    return "\n".join(out).strip()


def md_html(md):
    """Tiny markdown subset: code fences, tables, bullets, paragraphs, `code`, links."""
    import re
    def inline(t):
        t = html.escape(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    out, i, L = [], 0, md.splitlines()
    while i < len(L):
        ln = L[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(L) and not L[j].startswith("```"):
                j += 1
            out.append("<pre>" + html.escape("\n".join(L[i + 1:j])) + "</pre>")
            i = j + 1
        elif ln.startswith("|"):
            rows = []
            while i < len(L) and L[i].startswith("|"):
                cells = [c.strip() for c in L[i].strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            out.append("<div style='overflow-x:auto'><table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</table></div>")
        elif ln.lstrip().startswith(("- ", "* ")):
            items = []
            while i < len(L) and L[i].lstrip().startswith(("- ", "* ")):
                items.append(inline(L[i].lstrip()[2:]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
        elif ln.strip():
            para = []
            while i < len(L) and L[i].strip() and not L[i].startswith(("```", "|", "- ", "* ", "#")):
                para.append(L[i].strip())
                i += 1
            if para:
                out.append(f"<p>{inline(' '.join(para))}</p>")
            else:
                i += 1
        else:
            i += 1
    return "".join(out)


def plugin_page(e):
    d = ROOT / "plugins" / e["slug"]
    m = json.loads((d / ".claude-plugin" / "plugin.json").read_text())
    readme = (d / "README.md").read_text()
    slug, repo = e["slug"], f"https://github.com/{OWNER}/{e['repo']}"
    utm = f"utm_source=site&utm_campaign={slug}"
    affil = [ln for ln in readme.splitlines() if ln.startswith("Not affiliated")]
    cowork = e["surface"] == "cowork"
    install = f"""<h2>Install</h2>
{"<p><strong>Claude Cowork or claude.ai:</strong> download the plugin file and install it.</p>" if cowork else ""}
{f'<p><a class="btn" data-track="download_plugin" data-plugin="{slug}" href="{repo}/releases/latest?{utm}">Download {html.escape(m["displayName"])}</a></p>' if cowork else ""}
<p><strong>Claude Code:</strong></p>
<pre data-track="copy_install" data-plugin="{slug}">/plugin marketplace add {OWNER}/{REG['marketplace']}
/plugin install {slug}@{REG['marketplace']}</pre>"""
    try_it = md_section(readme, "Try it")
    what = md_section(readme, "What it does")
    privacy = md_section(readme, "Privacy")
    body = f"""<p><a href="../index.html">All plugins</a></p>
<span class="chip">For {html.escape(e['audience'])}</span>
<h1>{html.escape(m['displayName'])}</h1><p class="lead">{html.escape(m['description'])}</p>
{install}
{"<h2>Try it in 60 seconds</h2>" + md_html(try_it) if try_it else ""}
{"<h2>What it does</h2>" + md_html(what) if what else ""}
{"<h2>Privacy</h2>" + md_html(privacy) if privacy else ""}
<h2>Open source</h2><p>MIT licensed, with its design brief and eval suite:
<a data-track="view_source" data-plugin="{slug}" href="{repo}?{utm}">{repo.replace("https://", "")}</a>.
Ideas or problems? Open an issue there, or ask the plugin's request skill to draft one for you.</p>
<p class="lead" style="font-size:14px">{html.escape(" ".join(affil))}</p>"""
    return page(m["displayName"], m["description"], body, name=slug)


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
<a href="p/{e['slug']}.html" data-track="open_plugin_page" data-plugin="{e['slug']}">Details and install</a></div>""")
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
    fields = """<input name="email" type="email" required placeholder="you@business.com" aria-label="Email">
<input name="role" placeholder="What you do (e.g. property manager)" aria-label="Role">
<textarea name="task" rows="3" placeholder="The task you repeat every week" aria-label="Task"></textarea>"""
    if ENDPOINT:
        form = f"""<form method="post" action="{html.escape(ENDPOINT)}">
<input type="hidden" name="list" value="built-for-you">{fields}
<button class="btn" type="submit">Join the waitlist</button></form>"""
    elif POSTHOG_KEY:
        form = f"""<form id="wl">{fields}
<button class="btn" type="submit">Join the waitlist</button>
<p style="font-size:13px;color:var(--mute);margin:0">We store what you type here to contact you about this service, nothing else.</p></form>
<p class="thanks" id="wl-thanks">Thanks, you're on the list. We'll email you before anything is built.</p>
<script>
document.getElementById("wl").addEventListener("submit", function (e) {{
  e.preventDefault();
  var f = new FormData(e.target);
  posthog.capture("waitlist_signup", {{list: "built-for-you", email: f.get("email"), role: f.get("role"), task: f.get("task")}});
  e.target.style.display = "none";
  document.getElementById("wl-thanks").style.display = "block";
}});
</script>"""
    else:
        form = ("<p><a class='btn' data-track='waitlist_email' href=\"mailto:brian@press-start-studios.com?subject=Built-for-you%20plugin%20waitlist"
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
    return page("Built For You", "Turn your own examples into a one-click Claude assistant.", body, name="built-for-you")


if __name__ == "__main__":
    site = ROOT / "docs"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(index())
    (site / "built-for-you.html").write_text(built_for_you())
    (site / "p").mkdir(exist_ok=True)
    for e in REG["plugins"]:
        if (ROOT / "plugins" / e["slug"] / ".claude-plugin" / "plugin.json").exists():
            (site / "p" / f"{e['slug']}.html").write_text(plugin_page(e))
    print("wrote docs/ (index, built-for-you, p/<slug>); analytics "
          + ("on (PostHog)" if POSTHOG_KEY else "off")
          + "; waitlist via " + ("endpoint" if ENDPOINT else "PostHog" if POSTHOG_KEY else "email"))
