"""Generates every animated SVG used by the profile README.

Run:  python tools/build_assets.py
Edit the content blocks below (metrics, projects, timeline...) and re-run.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- palette
BG, PANEL, LINE = "#070B14", "#0C1220", "#1C2638"
TEXT, SOFT, MUTED = "#E6EDF3", "#C3CEDC", "#7D8AA0"
TEAL, CYAN, VIOLET, AMBER, PINK, GREEN = (
    "#5EEAD4", "#38BDF8", "#A78BFA", "#FBBF24", "#F472B6", "#4ADE80")

SANS = "'Segoe UI', Inter, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, 'Courier New', monospace"

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .rise {{ animation: rise .8s cubic-bezier(.2,.7,.2,1) both; }}
  .fade {{ animation: fade .6s ease-out both; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .ping {{ animation: ping 2s cubic-bezier(0,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes pulse {{ 0%,100% {{ opacity: .45; transform: scale(.85); }} 50% {{ opacity: 1; transform: scale(1.15); }} }}
  @keyframes ping {{ 0% {{ opacity: .7; transform: scale(1); }} 80%,100% {{ opacity: 0; transform: scale(2.6); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def e(s):
    return escape(str(s), quote=True)


def svg(w, h, body, css="", defs="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}">\n'
            f'<title>{e(label)}</title>\n<style>{BASE_CSS}{css}</style>\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>\n')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  assets/{name}")


def mono_w(text, size):
    return len(text) * size * 0.6


def chip(x, y, text, color, size=12.5, h=26):
    w = mono_w(text, size) + 22
    return (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{color}" '
            f'fill-opacity=".08" stroke="{color}" stroke-opacity=".38"/>'
            f'<text x="{x + w/2:.1f}" y="{y + h/2 + size*0.36:.1f}" text-anchor="middle" '
            f'class="mono" font-size="{size}" fill="{color}">{e(text)}</text>'), w


def delay(s):
    return f' style="animation-delay:{s:.2f}s"'


# ================================================================== HERO
def hero():
    W, H = 1200, 360
    import base64
    photo = base64.b64encode((Path(__file__).parent / "avatar.jpg").read_bytes()).decode()
    PX, PY, PR = 1010, 180, 104

    def orbit(r, dots, cls, dash):
        d = "".join(
            f'<circle cx="{PX + r * __import__("math").cos(__import__("math").radians(a)):.1f}" '
            f'cy="{PY + r * __import__("math").sin(__import__("math").radians(a)):.1f}" r="{sz}" fill="{c}"/>'
            for a, c, sz in dots)
        return (f'<g class="{cls}"><circle cx="{PX}" cy="{PY}" r="{r}" fill="none" stroke="{SOFT}" '
                f'stroke-opacity=".16" stroke-dasharray="{dash}"/>{d}</g>')

    portrait = f"""
  <circle cx="{PX}" cy="{PY}" r="190" fill="url(#gA)"/>
  {orbit(156, [(-60, TEAL, 5), (70, VIOLET, 4), (200, AMBER, 4.5)], "spinR", "3 7")}
  {orbit(132, [(20, CYAN, 3.5), (150, PINK, 4), (260, GREEN, 3)], "spinL", "1 5")}
  <circle cx="{PX}" cy="{PY}" r="{PR + 9}" fill="none" stroke="url(#ring)" stroke-width="3" class="spinR fast"/>
  <circle cx="{PX}" cy="{PY}" r="{PR + 2}" fill="{BG}"/>
  <image x="{PX - PR}" y="{PY - PR}" width="{PR * 2}" height="{PR * 2}" href="data:image/jpeg;base64,{photo}" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>
  <g class="rise"{delay(1)}>
    <rect x="{PX - 74}" y="{PY + PR - 4}" width="148" height="26" rx="13" fill="{PANEL}" stroke="{TEAL}" stroke-opacity=".5"/>
    <circle cx="{PX - 58}" cy="{PY + PR + 9}" r="4" fill="{GREEN}" class="ping"/>
    <circle cx="{PX - 58}" cy="{PY + PR + 9}" r="4" fill="{GREEN}"/>
    <text x="{PX + 6}" y="{PY + PR + 13.5}" text-anchor="middle" class="mono" font-size="12" fill="{TEXT}">shipping AI</text>
  </g>
"""

    chips, cx = [], 64
    for t, c in [("LLMs", TEAL), ("RAG", CYAN), ("Voice AI", VIOLET),
                 ("Computer Vision", PINK), ("Full-stack AI", AMBER)]:
        s, w = chip(cx, 244, t, c, size=13, h=28)
        chips.append(s)
        cx += w + 10

    css = f"""
  .orbA {{ animation: float 11s ease-in-out infinite; }}
  .orbB {{ animation: float 14s ease-in-out infinite reverse; }}
  @keyframes float {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(-30px,18px); }} }}
  .spinR {{ animation: spin 40s linear infinite; transform-box: view-box; transform-origin: 1010px 180px; }}
  .spinL {{ animation: spin 55s linear infinite reverse; transform-box: view-box; transform-origin: 1010px 180px; }}
  .fast {{ animation-duration: 6s; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .bar {{ animation: grow 1.2s cubic-bezier(.2,.7,.2,1) .5s both; transform-box: fill-box; transform-origin: left; }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
"""
    defs = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#0A1528"/></linearGradient>
  <radialGradient id="gA"><stop offset="0" stop-color="{TEAL}" stop-opacity=".22"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gB"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".18"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#D5FBF4"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>
  <linearGradient id="ub" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity=".6"/><stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".6"/></linearGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <clipPath id="face"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".2"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
"""
    body = f"""
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <circle cx="1000" cy="70" r="260" fill="url(#gA)" class="orbA"/>
  <circle cx="160" cy="380" r="300" fill="url(#gB)" class="orbB"/>
  {portrait}

  <g class="rise"{delay(.05)}>
    <text x="64" y="86" class="mono" font-size="15" fill="{TEAL}">&gt; whoami<tspan class="blink">▍</tspan></text>
  </g>
  <g class="rise"{delay(.2)}>
    <text x="60" y="160" class="sans" font-size="68" font-weight="800" letter-spacing="-1.5" fill="url(#name)">Tanmay Kala</text>
  </g>
  <rect x="64" y="176" width="150" height="4" rx="2" fill="url(#ub)" class="bar"/>
  <g class="rise"{delay(.4)}>
    <text x="64" y="218" class="sans" font-size="22" fill="{SOFT}">Generative AI &amp; NLP Engineer  <tspan fill="{MUTED}">·</tspan>  Founder @ <tspan fill="{TEXT}" font-weight="700">Naxatra AI</tspan></text>
  </g>
  <g class="rise"{delay(.6)}>{''.join(chips)}</g>
  <g class="rise"{delay(.8)}>
    <circle cx="72" cy="313" r="5" fill="{GREEN}" class="ping"/>
    <circle cx="72" cy="313" r="5" fill="{GREEN}"/>
    <text x="88" y="318" class="sans" font-size="15" fill="{SOFT}">B.Tech CSE (AI &amp; ML) @ VIT Bhopal  <tspan fill="{MUTED}">·</tspan>  <tspan fill="{GREEN}">Open to AI/ML internships</tspan></text>
  </g>
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="21.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
"""
    write("hero.svg", svg(W, H, body, css, defs,
                          "Tanmay Kala — Generative AI & NLP Engineer, Founder @ Naxatra AI"))


# ======================================================= SECTION HEADERS
def header(slug, num, title, comment):
    W, H = 1200, 56
    css = """
  .scan { animation: scan 6s ease-in-out infinite; }
  @keyframes scan { 0%,100% { transform: translateX(0); } 50% { transform: translateX(1040px); } }
"""
    defs = f"""<linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".5" stop-color="{TEAL}"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath>"""
    body = f"""
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{PANEL}"/>
  <rect x="20" y="{H-2}" width="120" height="2" fill="url(#hl)" class="scan"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="{LINE}"/>
<text x="26" y="34" class="mono" font-size="14" fill="{TEAL}">{e(num)}</text>
<text x="62" y="35" class="sans" font-size="17" font-weight="700" letter-spacing="3" fill="{TEXT}">{e(title.upper())}</text>
<text x="{W-26}" y="34" text-anchor="end" class="mono" font-size="13" fill="{MUTED}">{e(comment)}</text>
"""
    write(f"h-{slug}.svg", svg(W, H, body, css, defs, title))


# ============================================================== TERMINAL
def terminal():
    W, H = 1200, 420
    P, K, S, N = MUTED, CYAN, TEAL, AMBER   # punctuation, key, string, accent
    prompt = [("tanmay@naxatra", TEAL), (":", P), ("~/profile", CYAN), ("$ ", P)]
    rows = [
        prompt + [("cat about.json", TEXT)],
        [("{", P)],
        [('  "name"', K), (":      ", P), ('"Tanmay Kala"', S), (",", P)],
        [('  "role"', K), (":      ", P), ('"Generative AI & NLP Engineer"', S), (",", P)],
        [('  "edu"', K), (":       ", P), ('"B.Tech CSE (AI & ML), VIT Bhopal \'28"', S), (",", P)],
        [('  "founder"', K), (":   ", P), ('"Naxatra AI"', N), (",", P)],
        [('  "focus"', K), (":     ", P), ("[", P), ('"LLMs"', S), (", ", P), ('"RAG"', S), (", ", P),
         ('"Voice AI"', S), (", ", P), ('"CV"', S), ("]", P), (",", P)],
        [('  "certified"', K), (": ", P), ('"OCI Generative AI Professional"', S), (",", P)],
        [('  "shipped"', K), (":   ", P), ("5", N), (",", P), ("  ", P), ("// live AI products", "#4B5873")],
        [('  "motto"', K), (":     ", P), ('"Useful AI products, not demos."', VIOLET)],
        [("}", P)],
        prompt,
    ]
    lines = []
    for i, row in enumerate(rows):
        spans = "".join(f'<tspan fill="{c}">{e(t)}</tspan>' for t, c in row)
        cursor = f'<tspan fill="{TEAL}" class="blink">▋</tspan>' if i == len(rows) - 1 else ""
        lines.append(f'<text x="32" y="{88 + i*26}" class="mono fade" font-size="15" '
                     f'xml:space="preserve"{delay(.25 + i*.18)}>{spans}{cursor}</text>')

    side, y, d = [], 92, 2.6
    for title, col, items in [
        ("CURRENTLY", TEAL, ["Building AI products at Naxatra AI",
                             "Voice agents with LangGraph + CALL-E",
                             "Production ML — APIs, Docker, SHAP"]),
        ("LOOKING FOR", AMBER, ["AI/ML & GenAI internships",
                                "Hackathon & open-source teams"]),
        ("ASK ME ABOUT", VIOLET, ["LLM apps · RAG · Voice AI · CV"]),
    ]:
        side.append(f'<g class="rise"{delay(d)}><rect x="724" y="{y-11}" width="3" height="14" rx="1.5" fill="{col}"/>'
                    f'<text x="736" y="{y}" class="mono" font-size="12" letter-spacing="2.5" fill="{col}">{e(title)}</text></g>')
        y += 30
        for it in items:
            d += .15
            side.append(f'<g class="rise"{delay(d)}><text x="736" y="{y}" class="sans" font-size="16" fill="{TEXT}">'
                        f'<tspan fill="{col}">▸ </tspan>{e(it)}</text></g>')
            y += 27
        y += 22
        d += .2

    defs = f'<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
    body = f"""
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="44" fill="{PANEL}"/>
  <line x1="0" y1="44" x2="{W}" y2="44" stroke="{LINE}"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{LINE}"/>
<circle cx="26" cy="22" r="6" fill="#FF5F57"/><circle cx="46" cy="22" r="6" fill="#FEBC2E"/><circle cx="66" cy="22" r="6" fill="#28C840"/>
<text x="{W/2}" y="27" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">tanmay@naxatra — ~/profile — zsh</text>
<line x1="700" y1="70" x2="700" y2="{H-30}" stroke="{LINE}" stroke-dasharray="3 5"/>
{''.join(lines)}
{''.join(side)}
"""
    write("about.svg", svg(W, H, body, "", defs, "About Tanmay Kala"))


# =============================================================== METRICS
def metrics():
    W, H = 1200, 160
    data = [
        ("5+", "AI products shipped", "live on Vercel", TEAL),
        ("Top 25", "of 400+ teams", "Green Bharat hack", CYAN),
        ("96.82%", "test accuracy", "GTSRB · from scratch", VIOLET),
        ("421", "tests passing", "Market Buddy agent", AMBER),
        ("<500ms", "hotword latency", "Hey Dude assistant", PINK),
        ("50+", "languages", "Whisper AI tool", GREEN),
    ]
    tw, gap = (W - 5 * 12) / 6, 12
    tiles = []
    for i, (val, label, sub, col) in enumerate(data):
        x = i * (tw + gap)
        tiles.append(f"""<g class="rise"{delay(.1 + i*.12)}>
  <rect x="{x+.5:.1f}" y="10.5" width="{tw-1:.1f}" height="139" rx="14" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="{x+20:.1f}" y="30" width="26" height="3" rx="1.5" fill="{col}"/>
  <text x="{x+20:.1f}" y="82" class="sans" font-size="36" font-weight="800" letter-spacing="-1" fill="{col}">{e(val)}</text>
  <text x="{x+20:.1f}" y="109" class="sans" font-size="15" font-weight="600" fill="{TEXT}">{e(label)}</text>
  <text x="{x+20:.1f}" y="130" class="mono" font-size="11" fill="{MUTED}">{e(sub)}</text>
</g>""")
    write("impact.svg", svg(W, H, "\n".join(tiles), "", "", "Impact in numbers"))


# ========================================================= PROJECT CARDS
PROJECTS = [
    dict(slug="swachhvan", tag="FLAGSHIP · LIVE", color=TEAL, title="SwachhVan",
         desc=["AI smart-sanitation platform that forecasts demand and",
               "dispatches mobile washroom vans across city zones."],
         points=["Top 25 of 400+ teams · Hack For Green Bharat",
                 "−60% manual dispatch planning across 3 zones"],
         chips=["TypeScript", "Forecasting", "GPS", "Vercel"]),
    dict(slug="heydude", tag="VOICE AI · LIVE", color=VIOLET, title="Hey Dude",
         desc=["Voice assistant with face-auth login, Gemini reasoning,",
               "WhatsApp automation and full system control."],
         points=["Shipped zero → production in 15 days",
                 "<500 ms hotword latency · <2 s face login"],
         chips=["Python", "Gemini", "OpenCV", "SQLite"]),
    dict(slug="marketbuddy", tag="AGENTIC AI · HACKATHON", color=AMBER, title="Market Buddy",
         desc=["Autonomous voice agent that phones wholesale suppliers",
               "and turns live calls into commercial commitments."],
         points=["CALL-E voice SDK + LangGraph orchestration",
                 "421 tests passing across 19 suites"],
         chips=["Next.js", "LangGraph", "TypeScript", "CALL-E"]),
    dict(slug="gtsrb", tag="DEEP LEARNING", color=CYAN, title="TrafficSignNet",
         desc=["43-class traffic-sign CNN written from scratch in",
               "PyTorch — CPU-only, fully CLI-driven, tested."],
         points=["96.82% test accuracy with only 99K parameters",
                 "Track-aware split to stop frame leakage"],
         chips=["PyTorch", "CNN", "GTSRB", "CLI"]),
    dict(slug="travel", tag="NLP · LIVE", color=PINK, title="AI Travel Assist",
         desc=["Surfaces hidden points of interest along your route",
               "and ranks them by priority in real time."],
         points=["+40% relevance over baseline search",
                 "Sole AI engineer in a 6-member team"],
         chips=["Gemini", "SerpAPI", "TypeScript", "Geo"]),
    dict(slug="whisper", tag="SPEECH · LIVE", color=GREEN, title="Whisper Transcribe",
         desc=["Drag-and-drop transcription with automatic language",
               "detection, translation and subtitle export."],
         points=["95%+ accuracy across 50+ languages",
                 "TXT · SRT · JSON output, zero-cost hosting"],
         chips=["Whisper", "Gradio", "Flask", "Python"]),
]


def card(i, p):
    W, H = 580, 260
    c = p["color"]
    tag_w = mono_w(p["tag"], 11) + 20
    chips, cx = [], 28
    for t in p["chips"]:
        s, w = chip(cx, 214, t, c, size=12)
        chips.append(s)
        cx += w + 8
    css = f"""
  .shine {{ animation: shine 7s ease-in-out {i*1.1:.1f}s infinite; }}
  @keyframes shine {{ 0% {{ transform: translateX(-260px) skewX(-20deg); }} 35%,100% {{ transform: translateX(860px) skewX(-20deg); }} }}
"""
    defs = f"""
  <clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <linearGradient id="top" x1="0" x2="1"><stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>
  <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="glow" cx="1" cy="0" r="1"><stop offset="0" stop-color="{c}" stop-opacity=".14"/><stop offset=".6" stop-color="{c}" stop-opacity="0"/></radialGradient>
"""
    pts = "".join(
        f'<text x="28" y="{168 + j*24}" class="sans" font-size="14.5" fill="{TEXT}">'
        f'<tspan fill="{c}" class="mono">▸ </tspan>{e(t)}</text>' for j, t in enumerate(p["points"]))
    desc = "".join(
        f'<text x="28" y="{114 + j*20}" class="sans" font-size="14.5" fill="{MUTED}">{e(t)}</text>'
        for j, t in enumerate(p["desc"]))
    body = f"""
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{PANEL}"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  <rect width="{W}" height="3" fill="url(#top)"/>
  <rect x="0" y="0" width="140" height="{H}" fill="url(#sh)" class="shine"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{LINE}"/>
<g class="rise">
  <text x="28" y="40" class="mono" font-size="12" fill="{MUTED}">{i+1:02d}</text>
  <rect x="56" y="25" width="{tag_w:.1f}" height="21" rx="10.5" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".45"/>
  <text x="{56 + tag_w/2:.1f}" y="39.5" text-anchor="middle" class="mono" font-size="11" letter-spacing=".5" fill="{c}">{e(p["tag"])}</text>
  <text x="{W-28}" y="44" text-anchor="end" class="mono" font-size="20" fill="{c}">↗</text>
  <text x="28" y="86" class="sans" font-size="27" font-weight="800" letter-spacing="-.5" fill="{TEXT}">{e(p["title"])}</text>
  {desc}
</g>
<g class="rise"{delay(.2)}>{pts}</g>
<g class="rise"{delay(.35)}>{''.join(chips)}</g>
"""
    write(f"card-{p['slug']}.svg", svg(W, H, body, css, defs, p["title"]))


# ================================================================= STACK
def stack():
    W = 1200
    cols = [
        ("GENAI & LLMS", TEAL, ["LLMs", "RAG", "Prompt Eng.", "Fine-tuning", "Gemini API", "OpenAI API",
                                "Hugging Face", "Transformers", "LangGraph", "Vector DBs"]),
        ("ML & DEEP LEARNING", CYAN, ["PyTorch", "TensorFlow", "scikit-learn", "CNNs", "NLP", "SHAP",
                                      "pandas", "NumPy"]),
        ("SPEECH & VISION", VIOLET, ["Whisper", "OpenCV", "Speech Recog.", "TTS", "Porcupine",
                                     "Snowboy", "Face Auth"]),
        ("SHIP & SCALE", AMBER, ["Python", "TypeScript", "FastAPI", "Flask", "Gradio", "Streamlit",
                                 "Docker", "Vercel", "OCI", "AWS", "GCP", "SQL"]),
    ]
    cw, gap = (W - 3 * 14) / 4, 14
    parts, max_y = [], 0
    for i, (title, col, items) in enumerate(cols):
        x0 = i * (cw + gap)
        x, y = x0 + 20, 62
        chips = []
        for t in items:
            w = mono_w(t, 12) + 22
            if x + w > x0 + cw - 16:
                x, y = x0 + 20, y + 34
            s, w = chip(x, y, t, col, size=12)
            chips.append(s)
            x += w + 8
        max_y = max(max_y, y + 26)
        parts.append((x0, title, col, chips))
    H = int(max_y + 22)
    body = []
    for i, (x0, title, col, chips) in enumerate(parts):
        body.append(f"""<g class="rise"{delay(.1 + i*.15)}>
  <rect x="{x0+.5:.1f}" y=".5" width="{cw-1:.1f}" height="{H-1}" rx="14" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="{x0+20:.1f}" y="24" width="3" height="14" rx="1.5" fill="{col}"/>
  <text x="{x0+32:.1f}" y="36" class="mono" font-size="12.5" letter-spacing="2.5" fill="{col}">{e(title)}</text>
  {''.join(chips)}
</g>""")
    write("stack.svg", svg(W, H, "\n".join(body), "", "", "Tech stack"))


# ============================================================== TIMELINE
def timeline():
    W, H, Y = 1200, 300, 150
    events = [
        ("SEP 2024", "Joined VIT Bhopal", "B.Tech CSE · AI & ML", TEAL),
        ("JAN 2025", "Whisper AI tool", "50+ languages", GREEN),
        ("FEB 2025", "SwachhVan", "Top 25 / 400+ teams", CYAN),
        ("JUN 2025", "VibeHub", "Summer of Codefest '25", PINK),
        ("OCT 2025", "OCI GenAI Pro", "Oracle certified", AMBER),
        ("NOV 2025", "Hey Dude", "zero → prod in 15 days", VIOLET),
        ("2026", "Agents + prod ML", "CNNs · SHAP · LangGraph", TEAL),
    ]
    x0, x1 = 125, 1075
    step = (x1 - x0) / (len(events) - 1)
    css = """
  .draw { stroke-dasharray: 1100; stroke-dashoffset: 1100; animation: draw 2.2s cubic-bezier(.4,0,.2,1) .2s forwards; }
  @keyframes draw { to { stroke-dashoffset: 0; } }
  @media (prefers-reduced-motion: reduce) { .draw { stroke-dashoffset: 0; } }
"""
    defs = f"""<linearGradient id="tl" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>"""
    items = []
    for i, (date, title, sub, col) in enumerate(events):
        x = x0 + i * step
        up = i % 2 == 0
        d = .3 + i * .3
        ty = Y - 76 if up else Y + 52
        stem = (f'<line x1="{x:.1f}" y1="{Y-14 if up else Y+14}" x2="{x:.1f}" y2="{Y-26 if up else Y+32}" '
                f'stroke="{col}" stroke-opacity=".5" stroke-dasharray="2 3"/>')
        last = i == len(events) - 1
        ping = f'<circle cx="{x:.1f}" cy="{Y}" r="7" fill="{col}" class="ping"/>' if last else ""
        items.append(f"""<g class="rise"{delay(d)}>
  {stem}{ping}
  <circle cx="{x:.1f}" cy="{Y}" r="11" fill="{col}" fill-opacity=".14"/>
  <circle cx="{x:.1f}" cy="{Y}" r="6" fill="{BG}" stroke="{col}" stroke-width="2.5"/>
  <text x="{x:.1f}" y="{ty}" text-anchor="middle" class="mono" font-size="11.5" letter-spacing="1.5" fill="{col}">{e(date)}</text>
  <text x="{x:.1f}" y="{ty+22}" text-anchor="middle" class="sans" font-size="15.5" font-weight="700" fill="{TEXT}">{e(title)}</text>
  <text x="{x:.1f}" y="{ty+41}" text-anchor="middle" class="sans" font-size="12.5" fill="{MUTED}">{e(sub)}</text>
</g>""")
    body = f"""
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{BG}"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{LINE}"/>
<line x1="{x0-40}" y1="{Y}" x2="{x1+40}" y2="{Y}" stroke="{LINE}" stroke-width="2"/>
<line x1="{x0-40}" y1="{Y}" x2="{x1+40}" y2="{Y}" stroke="url(#tl)" stroke-width="2" class="draw"/>
{''.join(items)}
<text x="{x1+40}" y="{H-16}" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">→ still shipping</text>
"""
    write("journey.svg", svg(W, H, body, css, defs, "Build journey"))


# ================================================================ FOOTER
def footer():
    W, H = 1200, 210
    css = """
  .w1 { animation: wave 12s linear infinite; }
  .w2 { animation: wave 18s linear infinite reverse; }
  @keyframes wave { from { transform: translateX(0); } to { transform: translateX(-1200px); } }
"""

    def wave(y, amp):
        d = f"M0 {y} "
        for k in range(6):
            x = k * 400
            d += f"Q{x+100} {y-amp} {x+200} {y} T{x+400} {y} "
        return d + f"V{H} H0 Z"

    defs = f"""<linearGradient id="wv" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#0A1528"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>"""
    body = f"""
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <path d="{wave(168, 14)}" fill="url(#wv)" fill-opacity=".14" class="w1"/>
  <path d="{wave(180, 10)}" fill="url(#wv)" fill-opacity=".22" class="w2"/>
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="21.5" fill="none" stroke="{LINE}" stroke-width="1.5"/>
<g class="rise">
  <text x="{W/2}" y="66" text-anchor="middle" class="mono" font-size="14" fill="{TEAL}">$ git commit -m "let's build something real"</text>
  <text x="{W/2}" y="112" text-anchor="middle" class="sans" font-size="34" font-weight="800" letter-spacing="-.5" fill="{TEXT}">Got a hard problem? Let’s ship the AI for it.</text>
</g>
<g class="rise"{delay(.3)}>
  <text x="{W/2}" y="146" text-anchor="middle" class="mono" font-size="13.5" fill="{MUTED}">tanmaykala171206@gmail.com  ·  linkedin.com/in/tanmay-kala  ·  github.com/tanmayai23</text>
</g>
"""
    write("footer.svg", svg(W, H, body, css, defs, "Let's build something real"))


if __name__ == "__main__":
    print("Building assets:")
    hero()
    terminal()
    metrics()
    for i, p in enumerate(PROJECTS):
        card(i, p)
    stack()
    timeline()
    footer()
    for slug, num, title, comment in [
        ("about", "01", "About", "// cat about.json"),
        ("impact", "02", "Impact", "// numbers, not adjectives"),
        ("work", "03", "Featured Work", "// click a card to open it"),
        ("lab", "04", "Also in the Lab", "// more experiments"),
        ("stack", "05", "Tech Stack", "// tools I ship with"),
        ("journey", "06", "Build Journey", "// git log --oneline"),
        ("github", "07", "GitHub Activity", "// live stats"),
    ]:
        header(slug, num, title, comment)
