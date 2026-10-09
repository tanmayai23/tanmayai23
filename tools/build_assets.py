"""Generates the "TanmayGPT" chat-style profile README assets.

Every asset is written twice (name-dark.svg / name-light.svg); the README picks
one with <picture> + prefers-color-scheme, which follows the viewer's GitHub theme.

Run:  python tools/build_assets.py
The commit heatmap pulls live data from the GitHub GraphQL API using
$GITHUB_TOKEN (or `gh auth token`); it falls back to tools/contributions.json.
Edit CHAT_TOP / CHAT_MORE / CHAT_END / PROJECTS below and re-run.
"""
import base64
import json
import os
import subprocess
import urllib.request
from datetime import date, timedelta
from html import escape
from pathlib import Path

USER = "tanmayai23"
ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
ICONS = ROOT / "icons"
OUT.mkdir(exist_ok=True)
ICONS.mkdir(exist_ok=True)

DARK = dict(name="dark", bg="#0D1117", card="#161B22", line="#30363D", text="#E6EDF3", soft="#C9D1D9",
            muted="#8B949E", teal="#2DD4BF", cyan="#38BDF8", violet="#A78BFA", amber="#FBBF24",
            pink="#F472B6", green="#3FB950", glow=".18", chip=".10",
            u1="#2DD4BF", u2="#38BDF8", utext="#04221F",
            heat=["#1F2630", "#0E4D45", "#0F766E", "#14B8A6", "#5EEAD4"])
LIGHT = dict(name="light", bg="#FFFFFF", card="#F6F8FA", line="#D0D7DE", text="#1F2328", soft="#31373D",
             muted="#59636E", teal="#0F766E", cyan="#0369A1", violet="#6D28D9", amber="#B45309",
             pink="#BE185D", green="#1A7F37", glow=".09", chip=".07",
             u1="#0F766E", u2="#0369A1", utext="#FFFFFF",
             heat=["#EBEDF0", "#99F6E4", "#2DD4BF", "#0D9488", "#115E59"])

SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', SFMono-Regular, Consolas, 'Courier New', monospace"

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .pop {{ animation: pop .45s cubic-bezier(.2,.8,.2,1.2) both; transform-box: fill-box; }}
  .popL {{ transform-origin: left bottom; }}
  .popR {{ transform-origin: right bottom; }}
  .typing {{ opacity: 0; animation: show .7s linear; }}
  .dot {{ animation: bounce 1s ease-in-out infinite; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .twinkle {{ animation: twinkle 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes pop {{ from {{ opacity: 0; transform: translateY(12px) scale(.94); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes show {{ 0%,100% {{ opacity: 1; }} }}
  @keyframes bounce {{ 0%,60%,100% {{ transform: translateY(0); opacity: .45; }} 30% {{ transform: translateY(-5px); opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .2; transform: scale(.6); }} 50% {{ opacity: 1; transform: scale(1.1); }} }}
  @media (prefers-reduced-motion: reduce) {{ .pop, .dot, .blink, .twinkle {{ animation: none !important; }} }}
"""

PHOTO = base64.b64encode((ROOT / "avatar.jpg").read_bytes()).decode()
W, PAD, FS, LH = 1000, 36, 19, 30   # canvas width, side padding, message font size, line height
BX = PAD + 54                       # AI bubble left edge
BW = W - BX - PAD                   # widest AI bubble


def e(s):
    return escape(str(s), quote=True)


def dl(s):
    return f' style="animation-delay:{s:.2f}s"'


def sans_w(text, size):
    return len(text) * size * 0.53


def mono_w(text, size):
    return len(text) * size * 0.6


def bubble(x, y, w, h, r=20, tl=None, br=None, **attrs):
    """Rounded rect path with an optional tighter top-left / bottom-right corner (chat tail)."""
    tl = r if tl is None else tl
    br = r if br is None else br
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return (f'<path d="M{x+tl},{y} H{x+w-r} Q{x+w},{y} {x+w},{y+r} V{y+h-br} Q{x+w},{y+h} {x+w-br},{y+h} '
            f'H{x+r} Q{x},{y+h} {x},{y+h-r} V{y+tl} Q{x},{y} {x+tl},{y} Z" {a}/>')


def ai_bubble(T, w, h, y):
    return bubble(BX, y, w, h, tl=6, fill=T["card"], stroke=T["line"])


def photo(x, y, size):
    return f'<use href="#av" x="{x}" y="{y}" width="{size}" height="{size}"/>'


def chip(T, x, y, text, color, size=12.5, h=30):
    w = mono_w(text, size) + 24
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{T[color]}" '
            f'fill-opacity="{T["chip"]}" stroke="{T[color]}" stroke-opacity=".35"/>'
            f'<text x="{x + w/2:.1f}" y="{y + h/2 + size*.36:.1f}" text-anchor="middle" class="mono" '
            f'font-size="{size}" font-weight="600" fill="{T[color]}">{e(text)}</text>'), w


# ------------------------------------------------------------ live data
def icon_uri(name, theme):
    f = ICONS / f"{name}-{theme}.svg"
    if not f.exists():
        url = f"https://skillicons.dev/icons?i={name}&theme={theme}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-builder)"})
        f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()


def github_token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def contributions():
    cache = ROOT / "contributions.json"
    q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{'
         'totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}')
    tok = github_token()
    if tok:
        try:
            req = urllib.request.Request("https://api.github.com/graphql",
                                         data=json.dumps({"query": q, "variables": {"u": USER}}).encode(),
                                         headers={"Authorization": f"bearer {tok}", "Content-Type": "application/json"})
            cal = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            cache.write_text(json.dumps(cal), encoding="utf-8")
            return cal
        except Exception as ex:  # network / auth problems -> fall back to cache
            print("  ! contribution fetch failed, using cache:", ex)
    return json.loads(cache.read_text(encoding="utf-8"))


def streaks(days):
    counts = [dd["contributionCount"] for dd in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:      # today not committed yet doesn't break the streak
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    return cur, longest, sum(1 for c in counts if c)


# ----------------------------------------------------------------- content
CHAT_TOP = [
    ("user", "Who is Tanmay?"),
    ("ai", "text", [
        [("Tanmay Kala", "text", True), (" — founder of ", "soft", False), ("Naxatra AI", "teal", True)],
        [("and a Generative AI & NLP engineer.", "soft", False)],
        [("B.Tech CSE (AI & ML) @ VIT Bhopal, class of '28.", "soft", False)],
        [("He doesn't stop at demos. He ships AI products.", "text", True)],
    ]),
    ("user", "Impressive. Any proof?"),
    ("ai", "stats", "Here are the receipts:", [
        ("5+", "AI products live", "teal"), ("Top 25", "of 400+ teams", "cyan"),
        ("96.82%", "CNN accuracy", "pink"), ("421", "tests passing", "amber"),
    ]),
    ("user", "But is he founder material?"),
    ("ai", "text", [
        [("Naxatra AI", "teal", True), (" — AI products for problems India actually has.", "soft", False)],
        [("▸ ", "amber", True), ("Ships fast: ", "text", True), ("Hey Dude went zero → production in 15 days", "soft", False)],
        [("▸ ", "violet", True), ("Leads: ", "text", True), ("sole AI engineer in a 6-member team", "soft", False)],
        [("▸ ", "pink", True), ("Builds in public: ", "text", True), ("21 posts · 538+ avg impressions", "soft", False)],
        [("▸ ", "cyan", True), ("Picks real problems: ", "text", True), ("sanitation, campus life, travel", "soft", False)],
    ]),
    ("user", "Show me his best work."),
    ("ai", "text", [[("Tap any card below ", "soft", False), ("↓", "teal", True)]]),
]

TROPHIES = [
    ("Top 25 / 400+", "Hack For Green Bharat", "amber"),
    ("Codefest '25", "Placed · VibeHub", "cyan"),
    ("OCI GenAI Pro", "Oracle certified · 2025", "teal"),
    ("OCI AI Foundations", "Oracle certified · 2025", "violet"),
    ("96.82% accuracy", "TrafficSignNet CNN", "pink"),
    ("15-day sprint", "Hey Dude: idea → prod", "green"),
]

STACK = [
    ("AI / ML", ["py", "pytorch", "tensorflow", "sklearn", "opencv"],
     [("LLMs", "teal"), ("RAG", "cyan"), ("LangGraph", "violet"), ("Hugging Face", "amber"), ("Gemini", "cyan"), ("Whisper", "pink")]),
    ("BUILD", ["ts", "js", "nextjs", "fastapi", "flask", "cpp", "c"], []),
    ("SHIP", ["docker", "aws", "gcp", "vercel", "git", "github", "mysql", "sqlite"], []),
]

CHAT_MORE = [
    ("user", "Any trophies?"),
    ("ai", "trophies", "His trophy case:"),
    ("user", "What's his stack?"),
    ("ai", "stack", "His daily drivers:"),
    ("user", "Does he actually code consistently?"),
    ("ai", "commits", "Here's his commit history for the last 12 months:"),
]

CHAT_END = [
    ("user", "Okay, I'm convinced. How do we connect?"),
    ("ai", "text", [
        [("He's ", "soft", False), ("open to AI/ML & GenAI internships", "green", True)],
        [("and to building with anyone solving something real.", "soft", False)],
        [("Pick a channel below and say hi! ", "soft", False), ("↓", "teal", True)],
    ]),
]


# --------------------------------------------------------- AI renderers
LINE_T = .42


def r_text(T, m, y, t, defs):
    lines = m[2]
    lw = max(sum(sans_w(s, FS) for s, _, _ in ln) for ln in lines)
    w, h = lw + 48, len(lines) * LH + 26
    body = [ai_bubble(T, w, h, y)]
    for i, ln in enumerate(lines):
        cid = f"tw{len(defs)}"
        ly = y + 13 + (i + 1) * LH - 8
        full = sum(sans_w(s, FS) for s, _, _ in ln) + 30
        defs.append(f'<clipPath id="{cid}"><rect x="{BX+16}" y="{ly-FS-2}" width="0" height="{FS+10}">'
                    f'<animate attributeName="width" from="0" to="{full:.0f}" begin="{t + i*LINE_T:.2f}s" '
                    f'dur="{LINE_T:.2f}s" fill="freeze"/></rect></clipPath>')
        spans = "".join(f'<tspan fill="{T[c]}"{" font-weight=\"700\"" if b else ""}>{e(s)}</tspan>' for s, c, b in ln)
        body.append(f'<text x="{BX+24}" y="{ly}" class="sans" font-size="{FS}" xml:space="preserve" clip-path="url({chr(35)}{cid})">{spans}</text>')
    return [f'<g class="pop popL"{dl(t)}>{"".join(body)}</g>'], h, t + len(lines) * LINE_T


def intro(T, y, text):
    return f'<text x="{BX+24}" y="{y+40}" class="sans" font-size="{FS}" fill="{T["soft"]}">{e(text)}</text>'


def r_stats(T, m, y, t, defs):
    stats = m[3]
    tw, gap = 172, 12
    w = 48 + len(stats) * tw + (len(stats) - 1) * gap
    h = 168
    out = [f'<g class="pop popL"{dl(t)}>{ai_bubble(T, w, h, y)}{intro(T, y, m[2])}</g>']
    for i, (val, lab, c) in enumerate(stats):
        tx = BX + 24 + i * (tw + gap)
        out.append(f'<g class="pop popL"{dl(t + .25 + i*.18)}>'
                   f'<rect x="{tx}" y="{y+60}" width="{tw}" height="88" rx="14" fill="{T[c]}" fill-opacity="{T["chip"]}" stroke="{T[c]}" stroke-opacity=".35"/>'
                   f'<text x="{tx+16}" y="{y+100}" class="sans" font-size="30" font-weight="800" letter-spacing="-1" fill="{T[c]}">{e(val)}</text>'
                   f'<text x="{tx+16}" y="{y+128}" class="sans" font-size="14.5" fill="{T["soft"]}">{e(lab)}</text></g>')
    return out, h, t + .25 + len(stats) * .18


def cup(T, x, y, c, gid):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T[c]}"/>'
            f'<stop offset="1" stop-color="{T[c]}" stop-opacity=".55"/></linearGradient>',
            f'<path d="M{x+10},{y+9} H{x+4} Q{x+3},{y+19} {x+12},{y+21}" fill="none" stroke="{T[c]}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="M{x+34},{y+9} H{x+40} Q{x+41},{y+19} {x+32},{y+21}" fill="none" stroke="{T[c]}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="M{x+9},{y+4} H{x+35} V{y+16} Q{x+35},{y+29} {x+22},{y+29} Q{x+9},{y+29} {x+9},{y+16} Z" fill="url(#{gid})"/>'
            f'<path d="M{x+15},{y+9} V{y+16} Q{x+15},{y+21} {x+19},{y+23}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/>'
            f'<rect x="{x+19.5}" y="{y+29}" width="5" height="7" fill="{T[c]}"/>'
            f'<rect x="{x+13}" y="{y+36}" width="18" height="5" rx="2" fill="{T[c]}"/>'
            f'<path d="M{x+41},{y-1} l1.6,3.6 3.6,1.6 -3.6,1.6 -1.6,3.6 -1.6,-3.6 -3.6,-1.6 3.6,-1.6 Z" fill="{T[c]}" class="twinkle"/>')


def r_trophies(T, m, y, t, defs):
    cols, gap, th = 3, 12, 84
    tw = (BW - 48 - (cols - 1) * gap) / cols
    rows = (len(TROPHIES) + cols - 1) // cols
    h = 62 + rows * th + (rows - 1) * gap + 22
    out = [f'<g class="pop popL"{dl(t)}>{ai_bubble(T, BW, h, y)}{intro(T, y, m[2])}</g>']
    for i, (title, sub, c) in enumerate(TROPHIES):
        tx = BX + 24 + (i % cols) * (tw + gap)
        ty = y + 62 + (i // cols) * (th + gap)
        grad, icon = cup(T, tx + 16, ty + 20, c, f"cup{i}")
        defs.append(grad)
        out.append(f'<g class="pop popL"{dl(t + .25 + i*.15)}>'
                   f'<rect x="{tx:.1f}" y="{ty}" width="{tw:.1f}" height="{th}" rx="14" fill="{T[c]}" fill-opacity="{T["chip"]}" stroke="{T[c]}" stroke-opacity=".35"/>'
                   f'{icon}'
                   f'<text x="{tx+76:.1f}" y="{ty+38}" class="sans" font-size="16" font-weight="800" fill="{T["text"]}">{e(title)}</text>'
                   f'<text x="{tx+76:.1f}" y="{ty+60}" class="sans" font-size="13.5" fill="{T["muted"]}">{e(sub)}</text></g>')
    return out, h, t + .25 + len(TROPHIES) * .15


def r_stack(T, m, y, t, defs):
    IS, ig, rh = 46, 10, 92
    h = 62 + len(STACK) * rh + 4
    out = [f'<g class="pop popL"{dl(t)}>{ai_bubble(T, BW, h, y)}{intro(T, y, m[2])}</g>']
    k = 0
    for r, (lab, icons, chips) in enumerate(STACK):
        ry = y + 66 + r * rh
        out.append(f'<g class="pop popL"{dl(t + .2 + r*.2)}><text x="{BX+24}" y="{ry+12}" class="mono" font-size="11.5" '
                   f'font-weight="600" letter-spacing="2.2" fill="{T["muted"]}">{e(lab)}</text></g>')
        x = BX + 24
        for name in icons:
            out.append(f'<g class="pop"{dl(t + .3 + k*.05)}><image x="{x}" y="{ry+22}" width="{IS}" height="{IS}" '
                       f'href="{icon_uri(name, T["name"])}"/></g>')
            x += IS + ig
            k += 1
        x += 6
        for text, c in chips:
            s, cw = chip(T, x, ry + 30, text, c, size=12)
            out.append(f'<g class="pop"{dl(t + .3 + k*.05)}>{s}</g>')
            x += cw + 8
            k += 1
    return out, h, t + .3 + k * .05


def r_commits(T, m, y, t, defs):
    cal = contributions()
    weeks = cal["weeks"]
    days = [dd for wk in weeks for dd in wk["contributionDays"]]
    cur, longest, active = streaks(days)
    lvl = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    cs, cg = 11.5, 3.2
    gx, gy = BX + 24, y + 84
    out_cells, months, last_m = [], [], None
    for wi, wk in enumerate(weeks):
        cells = []
        for dd in wk["contributionDays"]:
            dow = date.fromisoformat(dd["date"]).isoweekday() % 7
            cells.append(f'<rect x="{gx + wi*(cs+cg):.1f}" y="{gy + dow*(cs+cg):.1f}" width="{cs}" height="{cs}" rx="2.5" '
                         f'fill="{T["heat"][lvl.get(dd["contributionLevel"], 0)]}"><title>{dd["contributionCount"]} on {dd["date"]}</title></rect>')
        out_cells.append(f'<g class="pop"{dl(t + .25 + wi*.018)}>{"".join(cells)}</g>')
        mth = date.fromisoformat(wk["contributionDays"][0]["date"]).strftime("%b")
        if mth != last_m and wi < len(weeks) - 2:
            months.append(f'<text x="{gx + wi*(cs+cg):.1f}" y="{gy-10}" class="sans" font-size="12" fill="{T["muted"]}">{mth}</text>')
            last_m = mth
    grid_w = len(weeks) * (cs + cg)
    legend_x = gx + grid_w - 5 * (cs + cg)
    legend = (f'<text x="{legend_x - 8}" y="{gy + 7*(cs+cg) + 16}" text-anchor="end" class="sans" font-size="11.5" fill="{T["muted"]}">less</text>'
              + "".join(f'<rect x="{legend_x + i*(cs+cg):.1f}" y="{gy + 7*(cs+cg) + 6}" width="{cs}" height="{cs}" rx="2.5" fill="{c}"/>' for i, c in enumerate(T["heat"]))
              + f'<text x="{legend_x + 5*(cs+cg) + 4}" y="{gy + 7*(cs+cg) + 16}" class="sans" font-size="11.5" fill="{T["muted"]}">more</text>')
    sy = gy + 7 * (cs + cg) + 34
    stats = [(f"{cal['totalContributions']}", "contributions", "teal"), (f"{cur} days", "current streak", "amber"),
             (f"{longest} days", "longest streak", "pink"), (f"{active}", "active days", "violet")]
    sw = (BW - 48 - 3 * 12) / 4
    st = "".join(
        f'<g class="pop popL"{dl(t + 1.3 + i*.15)}><rect x="{BX+24 + i*(sw+12):.1f}" y="{sy}" width="{sw:.1f}" height="70" rx="14" '
        f'fill="{T[c]}" fill-opacity="{T["chip"]}" stroke="{T[c]}" stroke-opacity=".35"/>'
        f'<text x="{BX+40 + i*(sw+12):.1f}" y="{sy+34}" class="sans" font-size="25" font-weight="800" letter-spacing="-.5" fill="{T[c]}">{e(v)}</text>'
        f'<text x="{BX+40 + i*(sw+12):.1f}" y="{sy+56}" class="sans" font-size="13.5" fill="{T["soft"]}">{e(lab)}</text></g>'
        for i, (v, lab, c) in enumerate(stats))
    h = sy + 70 + 24 - y
    out = [f'<g class="pop popL"{dl(t)}>{ai_bubble(T, BW, h, y)}{intro(T, y, m[2])}{"".join(months)}{legend}</g>']
    return out + out_cells + [st], h, t + 1.9


RENDER = {"text": r_text, "stats": r_stats, "trophies": r_trophies, "stack": r_stack, "commits": r_commits}


# ------------------------------------------------------------------ chat
def chat(T, msgs, header, composer, start=.3):
    items, defs = [], []
    y = (72 + 30) if header else 30
    t = start
    TYPE = .75

    for m in msgs:
        if m[0] == "user":
            w, h = sans_w(m[1], FS) + 44, 50
            x = W - PAD - w
            items.append(f'<g class="pop popR"{dl(t)}>' + bubble(x, y, w, h, br=6, fill="url(#ub)")
                         + f'<text x="{x+22}" y="{y+32}" class="sans" font-size="{FS}" font-weight="600" fill="{T["utext"]}">{e(m[1])}</text></g>')
            y += h + 18
            t += .55
            continue
        items.append(f'<g class="pop popL"{dl(t)}>{photo(PAD, y + 2, 40)}</g>')
        items.append(f'<g class="typing" style="animation-delay:{t:.2f}s;animation-duration:{TYPE}s">'
                     + bubble(BX, y, 76, 46, tl=6, fill=T["card"], stroke=T["line"])
                     + "".join(f'<circle cx="{BX+22+i*16}" cy="{y+23}" r="4.5" fill="{T["muted"]}" class="dot" style="animation-delay:{i*.15:.2f}s"/>' for i in range(3))
                     + '</g>')
        t += TYPE
        out, h, t = RENDER[m[1]](T, m, y, t, defs)
        items += out
        y += h + 24
        t += .45

    if composer:
        y += 4
        items.append(f'<g class="pop"{dl(t)}>'
                     f'<rect x="{PAD}" y="{y}" width="{W-2*PAD}" height="58" rx="29" fill="{T["card"]}" stroke="{T["line"]}"/>'
                     f'<text x="{PAD+28}" y="{y+36}" class="sans" font-size="17" fill="{T["muted"]}">Ask TanmayGPT anything<tspan class="blink" fill="{T["teal"]}"> |</tspan></text>'
                     f'<circle cx="{W-PAD-29}" cy="{y+29}" r="20" fill="url(#ub)"/>'
                     f'<path d="M{W-PAD-36},{y+30} L{W-PAD-29},{y+22} L{W-PAD-22},{y+30} M{W-PAD-29},{y+22} V{y+37}" stroke="{T["utext"]}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'</g>')
        y += 58

    H = int(y + 30)
    head = ""
    if header:
        head = (f'<rect width="{W}" height="72" fill="{T["card"]}"/>'
                f'<line x1="0" y1="72" x2="{W}" y2="72" stroke="{T["line"]}"/>'
                f'{photo(PAD-6, 14, 44)}'
                f'<circle cx="{PAD+33}" cy="52" r="6" fill="{T["green"]}" stroke="{T["card"]}" stroke-width="2.5"/>'
                f'<text x="{PAD+56}" y="34" class="sans" font-size="19" font-weight="800" fill="{T["text"]}">TanmayGPT</text>'
                f'<text x="{PAD+56}" y="55" class="sans" font-size="13.5" fill="{T["muted"]}"><tspan fill="{T["green"]}">● online</tspan>  ·  founder @ Naxatra AI  ·  trained on 2 years of shipping</text>'
                f'<rect x="{W-PAD-206}" y="22" width="206" height="28" rx="14" fill="{T["teal"]}" fill-opacity="{T["chip"]}" stroke="{T["teal"]}" stroke-opacity=".35"/>'
                f'<text x="{W-PAD-103}" y="41" text-anchor="middle" class="mono" font-size="12.5" fill="{T["teal"]}">model: tanmay-kala-v2</text>')
    defs_s = f"""
  <clipPath id="avc"><circle cx="20" cy="20" r="20"/></clipPath>
  <symbol id="av" viewBox="0 0 40 40" overflow="visible"><image width="40" height="40" href="data:image/jpeg;base64,{PHOTO}" clip-path="url(#avc)"/></symbol>
  <clipPath id="win"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="ub" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T['u1']}"/><stop offset="1" stop-color="{T['u2']}"/></linearGradient>
  <radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{T['teal']}" stop-opacity="{T['glow']}"/><stop offset=".6" stop-color="{T['teal']}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{T['muted']}" fill-opacity=".16"/></pattern>
  {''.join(defs)}
"""
    body = f"""
<g clip-path="url(#win)">
  <rect width="{W}" height="{H}" fill="{T['bg']}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect width="{W}" height="{H}" fill="url(#gl)"/>
  {head}
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="21.5" fill="none" stroke="{T['line']}" stroke-width="1.5"/>
{''.join(items)}
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Chat with TanmayGPT"><title>Chat with TanmayGPT</title><style>{BASE_CSS}</style>'
            f'<defs>{defs_s}</defs>{body}</svg>\n')


# ------------------------------------------------------------- link cards
PROJECTS = [
    dict(slug="swachhvan", ini="SV", color="teal", title="SwachhVan", tech="TypeScript · Forecasting · GPS",
         desc="AI demand forecasting for mobile sanitation vans", metric="Top 25", mlabel="of 400+ teams"),
    dict(slug="heydude", ini="HD", color="violet", title="Hey Dude", tech="Python · Gemini · OpenCV",
         desc="Voice assistant with face-auth & WhatsApp control", metric="15 days", mlabel="zero → production"),
    dict(slug="marketbuddy", ini="MB", color="amber", title="Market Buddy", tech="Next.js · LangGraph · CALL-E",
         desc="Voice agent that turns supplier calls into deals", metric="421", mlabel="tests passing"),
    dict(slug="gtsrb", ini="TS", color="pink", title="TrafficSignNet", tech="PyTorch · CNN · CLI",
         desc="43-class traffic-sign CNN built from scratch", metric="96.82%", mlabel="test accuracy"),
]


def card(T, i, p):
    CW, CH = 492, 156
    c = T[p["color"]]
    css = f"""
  .shine {{ animation: shine 8s ease-in-out {i*1.2:.1f}s infinite; }}
  @keyframes shine {{ 0% {{ transform: translateX(-160px) skewX(-20deg); }} 30%,100% {{ transform: translateX(700px) skewX(-20deg); }} }}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" role="img" aria-label="{e(p['title'])}">
<title>{e(p['title'])}</title><style>{BASE_CSS}{css}</style>
<defs>
  <clipPath id="c"><rect width="{CW}" height="{CH}" rx="18"/></clipPath>
  <linearGradient id="ic" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity=".65"/></linearGradient>
  <radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{c}" stop-opacity="{T['glow']}"/><stop offset=".7" stop-color="{c}" stop-opacity="0"/></radialGradient>
  <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{c}" stop-opacity="0"/><stop offset=".5" stop-color="{c}" stop-opacity=".08"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{CW}" height="{CH}" fill="{T['card']}"/>
  <rect width="{CW}" height="{CH}" fill="url(#gl)"/>
  <rect width="100" height="{CH}" fill="url(#sh)" class="shine"/>
  <rect width="4" height="{CH}" fill="{c}"/>
</g>
<rect x=".5" y=".5" width="{CW-1}" height="{CH-1}" rx="17.5" fill="none" stroke="{T['line']}"/>
<g class="pop popL">
  <rect x="24" y="24" width="54" height="54" rx="14" fill="url(#ic)"/>
  <text x="51" y="58" text-anchor="middle" class="sans" font-size="20" font-weight="800" fill="{T['bg']}">{e(p['ini'])}</text>
  <text x="94" y="48" class="sans" font-size="22" font-weight="800" letter-spacing="-.5" fill="{T['text']}">{e(p['title'])}</text>
  <text x="94" y="70" class="mono" font-size="12.5" fill="{T['muted']}">{e(p['tech'])}</text>
  <text x="{CW-24}" y="50" text-anchor="end" class="sans" font-size="27" font-weight="800" letter-spacing="-1" fill="{c}">{e(p['metric'])}</text>
  <text x="{CW-24}" y="70" text-anchor="end" class="sans" font-size="12.5" fill="{T['muted']}">{e(p['mlabel'])}</text>
  <line x1="24" y1="98" x2="{CW-24}" y2="98" stroke="{T['line']}"/>
  <text x="24" y="128" class="sans" font-size="15.5" fill="{T['soft']}">{e(p['desc'])}</text>
  <text x="{CW-24}" y="129" text-anchor="end" class="mono" font-size="17" font-weight="700" fill="{c}">↗</text>
</g>
</svg>
"""


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    print("Building assets:")
    for T in (DARK, LIGHT):
        mode = T["name"]
        files = [(f"chat-{mode}.svg", chat(T, CHAT_TOP, header=True, composer=False)),
                 (f"chat-more-{mode}.svg", chat(T, CHAT_MORE, header=False, composer=False)),
                 (f"chat-end-{mode}.svg", chat(T, CHAT_END, header=False, composer=True))]
        files += [(f"card-{p['slug']}-{mode}.svg", card(T, i, p)) for i, p in enumerate(PROJECTS)]
        for name, content in files:
            (OUT / name).write_text(content, encoding="utf-8")
            print(f"  assets/{name}")
