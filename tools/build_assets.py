"""Generates the "Ghost Protocol" SVG assets for the profile README.

Each asset is written twice (name-dark.svg / name-light.svg); the README picks one
with <picture> + prefers-color-scheme, which follows the viewer's GitHub theme.

Run:  python tools/build_assets.py
"""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

DARK = dict(name="dark", bg="#050817", bg2="#111044", panel="#071D36", line="#1F2C63", text="#E4E9FF",
            soft="#A9B8E8", muted="#7F8BB8", red="#FF3158", red2="#8B102B", blue="#5145FF", blue2="#7C73FF",
            green="#34D399", ink="#E4E9FF", grid=".05", glowR=".45", glowB=".40")
LIGHT = dict(name="light", bg="#EEF1FF", bg2="#DCE1FF", panel="#E2E7FC", line="#C3CBEE", text="#050817",
             soft="#111044", muted="#4B557E", red="#8B102B", red2="#8B102B", blue="#5145FF", blue2="#5145FF",
             green="#047857", ink="#111044", grid=".06", glowR=".14", glowB=".16")

SANS = "'Segoe UI', Inter, -apple-system, 'Helvetica Neue', Arial, sans-serif"
COND = "Bahnschrift, 'DIN Condensed', 'Arial Narrow', 'Roboto Condensed', 'Segoe UI', sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', SFMono-Regular, Consolas, 'Courier New', monospace"
SERIF = "Georgia, 'Times New Roman', serif"

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .cond {{ font-family: {COND}; }}
  .mono {{ font-family: {MONO}; }}
  .serif {{ font-family: {SERIF}; }}
  .rise {{ animation: rise .9s cubic-bezier(.2,.7,.2,1) both; }}
  .redact {{ animation: unredact .7s cubic-bezier(.7,0,.3,1) both; transform-box: fill-box; transform-origin: right; }}
  .stamp {{ animation: stamp .5s cubic-bezier(.2,.8,.2,1.3) both; transform-box: fill-box; transform-origin: center; }}
  .blink {{ animation: blink 1.2s steps(1) infinite; }}
  .ping {{ animation: ping 2s cubic-bezier(0,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }}
  .drift {{ animation: drift 16s ease-in-out infinite; }}
  @keyframes drift {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(30px,-16px); }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes unredact {{ from {{ transform: scaleX(1); }} to {{ transform: scaleX(0); }} }}
  @keyframes stamp {{ from {{ opacity: 0; transform: scale(1.8); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes ping {{ 0% {{ opacity: .8; transform: scale(1); }} 80%,100% {{ opacity: 0; transform: scale(2.8); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .redact {{ display: none; }} }}
"""


def e(s):
    return escape(str(s), quote=True)


def dl(s):
    return f' style="animation-delay:{s:.2f}s"'


def svg(w, h, body, css, defs, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{e(label)}"><title>{e(label)}</title><style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n')


def frame(T, w, h, file_no, right):
    """Paper/graphite sheet with grid, registration marks and a dossier header strip."""
    marks = "".join(
        f'<path d="M{x},{y+dy*14} V{y} H{x+dx*14}" fill="none" stroke="{T["muted"]}" stroke-width="1.5"/>'
        for x, y, dx, dy in [(14, 14, 1, 1), (w-14, 14, -1, 1), (14, h-14, 1, -1), (w-14, h-14, -1, -1)])
    return f"""
<g clip-path="url(#sheet)">
  <rect width="{w}" height="{h}" fill="url(#bgG)"/>
  <ellipse cx="{w*.12:.0f}" cy="{h}" rx="{w*.42:.0f}" ry="{h*.9:.0f}" fill="url(#gR)" class="drift"/>
  <ellipse cx="{w*.9:.0f}" cy="0" rx="{w*.45:.0f}" ry="{h:.0f}" fill="url(#gB)" class="drift" style="animation-delay:-6s"/>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
</g>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="14" fill="none" stroke="{T['line']}" stroke-width="1.5"/>
{marks}
<text x="40" y="44" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">{e(file_no)}</text>
<text x="{w-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">{right}</text>
<line x1="40" y1="58" x2="{w-40}" y2="58" stroke="{T['line']}"/>
"""


def sheet_defs(T, w, h):
    return (f'<clipPath id="sheet"><rect width="{w}" height="{h}" rx="14"/></clipPath>'
            f'<linearGradient id="bgG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["bg"]}"/>'
            f'<stop offset=".55" stop-color="{T["bg"]}"/><stop offset="1" stop-color="{T["bg2"]}"/></linearGradient>'
            f'<radialGradient id="gR"><stop offset="0" stop-color="{T["red2"]}" stop-opacity="{T["glowR"]}"/>'
            f'<stop offset="1" stop-color="{T["red2"]}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="gB"><stop offset="0" stop-color="{T["blue"]}" stop-opacity="{T["glowB"]}"/>'
            f'<stop offset="1" stop-color="{T["blue"]}" stop-opacity="0"/></radialGradient>'
            f'<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
            f'<path d="M24 0H0V24" fill="none" stroke="{T["ink"]}" stroke-opacity="{T["grid"]}"/></pattern>')


# ================================================================== HERO
def emblem(T, cx, cy):
    """Original abstract 'signal mask': a faceless mask filled with a live waveform, red visor slits."""
    mask = (f"M{cx-96},{cy-104} Q{cx},{cy-138} {cx+96},{cy-104} Q{cx+124},{cy+6} {cx+44},{cy+118} "
            f"Q{cx},{cy+142} {cx-44},{cy+118} Q{cx-124},{cy+6} {cx-96},{cy-104} Z")
    bars = []
    for i, y in enumerate(range(cy - 120, cy + 140, 9)):
        w = 70 + 90 * abs(math.sin(i * .55)) * (1 - abs(y - cy) / 190)
        bars.append(f'<rect x="{cx - w/2:.1f}" y="{y}" width="{w:.1f}" height="3" rx="1.5" fill="{T["blue2"]}" '
                    f'fill-opacity=".55" class="wave"{dl(-(i % 9) * .17)}/>')
    eyes = (f'<path d="M{cx-74},{cy-14} L{cx-14},{cy-4} L{cx-18},{cy+8} L{cx-70},{cy+2} Z" fill="{T["red"]}" class="eye"/>'
            f'<path d="M{cx+74},{cy-14} L{cx+14},{cy-4} L{cx+18},{cy+8} L{cx+70},{cy+2} Z" fill="{T["red"]}" class="eye"/>')
    ticks = "".join(
        f'<line x1="{cx + 150*math.cos(math.radians(a)):.1f}" y1="{cy + 150*math.sin(math.radians(a)):.1f}" '
        f'x2="{cx + 164*math.cos(math.radians(a)):.1f}" y2="{cy + 164*math.sin(math.radians(a)):.1f}" stroke="{T["muted"]}" stroke-width="2"/>'
        for a in (0, 90, 180, 270))
    return f"""
<defs><clipPath id="mask"><path d="{mask}"/></clipPath></defs>
<g class="spin"><circle cx="{cx}" cy="{cy}" r="157" fill="none" stroke="{T['muted']}" stroke-opacity=".5" stroke-dasharray="2 10"/>{ticks}
  <circle cx="{cx+157}" cy="{cy}" r="4" fill="{T['red']}"/></g>
<path d="{mask}" fill="{T['panel']}" stroke="{T['line']}" stroke-width="2"/>
<g clip-path="url(#mask)">{''.join(bars)}
  <rect x="{cx-140}" y="{cy-150}" width="280" height="2" fill="{T['red']}" fill-opacity=".8" class="scan"/>
</g>
{eyes}
<path d="{mask}" fill="none" stroke="{T['text']}" stroke-opacity=".7" stroke-width="2"/>
"""


def hero(T):
    W, H = 1200, 430
    cx, cy = 225, 245
    css = f"""
  .wave {{ animation: wave 1.6s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }}
  @keyframes wave {{ from {{ transform: scaleX(.45); }} to {{ transform: scaleX(1); }} }}
  .scan {{ animation: scan 4.5s ease-in-out infinite; }}
  @keyframes scan {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(290px); }} }}
  .eye {{ animation: eye 3.2s ease-in-out infinite; }}
  @keyframes eye {{ 0%,100% {{ opacity: 1; }} 46% {{ opacity: 1; }} 50% {{ opacity: .15; }} 54% {{ opacity: 1; }} }}
  .spin {{ animation: spin 50s linear infinite; transform-box: view-box; transform-origin: {cx}px {cy}px; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
"""
    fields = [("ROLE", "GenAI & NLP Engineer"), ("OPERATION", "NAXATRA AI"), ("BASE", "VIT Bhopal · Bharat")]
    fx = [470, 700, 905]
    field_svg = "".join(
        f'<g class="rise"{dl(.9 + i*.1)}><text x="{x}" y="356" class="mono" font-size="11.5" letter-spacing="2.5" fill="{T["muted"]}">{e(k)}</text>'
        f'<text x="{x}" y="382" class="sans" font-size="16.5" font-weight="700" fill="{T["text"]}">{e(v)}</text>'
        f'<rect x="{x-2}" y="366" width="{len(v)*9.4:.0f}" height="22" fill="{T["ink"]}" class="redact"{dl(1.3 + i*.35)}/></g>'
        for i, ((k, v), x) in enumerate(zip(fields, fx)))
    body = f"""
{frame(T, W, H, "FILE NO. TK-2028  ·  CLEARANCE: PUBLIC", "")}
<g class="rise"><text x="{W-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">
  <tspan fill="{T['green']}">● </tspan>STATUS: <tspan fill="{T['green']}">ACTIVE</tspan><tspan class="blink" fill="{T['green']}">_</tspan></text></g>
{emblem(T, cx, cy)}
<g class="rise"{dl(.15)}><text x="470" y="128" class="mono" font-size="14" font-weight="700" letter-spacing="7" fill="{T['red']}">THE GHOST PROTOCOL</text></g>
<g class="rise"{dl(.3)}><text x="466" y="208" class="cond" font-size="84" font-weight="700" letter-spacing="3" textLength="560" lengthAdjust="spacingAndGlyphs" fill="{T['text']}">TANMAY KALA</text></g>
<g class="rise"{dl(.45)}><rect x="470" y="226" width="64" height="4" fill="{T['red']}"/>
  <text x="550" y="233" class="mono" font-size="14" letter-spacing="2.5" fill="{T['soft']}">AI ENGINEER · FOUNDER · SYSTEMS THINKER</text></g>
<g class="rise"{dl(.6)}><text x="470" y="296" class="serif" font-size="32" font-style="italic" fill="{T['text']}">Build quietly. <tspan fill="{T['red']}">Ship relentlessly.</tspan></text></g>
<line x1="470" y1="326" x2="{W-40}" y2="326" stroke="{T['line']}" stroke-dasharray="4 5"/>
{field_svg}
<g class="stamp"{dl(2.4)}><g transform="rotate(-9 1075 290)">
  <rect x="990" y="266" width="170" height="48" rx="6" fill="none" stroke="{T['red']}" stroke-width="3"/>
  <rect x="996" y="272" width="158" height="36" rx="3" fill="none" stroke="{T['red']}" stroke-width="1.2"/>
  <text x="1075" y="297" text-anchor="middle" class="mono" font-size="16" font-weight="800" letter-spacing="3" fill="{T['red']}">DECLASSIFIED</text>
</g></g>
"""
    return svg(W, H, body, css, sheet_defs(T, W, H),
               "Tanmay Kala — AI engineer, founder, and systems thinker. Build quietly. Ship relentlessly.")


# ============================================================ SWACHHVAN
def swachhvan(T):
    W, H = 1200, 420
    css = """
  .pulse { animation: pulse 2.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes pulse { 0%,100% { opacity: .25; transform: scale(.7); } 50% { opacity: .75; transform: scale(1.15); } }
"""
    # right-hand "Fig. 1" city dispatch map
    mx, my, mw, mh = 744, 92, 416, 252
    streets = "".join(f'<line x1="{mx}" y1="{my+y}" x2="{mx+mw}" y2="{my+y}" stroke="{T["line"]}" stroke-width="{w}"/>'
                      for y, w in [(46, 2), (118, 5), (190, 2), (232, 2)])
    streets += "".join(f'<line x1="{mx+x}" y1="{my}" x2="{mx+x}" y2="{my+mh}" stroke="{T["line"]}" stroke-width="{w}"/>'
                       for x, w in [(64, 2), (150, 5), (250, 2), (338, 3)])
    zones = [(mx+14, my+14, 126, 94, "Z1"), (mx+160, my+128, 168, 100, "Z2"), (mx+262, my+14, 140, 94, "Z3")]
    zone_svg = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{T["red"]}" fill-opacity=".05" stroke="{T["red"]}" stroke-opacity=".55" stroke-dasharray="5 5"/>'
        f'<text x="{x+10}" y="{y+20}" class="mono" font-size="11" font-weight="700" fill="{T["red"]}">{z}</text>'
        for x, y, w, h, z in zones)
    demand = [(mx+92, my+66, 22), (mx+230, my+182, 28), (mx+330, my+62, 18), (mx+190, my+60, 12), (mx+70, my+212, 14)]
    dem_svg = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{T["red"]}" class="pulse"{dl(i*.5)}/>'
                      f'<circle cx="{x}" cy="{y}" r="3" fill="{T["red"]}"/>' for i, (x, y, r) in enumerate(demand))
    routes = [
        (f"M{mx+150},{my+mh} V{my+118} H{mx+64} V{my+66}", 7),
        (f"M{mx+mw},{my+190} H{mx+250} V{my+182}", 5.5),
        (f"M{mx+150},{my} V{my+46} H{mx+338} V{my+62}", 6.5),
    ]
    route_svg = "".join(
        f'<path d="{d}" fill="none" stroke="{T["blue2"]}" stroke-width="2.5" stroke-dasharray="6 6" stroke-opacity=".8"/>'
        f'<g><rect x="-9" y="-6" width="18" height="12" rx="3" fill="{T["blue2"]}"/>'
        f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;.8;1" calcMode="linear"/></g>'
        for d, dur in routes)
    fig = f"""
<rect x="{mx-16}" y="{my-16}" width="{mw+32}" height="{mh+32}" rx="10" fill="{T['panel']}" stroke="{T['line']}"/>
<g clip-path="url(#map)">{streets}{zone_svg}{dem_svg}{route_svg}</g>
<text x="{mx-16}" y="{my+mh+42}" class="mono" font-size="11.5" letter-spacing="1.5" fill="{T['muted']}">FIG. 1 — FORECAST → DISPATCH</text>
<text x="{mx+mw+16}" y="{my+mh+42}" text-anchor="end" class="mono" font-size="11.5" fill="{T['muted']}"><tspan fill="{T['red']}">●</tspan> demand  <tspan fill="{T['blue2']}">■</tspan> van</text>
"""
    metrics = [("TOP 25", "of 400+ teams"), ("−60%", "dispatch planning"), ("3", "city zones"), ("100+", "simulated bookings")]
    tw = 154
    met_svg = "".join(
        f'<g class="rise"{dl(.6 + i*.12)}><rect x="{40 + i*(tw+12)}" y="262" width="{tw}" height="78" rx="8" fill="{T["panel"]}" stroke="{T["line"]}"/>'
        f'<rect x="{40 + i*(tw+12)}" y="262" width="3" height="78" fill="{T["red"] if i % 2 == 0 else T["blue2"]}"/>'
        f'<text x="{58 + i*(tw+12)}" y="298" class="cond" font-size="30" font-weight="700" fill="{T["text"]}">{e(v)}</text>'
        f'<text x="{58 + i*(tw+12)}" y="322" class="sans" font-size="12.5" fill="{T["muted"]}">{e(l)}</text></g>'
        for i, (v, l) in enumerate(metrics))
    body = f"""
{frame(T, W, H, "CASE FILE 01  ·  FLAGSHIP OPERATION", "")}
<text x="{W-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}"><tspan fill="{T['green']}">● </tspan>DEPLOYED · <tspan fill="{T['green']}">LIVE</tspan></text>
<g class="rise"{dl(.1)}><text x="40" y="132" class="cond" font-size="64" font-weight="700" letter-spacing="1" fill="{T['text']}">SwachhVan</text></g>
<g class="rise"{dl(.25)}><text x="42" y="164" class="mono" font-size="13.5" letter-spacing="2.5" fill="{T['red']}">AI SMART-SANITATION PLATFORM</text></g>
<g class="rise"{dl(.4)}>
  <text x="42" y="204" class="sans" font-size="16.5" fill="{T['soft']}">Forecasts sanitation demand across city zones and dispatches</text>
  <text x="42" y="228" class="sans" font-size="16.5" fill="{T['soft']}">mobile washroom vans — with GPS tracking, booking and ratings.</text>
</g>
{met_svg}
<text x="42" y="378" class="mono" font-size="12" fill="{T['muted']}">TypeScript · AI Demand Forecasting · GPS · Vercel</text>
{fig}
"""
    defs = sheet_defs(T, W, H) + f'<clipPath id="map"><rect x="{mx-16}" y="{my-16}" width="{mw+32}" height="{mh+32}" rx="10"/></clipPath>'
    return svg(W, H, body, css, defs, "SwachhVan — AI smart-sanitation platform, Top 25 of 400+ teams")


# ============================================================ BUILD LOG
def build_log(T):
    W, H = 1200, 230
    steps = [("01", "EXPLORE", "the work"), ("02", "READ", "the code"), ("03", "TEST", "the claims"), ("04", "IMPROVE", "the system")]
    x0, x1, y = 150, 1050, 132
    step = (x1 - x0) / 3
    css = f"""
  .signal {{ animation: travel 5s cubic-bezier(.6,0,.4,1) infinite; }}
  @keyframes travel {{ 0% {{ transform: translateX(0); opacity: 0; }} 6% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ transform: translateX({x1-x0}px); opacity: 0; }} }}
  .lit {{ animation: lit 5s linear infinite; }}
  @keyframes lit {{ 0%,100% {{ fill: {T['panel']}; }} 4%,14% {{ fill: {T['red']}; }} 22% {{ fill: {T['panel']}; }} }}
"""
    nodes = "".join(
        f'<g class="rise"{dl(.1 + i*.15)}>'
        f'<circle cx="{x0 + i*step:.0f}" cy="{y}" r="24" fill="{T["panel"]}" stroke="{T["text"]}" stroke-width="2" class="lit" style="animation-delay:{i*5*(step/(x1-x0))*.82:.2f}s"/>'
        f'<text x="{x0 + i*step:.0f}" y="{y+5}" text-anchor="middle" class="mono" font-size="13" font-weight="800" fill="{T["text"]}">{n}</text>'
        f'<text x="{x0 + i*step:.0f}" y="{y+56}" text-anchor="middle" class="cond" font-size="22" font-weight="700" letter-spacing="2" fill="{T["text"]}">{e(a)}</text>'
        f'<text x="{x0 + i*step:.0f}" y="{y+76}" text-anchor="middle" class="serif" font-size="15" font-style="italic" fill="{T["muted"]}">{e(b)}</text></g>'
        for i, (n, a, b) in enumerate(steps))
    body = f"""
{frame(T, W, H, "BUILD LOG  ·  OPERATING LOOP", "")}
<text x="{W-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">REPEAT UNTIL USEFUL <tspan fill="{T['red']}">↻</tspan></text>
<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{T['line']}" stroke-width="2"/>
<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{T['muted']}" stroke-width="2" stroke-dasharray="2 8"/>
<path d="M{x1+24},{y} C{x1+90},{y} {x1+90},{y-62} {x1-20},{y-62} H{x0+20} C{x0-90},{y-62} {x0-90},{y} {x0-24},{y}" fill="none" stroke="{T['blue2']}" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="4 6"/>
<g class="signal"><circle cx="{x0}" cy="{y}" r="6" fill="{T['red']}"/><circle cx="{x0}" cy="{y}" r="12" fill="{T['red']}" fill-opacity=".25"/></g>
{nodes}
"""
    return svg(W, H, body, css, sheet_defs(T, W, H),
               "Build log: explore the work, read the code, test the claims, improve the system.")

# ======================================================= OPERATION CARDS
OPS = [
    dict(slug="heydude", no="02", tag="VOICE AI", title="Hey Dude", sub="VOICE-FIRST DESKTOP ASSISTANT",
         desc=["Voice, Gemini-powered conversation, face", "recognition, hotword detection, automation."],
         metric="<500 ms hotword · 15-day build", tech="Python · Gemini · OpenCV · SQLite", cta="INSPECT REPO", live=False, viz="wave"),
    dict(slug="marketbuddy", no="03", tag="AGENTIC AI", title="Market Buddy", sub="AUTONOMOUS VOICE AGENT · CALL-E",
         desc=["Hackathon voice agent built for dependable", "conversational workflows."],
         metric="421 passing tests", tech="Agents · TypeScript · Testing", cta="INSPECT REPO", live=False, viz="agent"),
    dict(slug="trafficsign", no="04", tag="COMPUTER VISION", title="TrafficSignNet", sub="CNN CLASSIFICATION · 43 CLASSES",
         desc=["Traffic-sign recognition CNN built from", "scratch in PyTorch, CPU-only, CLI-driven."],
         metric="96.82% test accuracy", tech="Python · CNN · Computer Vision", cta="INSPECT REPO", live=False, viz="grid"),
    dict(slug="travel", no="05", tag="NLP · GEO", title="Hey, where next?", sub="AI TRAVEL ASSIST",
         desc=["Location-aware discovery that surfaces", "interesting places along your journey."],
         metric="POIs within a 10 km radius", tech="Python · Gemini API · Geolocation", cta="OPEN LIVE", live=True, viz="route"),
]


def viz(T, kind, cx, cy):
    if kind == "wave":
        bars = "".join(
            f'<rect x="{cx-66 + i*10}" y="{cy-34}" width="5" height="68" rx="2.5" fill="{T["blue2"] if i % 3 else T["red"]}" '
            f'class="eq"{dl(-((i*.13) % 1.1))}/>' for i in range(14))
        return (f'<circle cx="{cx}" cy="{cy}" r="58" fill="none" stroke="{T["line"]}" stroke-dasharray="2 6"/>{bars}'
                f'<text x="{cx}" y="{cy+76}" text-anchor="middle" class="mono" font-size="10.5" letter-spacing="2" fill="{T["muted"]}">"HEY DUDE…"</text>')
    if kind == "agent":
        sat = [(-58, -40, "call"), (58, -40, "plan"), (-58, 40, "tool"), (58, 40, "log")]
        edges = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx}" y2="{cy+dy}" stroke="{T["line"]}" stroke-width="2"/>' for dx, dy, _ in sat)
        dots = "".join(
            f'<circle r="3.5" fill="{T["red"] if i % 2 else T["blue2"]}"><animateMotion dur="{1.6 + i*.3:.1f}s" repeatCount="indefinite" '
            f'path="M{cx},{cy} L{cx+dx},{cy+dy}"/></circle>' for i, (dx, dy, _) in enumerate(sat))
        nodes = "".join(
            f'<circle cx="{cx+dx}" cy="{cy+dy}" r="15" fill="{T["panel"]}" stroke="{T["blue2"]}" stroke-width="1.6"/>'
            f'<text x="{cx+dx}" y="{cy+dy+3.5}" text-anchor="middle" class="mono" font-size="9.5" fill="{T["soft"]}">{n}</text>' for dx, dy, n in sat)
        return (edges + dots + nodes +
                f'<circle cx="{cx}" cy="{cy}" r="22" fill="{T["red"]}" class="ping"/><circle cx="{cx}" cy="{cy}" r="22" fill="{T["red2"]}" stroke="{T["red"]}" stroke-width="2"/>'
                f'<text x="{cx}" y="{cy+4}" text-anchor="middle" class="mono" font-size="11" font-weight="800" fill="#fff">LLM</text>')
    if kind == "grid":
        cs, g, n = 14, 4, 7
        w = n*cs + (n-1)*g
        x0, y0 = cx - w/2, cy - w/2 - 6
        cells = "".join(
            f'<rect x="{x0 + (k % n)*(cs+g):.1f}" y="{y0 + (k//n)*(cs+g):.1f}" width="{cs}" height="{cs}" rx="3" '
            f'fill="{T["blue2"] if k < 43 else "none"}" fill-opacity="{.25 + .6*((k*37) % 10)/10:.2f}" stroke="{T["line"]}"/>'
            for k in range(n*n))
        return (f'<defs><clipPath id="gc"><rect x="{x0}" y="{y0}" width="{w}" height="{w}"/></clipPath></defs>{cells}'
                f'<g clip-path="url(#gc)"><rect x="{x0-30}" y="{y0}" width="24" height="{w}" fill="{T["red"]}" fill-opacity=".45" class="sweep"/></g>'
                f'<text x="{cx}" y="{y0 + w + 20}" text-anchor="middle" class="mono" font-size="10.5" letter-spacing="2" fill="{T["muted"]}">43 CLASSES</text>')
    d = f"M{cx-62},{cy+40} C{cx-30},{cy+40} {cx-40},{cy-10} {cx},{cy-6} S{cx+30},{cy-50} {cx+60},{cy-42}"
    pins = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{T["red"]}"/><circle cx="{x}" cy="{y}" r="5" fill="{T["red"]}" class="ping"{dl(i*.6)}/>'
                   for i, (x, y) in enumerate([(cx-22, cy+18), (cx+18, cy-22), (cx+48, cy-8)]))
    return (f'<circle cx="{cx}" cy="{cy}" r="56" fill="{T["blue"]}" fill-opacity=".07" stroke="{T["blue2"]}" stroke-dasharray="3 5"/>'
            f'<path d="{d}" fill="none" stroke="{T["blue2"]}" stroke-width="2.5" stroke-dasharray="6 5"/>{pins}'
            f'<circle r="6" fill="{T["text"]}" stroke="{T["blue2"]}" stroke-width="2.5"><animateMotion dur="4s" repeatCount="indefinite" path="{d}"/></circle>'
            f'<text x="{cx}" y="{cy+76}" text-anchor="middle" class="mono" font-size="10.5" letter-spacing="2" fill="{T["muted"]}">10 KM RADIUS</text>')


def op_card(T, p):
    W, H = 592, 290
    css = """
  .eq { animation: eq 1.1s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
  @keyframes eq { from { transform: scaleY(.18); } to { transform: scaleY(1); } }
  .sweep { animation: sweep 3s ease-in-out infinite; }
  @keyframes sweep { 0% { transform: translateX(0); } 100% { transform: translateX(160px); } }
"""
    status = (f'<tspan fill="{T["green"]}">● </tspan>DEPLOYED · <tspan fill="{T["green"]}">LIVE</tspan>' if p["live"]
              else f'<tspan fill="{T["blue2"]}">● </tspan>SOURCE · <tspan fill="{T["blue2"]}">OPEN</tspan>')
    mw = len(p["metric"]) * 7.4 + 30
    cw = len(p["cta"]) * 8.4 + 52
    desc = "".join(f'<text x="40" y="{176 + i*21}" class="sans" font-size="14.5" fill="{T["soft"]}">{e(t)}</text>' for i, t in enumerate(p["desc"]))
    mcol = T["blue2"] if T["name"] == "light" else T["text"]
    body = f"""
{frame(T, W, H, f"CASE FILE {p['no']}  ·  {p['tag']}", "")}
<text x="{W-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">{status}</text>
<text x="{W-24}" y="{H-18}" text-anchor="end" class="cond" font-size="170" font-weight="700" fill="{T['text']}" fill-opacity=".045">{p['no']}</text>
<g class="rise"{dl(.1)}><text x="38" y="112" class="cond" font-size="38" font-weight="700" letter-spacing=".5" fill="{T['text']}">{e(p['title'])}</text></g>
<g class="rise"{dl(.2)}><rect x="40" y="128" width="28" height="3" fill="{T['red']}"/>
  <text x="78" y="134" class="mono" font-size="11" letter-spacing="2" fill="{T['red']}">{e(p['sub'])}</text></g>
<g class="rise"{dl(.3)}>{desc}</g>
<g class="rise"{dl(.4)}><rect x="40" y="208" width="{mw:.0f}" height="26" rx="13" fill="{T['blue']}" fill-opacity=".14" stroke="{T['blue2']}" stroke-opacity=".6"/>
  <text x="{40 + mw/2:.0f}" y="225.5" text-anchor="middle" class="mono" font-size="12" font-weight="700" fill="{mcol}">{e(p['metric'])}</text></g>
<text x="40" y="{H-34}" class="mono" font-size="11.5" fill="{T['muted']}">{e(p['tech'])}</text>
<g class="rise"{dl(.5)}><rect x="{W-40-cw:.0f}" y="{H-56}" width="{cw:.0f}" height="32" rx="4" fill="{T['red2']}" stroke="{T['red']}"/>
  <text x="{W-40-cw/2:.0f}" y="{H-35}" text-anchor="middle" class="mono" font-size="12" font-weight="800" letter-spacing="2" fill="#fff">{e(p['cta'])} ↗</text></g>
<g class="rise"{dl(.35)}>{viz(T, p['viz'], 478, 140)}</g>
"""
    return svg(W, H, body, css, sheet_defs(T, W, H), f"{p['title']} — {p['sub'].title()}")


# ========================================================== FIELD NOTES
def field_notes(T):
    W, H = 1200, 312
    tw, g, y0, th = (1200 - 80 - 32) / 3, 16, 80, 204
    circ = 2 * math.pi * 40
    css = f"""
  .slide {{ animation: slide 1.8s cubic-bezier(.2,.7,.2,1) .4s both; }}
  @keyframes slide {{ from {{ transform: translateX(260px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  .ring {{ animation: ring 2s cubic-bezier(.3,.7,.2,1) .4s both; }}
  @keyframes ring {{ from {{ stroke-dashoffset: {circ:.1f}; }} }}
  .tick {{ animation: tick .25s ease-out both; }}
  @keyframes tick {{ from {{ opacity: .12; }} to {{ opacity: 1; }} }}
"""
    tiles = []
    for i, (num, label, sub, col) in enumerate([
            ("TOP 25", "Hack For Green Bharat", "among 400+ teams, as reported", "red"),
            ("96.82%", "Traffic-sign CNN accuracy", "project-reported result", "blue2"),
            ("421", "Passing tests", "CALL-E / Market Buddy, project-reported", "red")]):
        x = 40 + i * (tw + g)
        tiles.append(f'<g class="rise"{dl(.1 + i*.15)}><rect x="{x:.1f}" y="{y0}" width="{tw:.1f}" height="{th}" rx="10" fill="{T["panel"]}" stroke="{T["line"]}"/>'
                     f'<rect x="{x:.1f}" y="{y0}" width="4" height="{th}" fill="{T[col]}"/>'
                     f'<text x="{x+26:.1f}" y="{y0+36}" class="mono" font-size="11" letter-spacing="2.5" fill="{T["muted"]}">EVIDENCE {i+1:02d}</text>'
                     f'<text x="{x+24:.1f}" y="{y0+94}" class="cond" font-size="58" font-weight="700" fill="{T["text"]}">{num}</text>'
                     f'<text x="{x+26:.1f}" y="{y0+120}" class="sans" font-size="15" font-weight="700" fill="{T["text"]}">{e(label)}</text>'
                     f'<text x="{x+26:.1f}" y="{y0+140}" class="sans" font-size="12.5" fill="{T["muted"]}">{e(sub)}</text></g>')
    # tile 1: rank bar with marker at #25 of 400
    x = 40
    bx, bw, by = x + 26, tw - 52, y0 + 160
    segs = "".join(f'<rect x="{bx + k*bw/80:.1f}" y="{by}" width="{bw/80 - 1.2:.1f}" height="10" rx="1.5" fill="{T["muted"]}" fill-opacity="{.7 if k < 5 else .2}"/>' for k in range(80))
    mx = bx + bw * 25 / 400
    tiles.append(f'<g>{segs}<g class="slide"><path d="M{mx:.1f},{by+14} l-6,10 h12 Z" fill="{T["red"]}"/>'
                 f'<text x="{mx + 12:.1f}" y="{by+25}" class="mono" font-size="10.5" font-weight="800" fill="{T["red"]}">#25 · TOP 6%</text></g>'
                 f'<text x="{bx+bw:.1f}" y="{by+25}" text-anchor="end" class="mono" font-size="10" fill="{T["muted"]}">400+ TEAMS</text></g>')
    # tile 2: accuracy ring
    x = 40 + tw + g
    rcx, rcy, r = x + tw - 66, y0 + 82, 40
    tiles.append(f'<circle cx="{rcx:.1f}" cy="{rcy}" r="{r}" fill="none" stroke="{T["line"]}" stroke-width="9"/>'
                 f'<circle cx="{rcx:.1f}" cy="{rcy}" r="{r}" fill="none" stroke="{T["blue2"]}" stroke-width="9" stroke-linecap="round" '
                 f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ*(1-.9682):.1f}" transform="rotate(-90 {rcx:.1f} {rcy})" class="ring"/>'
                 f'<text x="{rcx:.1f}" y="{rcy+4}" text-anchor="middle" class="mono" font-size="14" font-weight="800" fill="{T["text"]}">43</text>'
                 f'<text x="{rcx:.1f}" y="{rcy+18}" text-anchor="middle" class="mono" font-size="8.5" fill="{T["muted"]}">CLASSES</text>')
    # tile 3: test ticks lighting up
    x = 40 + 2 * (tw + g)
    tx0, ty0 = x + 26, y0 + 158
    ticks = "".join(f'<rect x="{tx0 + (k % 16)*12.5:.1f}" y="{ty0 + (k//16)*14}" width="10" height="10" rx="2.5" fill="{T["green"]}" class="tick"{dl(.5 + k*.04)}/>' for k in range(32))
    tiles.append(ticks + f'<text x="{x + tw - 26:.1f}" y="{ty0 + 9}" text-anchor="end" class="mono" font-size="10" font-weight="700" fill="{T["green"]}">✓ ALL PASSING</text>')
    body = f"""
{frame(T, W, H, "FIELD NOTES  ·  EVIDENCE LOG", "")}
<text x="{W-40}" y="44" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{T['muted']}">VERIFY, DON&#8217;T TRUST <tspan fill="{T['red']}">◆</tspan></text>
{''.join(tiles)}
"""
    return svg(W, H, body, css, sheet_defs(T, W, H), "Field notes: Top 25 of 400+ teams, 96.82% CNN accuracy, 421 passing tests")


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    print("Building assets:")
    for T in (DARK, LIGHT):
        jobs = [("ghost-protocol", hero), ("project-swachhvan", swachhvan), ("build-log", build_log), ("field-notes", field_notes)]
        jobs += [(f"op-{p['slug']}", (lambda T, p=p: op_card(T, p))) for p in OPS]
        for name, fn in jobs:
            f = OUT / f"{name}-{T['name']}.svg"
            f.write_text(fn(T), encoding="utf-8")
            print(f"  assets/{f.name}")
