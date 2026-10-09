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


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    print("Building assets:")
    for T in (DARK, LIGHT):
        for name, fn in [("ghost-protocol", hero), ("project-swachhvan", swachhvan), ("build-log", build_log)]:
            f = OUT / f"{name}-{T['name']}.svg"
            f.write_text(fn(T), encoding="utf-8")
            print(f"  assets/{f.name}")
