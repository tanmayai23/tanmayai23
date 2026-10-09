"""Generates the theme-aware animated SVGs used by the profile README.

Every asset is written twice (name-dark.svg / name-light.svg) and the README
picks one with <picture> + prefers-color-scheme, which follows the viewer's
GitHub theme.

Run:  python tools/build_assets.py
"""
import base64
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

DARK = dict(bg="#0D1117", card="#161B22", line="#30363D", text="#E6EDF3", soft="#C9D1D9",
            muted="#8B949E", teal="#2DD4BF", cyan="#38BDF8", violet="#A78BFA", amber="#FBBF24",
            pink="#F472B6", green="#3FB950", glow=".20", chip=".10")
LIGHT = dict(bg="#FFFFFF", card="#F6F8FA", line="#D0D7DE", text="#1F2328", soft="#31373D",
             muted="#59636E", teal="#0F766E", cyan="#0369A1", violet="#6D28D9", amber="#B45309",
             pink="#BE185D", green="#1A7F37", glow=".10", chip=".07")

SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', SFMono-Regular, Consolas, 'Courier New', monospace"

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .rise {{ animation: rise .9s cubic-bezier(.2,.7,.2,1) both; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .ping {{ animation: ping 2s cubic-bezier(0,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes ping {{ 0% {{ opacity: .8; transform: scale(1); }} 80%,100% {{ opacity: 0; transform: scale(2.8); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def e(s):
    return escape(str(s), quote=True)


def d(s):
    return f' style="animation-delay:{s:.2f}s"'


def mono_w(text, size):
    return len(text) * size * 0.6


def svg(w, h, body, css="", defs="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}">\n<title>{e(label)}</title>\n'
            f'<style>{BASE_CSS}{css}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  assets/{name}")


def chip(T, x, y, text, color, size=12.5, h=28):
    w = mono_w(text, size) + 24
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{color}" '
            f'fill-opacity="{T["chip"]}" stroke="{color}" stroke-opacity=".35"/>'
            f'<text x="{x + w/2:.1f}" y="{y + h/2 + size*.36:.1f}" text-anchor="middle" class="mono" '
            f'font-size="{size}" font-weight="600" fill="{color}">{e(text)}</text>'), w


def label(T, x, y, text, color):
    return (f'<circle cx="{x+4}" cy="{y-4}" r="4" fill="{color}"/>'
            f'<text x="{x+16}" y="{y}" class="mono" font-size="12" font-weight="600" letter-spacing="2.2" '
            f'fill="{T["muted"]}">{e(text)}</text>')


def tile(T, x, y, w, h, inner, delay=0.0):
    return (f'<g class="rise"{d(delay)}><rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="20" '
            f'fill="{T["card"]}" stroke="{T["line"]}"/>{inner}</g>')


# ================================================================== HERO
PHOTO = base64.b64encode((ROOT / "avatar.jpg").read_bytes()).decode()
WORDS = ["AI products that ship.", "voice assistants.", "RAG systems.", "vision models.", "an AI startup."]


def hero(T):
    W, H = 1200, 400
    PX, PY, PR = 1000, 200, 118
    n = len(WORDS)
    cyc = 2.4
    words = "".join(
        f'<text x="186" y="246" class="sans w w{i}" font-size="36" font-weight="800" letter-spacing="-.5" '
        f'fill="url(#acc)"{d(i*cyc)}>{e(wd)}</text>' for i, wd in enumerate(WORDS))
    seg = 100 / n

    def orbit(r, dots, cls, dash):
        pts = "".join(f'<circle cx="{PX + r*math.cos(math.radians(a)):.1f}" cy="{PY + r*math.sin(math.radians(a)):.1f}" '
                      f'r="{s}" fill="{T[c]}"/>' for a, c, s in dots)
        return (f'<g class="{cls}"><circle cx="{PX}" cy="{PY}" r="{r}" fill="none" stroke="{T["muted"]}" '
                f'stroke-opacity=".35" stroke-dasharray="{dash}"/>{pts}</g>')

    chips, cx = [], 64
    for t, c in [("LLMs", "teal"), ("RAG", "cyan"), ("Voice AI", "violet"), ("Computer Vision", "pink"), ("Agents", "amber")]:
        s, w = chip(T, cx, 312, t, T[c], size=12.5, h=30)
        chips.append(s)
        cx += w + 10

    css = f"""
  .w {{ opacity: 0; animation: cyc {n*cyc}s ease-in-out infinite; }}
  @keyframes cyc {{ 0% {{ opacity: 0; transform: translateY(14px); }} {seg*.12:.1f}%, {seg*.85:.1f}% {{ opacity: 1; transform: none; }}
                   {seg:.1f}%, 100% {{ opacity: 0; transform: translateY(-14px); }} }}
  .spinR {{ animation: spin 40s linear infinite; transform-box: view-box; transform-origin: {PX}px {PY}px; }}
  .spinL {{ animation: spin 60s linear infinite reverse; transform-box: view-box; transform-origin: {PX}px {PY}px; }}
  .fast {{ animation-duration: 7s; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .drift {{ animation: drift 14s ease-in-out infinite; }}
  @keyframes drift {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(-40px,24px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .w0 {{ opacity: 1; }} }}
"""
    defs = f"""
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  <clipPath id="face"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>
  <radialGradient id="gA"><stop offset="0" stop-color="{T['teal']}" stop-opacity="{T['glow']}"/><stop offset="1" stop-color="{T['teal']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gB"><stop offset="0" stop-color="{T['violet']}" stop-opacity="{T['glow']}"/><stop offset="1" stop-color="{T['violet']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{T['teal']}"/><stop offset=".55" stop-color="{T['cyan']}"/><stop offset="1" stop-color="{T['violet']}"/></linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T['teal']}"/><stop offset=".5" stop-color="{T['cyan']}" stop-opacity=".15"/><stop offset="1" stop-color="{T['violet']}"/></linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{T['muted']}" fill-opacity=".18"/></pattern>
"""
    body = f"""
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{T['bg']}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <circle cx="{PX}" cy="{PY}" r="300" fill="url(#gA)" class="drift"/>
  <circle cx="120" cy="420" r="320" fill="url(#gB)" class="drift"{d(-7)}/>
  {orbit(170, [(-60, 'teal', 6), (75, 'violet', 5), (200, 'amber', 5.5)], 'spinR', '3 8')}
  {orbit(145, [(20, 'cyan', 4), (150, 'pink', 4.5), (265, 'green', 3.5)], 'spinL', '1 6')}
  <circle cx="{PX}" cy="{PY}" r="{PR+9}" fill="none" stroke="url(#ring)" stroke-width="3.5" class="spinR fast"/>
  <circle cx="{PX}" cy="{PY}" r="{PR+2}" fill="{T['bg']}"/>
  <image x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}" href="data:image/jpeg;base64,{PHOTO}" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.5" fill="none" stroke="{T['line']}" stroke-width="1.5"/>

<g class="rise"{d(.05)}>
  <rect x="64" y="52" width="232" height="30" rx="15" fill="{T['green']}" fill-opacity="{T['chip']}" stroke="{T['green']}" stroke-opacity=".4"/>
  <circle cx="84" cy="67" r="4.5" fill="{T['green']}" class="ping"/><circle cx="84" cy="67" r="4.5" fill="{T['green']}"/>
  <text x="98" y="72" class="sans" font-size="14" font-weight="600" fill="{T['green']}">Open to AI/ML internships</text>
</g>
<g class="rise"{d(.2)}>
  <text x="60" y="172" class="sans" font-size="84" font-weight="800" letter-spacing="-3" fill="{T['text']}">Tanmay <tspan fill="url(#acc)">Kala</tspan></text>
</g>
<g class="rise"{d(.4)}>
  <text x="64" y="246" class="sans" font-size="36" font-weight="300" letter-spacing="-.5" fill="{T['soft']}">I build</text>
</g>
<g{d(.4)}>{words}</g>
<g class="rise"{d(.6)}>
  <text x="64" y="288" class="sans" font-size="18" fill="{T['muted']}">Generative AI &amp; NLP Engineer  ·  Founder @ <tspan fill="{T['text']}" font-weight="700">Naxatra AI</tspan>  ·  VIT Bhopal</text>
</g>
<g class="rise"{d(.8)}>{''.join(chips)}</g>
"""
    return svg(W, H, body, css, defs, "Tanmay Kala — I build AI products that ship")


# ================================================================= BENTO
def bento(T):
    W, G, R = 1200, 16, 200
    cw = (W - 3 * G) / 4
    H = 2 * R + G
    parts = []

    # A — shipped (2 wide)
    chips, cx = [], 28
    for t, c in [("SwachhVan", "teal"), ("Hey Dude", "violet"), ("Travel Assist", "pink"),
                 ("Whisper", "green"), ("VibeHub", "cyan")]:
        s, w = chip(T, cx, 146, t, T[c], size=12)
        chips.append(s)
        cx += w + 8
    parts.append(tile(T, 0, 0, 2*cw + G, R, f"""
  {label(T, 28, 40, 'SHIPPED', T['teal'])}
  <text x="24" y="122" class="sans" font-size="84" font-weight="800" letter-spacing="-4" fill="url(#acc)">5+</text>
  <text x="150" y="92" class="sans" font-size="24" font-weight="700" fill="{T['text']}">AI products, live on the web</text>
  <text x="150" y="118" class="sans" font-size="15" fill="{T['muted']}">idea → model → deployed product, end to end</text>
  {''.join(chips)}""", .05))

    # B — hackathon
    x = 2 * (cw + G)
    parts.append(tile(T, x, 0, cw, R, f"""
  {label(T, x+28, 40, 'HACKATHON', T['cyan'])}
  <text x="{x+26}" y="112" class="sans" font-size="54" font-weight="800" letter-spacing="-2" fill="{T['cyan']}">Top 25</text>
  <text x="{x+28}" y="142" class="sans" font-size="17" font-weight="600" fill="{T['text']}">of 400+ teams</text>
  <text x="{x+28}" y="166" class="sans" font-size="13.5" fill="{T['muted']}">Hack For Green Bharat · SwachhVan</text>""", .15))

    # C — stack (tall)
    x = 3 * (cw + G)
    stack = [("Python", "teal"), ("PyTorch", "pink"), ("LLMs", "violet"), ("RAG", "cyan"),
             ("Gemini", "cyan"), ("LangGraph", "teal"), ("Hugging Face", "amber"), ("OpenCV", "green"),
             ("Whisper", "violet"), ("FastAPI", "teal"), ("TypeScript", "cyan"), ("Docker", "cyan"),
             ("scikit-learn", "amber"), ("Transformers", "violet"), ("Gradio", "amber"), ("Streamlit", "pink"),
             ("SQL", "green"), ("OCI", "pink"), ("AWS", "amber"), ("GCP", "cyan")]
    chips, cx, cy = [], x + 24, 66
    for t, c in stack:
        w = mono_w(t, 12) + 24
        if cx + w > x + cw - 20:
            cx, cy = x + 24, cy + 38
        s, w = chip(T, cx, cy, t, T[c], size=12)
        chips.append(s)
        cx += w + 8
    parts.append(tile(T, x, 0, cw, H, f"""
  {label(T, x+28, 40, 'STACK', T['violet'])}
  {''.join(chips)}
  <text x="{x+28}" y="{H-28}" class="mono" font-size="12" fill="{T['muted']}">+ always learning<tspan class="blink" fill="{T['violet']}">_</tspan></text>""", .25))

    # D — accuracy
    y = R + G
    parts.append(tile(T, 0, y, cw, R, f"""
  {label(T, 28, y+40, 'DEEP LEARNING', T['pink'])}
  <text x="26" y="{y+112}" class="sans" font-size="54" font-weight="800" letter-spacing="-2" fill="{T['pink']}">96.82%</text>
  <text x="28" y="{y+142}" class="sans" font-size="17" font-weight="600" fill="{T['text']}">test accuracy</text>
  <text x="28" y="{y+166}" class="sans" font-size="13.5" fill="{T['muted']}">43-class CNN built from scratch</text>""", .35))

    # E — now (2 wide)
    x = cw + G
    rows = [("Building Naxatra AI", "AI products for civic & student problems", "teal"),
            ("Shipping voice agents", "LangGraph + CALL-E · 421 tests passing", "violet"),
            ("Certified by Oracle", "OCI 2025 Generative AI Professional", "amber")]
    lines = "".join(
        f'<rect x="{x+28}" y="{y+62 + i*42}" width="4" height="30" rx="2" fill="{T[c]}"/>'
        f'<text x="{x+46}" y="{y+76 + i*42}" class="sans" font-size="16" font-weight="700" fill="{T["text"]}">{e(a)}</text>'
        f'<text x="{x+46}" y="{y+94 + i*42}" class="sans" font-size="13.5" fill="{T["muted"]}">{e(b)}</text>'
        for i, (a, b, c) in enumerate(rows))
    parts.append(tile(T, x, y, 2*cw + G, R, f"""
  <circle cx="{x+32}" cy="{y+36}" r="4" fill="{T['green']}" class="ping"/>
  {label(T, x+28, y+40, 'RIGHT NOW', T['green'])}
  {lines}""", .45))

    defs = (f'<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{T["teal"]}"/>'
            f'<stop offset="1" stop-color="{T["violet"]}"/></linearGradient>')
    return svg(W, H, "\n".join(parts), "", defs, "Highlights: 5+ AI products, Top 25 of 400+ teams, 96.82% accuracy")


# ================================================================= CARDS
PROJECTS = [
    dict(slug="swachhvan", tag="FLAGSHIP · LIVE", color="teal", title="SwachhVan",
         desc="AI demand forecasting for mobile sanitation vans", metric="Top 25", mlabel="of 400+ teams",
         chips=["TypeScript", "Forecasting", "GPS", "Vercel"]),
    dict(slug="heydude", tag="VOICE AI · LIVE", color="violet", title="Hey Dude",
         desc="Voice assistant with face-auth, Gemini & WhatsApp control", metric="15 days",
         mlabel="zero → production", chips=["Python", "Gemini", "OpenCV", "SQLite"]),
    dict(slug="marketbuddy", tag="AGENTIC AI", color="amber", title="Market Buddy",
         desc="Voice agent that turns supplier calls into commitments", metric="421",
         mlabel="tests passing", chips=["Next.js", "LangGraph", "CALL-E", "TypeScript"]),
    dict(slug="gtsrb", tag="DEEP LEARNING", color="pink", title="TrafficSignNet",
         desc="43-class traffic-sign CNN written from scratch in PyTorch", metric="96.82%",
         mlabel="test accuracy", chips=["PyTorch", "CNN", "CLI", "Tested"]),
]


def card(T, i, p):
    W, H = 592, 220
    c = T[p["color"]]
    chips, cx = [], 28
    for t in p["chips"]:
        s, w = chip(T, cx, 166, t, c, size=12)
        chips.append(s)
        cx += w + 8
    css = f"""
  .shine {{ animation: shine 8s ease-in-out {i*1.3:.1f}s infinite; }}
  @keyframes shine {{ 0% {{ transform: translateX(-200px) skewX(-20deg); }} 30%,100% {{ transform: translateX(800px) skewX(-20deg); }} }}
"""
    defs = f"""
  <clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  <radialGradient id="glow" cx="1" cy="0" r="1"><stop offset="0" stop-color="{c}" stop-opacity="{T['glow']}"/><stop offset=".7" stop-color="{c}" stop-opacity="0"/></radialGradient>
  <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{c}" stop-opacity="0"/><stop offset=".5" stop-color="{c}" stop-opacity=".07"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>
"""
    body = f"""
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{T['card']}"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  <rect width="120" height="{H}" fill="url(#sh)" class="shine"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="19.5" fill="none" stroke="{T['line']}"/>
<g class="rise">
  {label(T, 28, 42, p['tag'], c)}
  <text x="26" y="96" class="sans" font-size="32" font-weight="800" letter-spacing="-1" fill="{T['text']}">{e(p['title'])}</text>
  <text x="28" y="130" class="sans" font-size="15" fill="{T['muted']}">{e(p['desc'])}</text>
  <text x="{W-28}" y="72" text-anchor="end" class="sans" font-size="38" font-weight="800" letter-spacing="-1.5" fill="{c}">{e(p['metric'])}</text>
  <text x="{W-28}" y="94" text-anchor="end" class="sans" font-size="13" fill="{T['muted']}">{e(p['mlabel'])}</text>
</g>
<g class="rise"{d(.2)}>{''.join(chips)}
  <text x="{W-28}" y="186" text-anchor="end" class="mono" font-size="18" fill="{c}">↗</text>
</g>
"""
    return svg(W, H, body, css, defs, p["title"])


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    print("Building assets:")
    for mode, T in (("dark", DARK), ("light", LIGHT)):
        write(f"hero-{mode}.svg", hero(T))
        write(f"bento-{mode}.svg", bento(T))
        for i, p in enumerate(PROJECTS):
            write(f"card-{p['slug']}-{mode}.svg", card(T, i, p))
