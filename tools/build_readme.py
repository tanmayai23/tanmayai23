"""Generates the "Hello World" light-theme SVG assets for the profile README.

Design language: Apple-style paper surfaces (#F5F5F7, hairlines, big type) with
Google's four colours used only as accents (sparkles, droplets, dots).

The header follows the hand-drawn sketch: a terminal card whose bottom edge melts
into drips, with sparkles scattered around it.

Run:  python tools/build_readme.py
Needs: Pillow (for the gallery photos). Brand icons live in tools/icons (simple-icons, CC0).
"""
import base64
import io
import math
import os
import re
from html import escape
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"
PHOTOS = ROOT / "assets" / "photos"
OUT = ROOT / "assets" / "hello"
# PREVIEW_DIR=... renders the final frame (no motion) somewhere else, for checking layouts
PREVIEW = os.environ.get("PREVIEW_DIR")
if PREVIEW:
    OUT = Path(PREVIEW)
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- tokens
INK, INK2, MUTED, HAIR = "#1D1D1F", "#424245", "#6E6E73", "#E3E3E8"
PAPER, SURFACE, WHITE = "#FBFBFD", "#F5F5F7", "#FFFFFF"
BLUE, RED, YELLOW, GREEN = "#4285F4", "#EA4335", "#FBBC04", "#34A853"
GOOGLE = [BLUE, RED, YELLOW, GREEN]

SANS = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Google Sans', 'Segoe UI Variable Display', 'Segoe UI', Inter, Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', 'Cascadia Code', Menlo, Consolas, 'Roboto Mono', monospace"

BASE_CSS = f"""
  text {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .up {{ animation: up .9s cubic-bezier(.2,.8,.2,1) both; }}
  .fade {{ animation: fade 1.2s ease both; }}
  .twinkle {{ animation: twinkle 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .spin {{ animation: spin 14s linear infinite; transform-box: fill-box; transform-origin: center; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .drop {{ animation: drop 3.6s cubic-bezier(.55,0,.9,.5) infinite; transform-box: fill-box; transform-origin: center top; }}
  .breathe {{ animation: breathe 3.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center top; }}
  .zoom {{ animation: zoom 18s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }}
  .ripple {{ animation: ripple 3.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes up {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .25; transform: scale(.55) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes drop {{ 0%,30% {{ opacity: 0; transform: translateY(0) scale(.4); }} 40% {{ opacity: 1; transform: translateY(0) scale(1); }}
                     85% {{ opacity: 1; transform: translateY(70px) scale(1,1.15); }} 100% {{ opacity: 0; transform: translateY(84px) scale(1.2,.6); }} }}
  @keyframes breathe {{ 0%,100% {{ transform: scaleY(1); }} 40% {{ transform: scaleY(1.07); }} }}
  @keyframes zoom {{ from {{ transform: scale(1); }} to {{ transform: scale(1.07); }} }}
  @keyframes ripple {{ 0% {{ opacity: .7; transform: scale(.2); }} 100% {{ opacity: 0; transform: scale(1.6); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def e(s):
    return escape(str(s), quote=True)


def dl(s):
    return f' style="animation-delay:{s:.2f}s"'


def tw(s, size, k=0.56):
    """Rough text width for the system sans at a given size (good enough for pills)."""
    narrow = sum(1 for c in s if c in "iljtf.,:;' |!·")
    wide = sum(1 for c in s if c in "mwMW@%")
    caps = sum(1 for c in s if c.isupper())
    return size * (k * len(s) - .28 * narrow + .3 * wide + .1 * caps)


def svg(w, h, body, label, css="", defs=""):
    if PREVIEW:
        css += "* { animation: none !important; }"
        body = body.replace('visibility="hidden"', "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><title>{e(label)}</title>'
            f'<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:<28} {len(content.encode()) / 1024:7.1f} KB")


def sparkle(x, y, s, fill, delay=0.0, cls="twinkle"):
    """Four-point concave star (the sketch's asterisks, rendered Gemini-style)."""
    d = f"M0,{-s} Q0,0 {s},0 Q0,0 0,{s} Q0,0 {-s},0 Q0,0 0,{-s}Z"
    return f'<g transform="translate({x},{y})"><path d="{d}" fill="{fill}" class="{cls}"{dl(delay)}/></g>'


def icon_path(slug):
    raw = (ICONS / f"{slug}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', raw).group(1)


def icon(slug, x, y, size, fill):
    k = size / 24
    return f'<path transform="translate({x},{y}) scale({k:.4f})" d="{icon_path(slug)}" fill="{fill}"/>'


def pill(x, y, text, fg, bg, size=13, pad=14, h=30, mono=False, weight=600):
    w = tw(text, size, .62 if mono else .56) + pad * 2
    cls = ' class="mono"' if mono else ""
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{bg}"/>'
            f'<text x="{x + w/2:.0f}" y="{y + h/2 + size*.36:.1f}" text-anchor="middle" font-size="{size}" '
            f'font-weight="{weight}" fill="{fg}"{cls}>{e(text)}</text>'), w


# ================================================================== HERO
def melt_path(x0, y0, x1, y1, r, drips):
    """Rounded card whose bottom edge melts into drips. drips: [(cx, half_width, length, bulb_r)]."""
    p = [f"M{x0 + r},{y0}", f"H{x1 - r}", f"Q{x1},{y0} {x1},{y0 + r}", f"V{y1 - r}", f"Q{x1},{y1} {x1 - r},{y1}"]
    for cx, w, L, br in sorted(drips, reverse=True):
        p += [f"H{cx + w}",
              f"C{cx + w*.35},{y1} {cx + br},{y1 + L*.35} {cx + br},{y1 + L}",
              f"A{br},{br} 0 0 1 {cx - br},{y1 + L}",
              f"C{cx - br},{y1 + L*.35} {cx - w*.35},{y1} {cx - w},{y1}"]
    p += [f"H{x0 + r}", f"Q{x0},{y1} {x0},{y1 - r}", f"V{y0 + r}", f"Q{x0},{y0} {x0 + r},{y0}", "Z"]
    return " ".join(p)


def typed(text, x, y, size, weight, fill, start, step, extra=""):
    """Per-character SMIL reveal so the proportional font keeps its natural spacing."""
    spans = "".join(
        f'<tspan visibility="hidden"{" fill=" + chr(34) + BLUE + chr(34) if c == "." and i == len(text) - 1 else ""}>{e(c)}<set attributeName="visibility" to="visible" '
        f'begin="{start + i*step:.2f}s" fill="freeze"/></tspan>' for i, c in enumerate(text))
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" letter-spacing="-1.5"{extra}>{spans}</text>'


def hero():
    W, H = 1200, 560
    x0, y0, x1, y1 = 40, 40, 1160, 400
    drips = [(250, 46, 70, 15), (520, 38, 118, 13), (580, 26, 40, 10), (865, 44, 92, 14), (1060, 30, 46, 11)]
    shape = melt_path(x0, y0, x1, y1, 30, drips)

    # falling droplets (one per long drip), in Google colours
    drops = "".join(
        f'<circle cx="{cx}" cy="{y1 + L + br + 8}" r="{br*.55:.1f}" fill="{c}" class="drop"{dl(i * .9)}/>'
        for i, ((cx, _, L, br), c) in enumerate(zip([drips[0], drips[1], drips[3], drips[4]], GOOGLE)))
    stars = "".join([
        sparkle(150, 470, 11, BLUE, 0), sparkle(395, 452, 7, YELLOW, .8), sparkle(700, 470, 12, RED, 1.6),
        sparkle(980, 505, 8, GREEN, .4), sparkle(1110, 470, 10, BLUE, 2.1), sparkle(25, 250, 8, GREEN, 1.2),
        sparkle(1180, 150, 9, YELLOW, 2.6), sparkle(330, 520, 6, RED, 1.9), sparkle(1180, 330, 6, BLUE, .6)])

    title_bar = (
        "".join(f'<circle cx="{78 + i*22}" cy="76" r="6.5" fill="{c}"/>' for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]))
        + f'<text x="600" y="81" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">tanmay — zsh — hello-world</text>'
        + f'<line x1="{x0}" y1="108" x2="{x1}" y2="108" stroke="{HAIR}"/>')

    # terminal tile, as drawn in the sketch
    tile = f"""
<g class="up"{dl(.1)}>
  <rect x="96" y="160" width="148" height="148" rx="36" fill="{INK}"/>
  <rect x="96" y="160" width="148" height="148" rx="36" fill="url(#tileSheen)"/>
  <path d="M132,206 L160,230 L132,254" fill="none" stroke="{WHITE}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="172" y="246" width="40" height="9" rx="4.5" fill="{GREEN}" class="blink"/>
</g>"""

    t1, t2 = "Hello World,", "I'm Tanmay."
    s1 = .5
    s2 = s1 + len(t1) * .09 + .35
    end = s2 + len(t2) * .09
    text = f"""
<text x="292" y="168" class="mono fade" font-size="16" fill="{MUTED}"{dl(.2)}>~ $ echo "$GREETING"</text>
{typed(t1, 288, 238, 70, 300, INK2, s1, .09)}
{typed(t2, 288, 318, 76, 700, INK, s2, .09)}
<g class="up"{dl(end + .45)}>
  <text x="292" y="362" font-size="19" fill="{MUTED}">GenAI &amp; NLP Engineer  <tspan fill="{HAIR}">/</tspan>  Founder, <tspan fill="{INK}" font-weight="600">NAXATRA AI</tspan>  <tspan fill="{HAIR}">/</tspan>  CS @ VIT Bhopal</text>
</g>"""

    status = f"""
<g class="fade"{dl(end + .8)}>
  <rect x="938" y="146" width="178" height="34" rx="17" fill="{WHITE}" stroke="{HAIR}"/>
  <circle cx="960" cy="163" r="5" fill="{GREEN}"/><circle cx="960" cy="163" r="5" fill="{GREEN}" class="ripple"/>
  <text x="974" y="168" font-size="13.5" font-weight="600" fill="{INK2}">Open to internships</text>
</g>"""

    defs = f"""
<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}"/><stop offset=".55" stop-color="{SURFACE}"/><stop offset="1" stop-color="#EDEDF2"/></linearGradient>
<linearGradient id="tileSheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="soft" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#1D1D1F" flood-opacity=".08"/></filter>"""
    body = f"""
<g filter="url(#soft)"><path d="{shape}" fill="url(#card)" stroke="{HAIR}" stroke-width="1.5"/></g>
{title_bar}{tile}{text}{status}{drops}{stars}"""
    return svg(W, H, body, "Hello World, I'm Tanmay — GenAI & NLP engineer, founder of NAXATRA AI, CS at VIT Bhopal", defs=defs)


# ================================================================== SECTION TITLES
def section(no, title, note):
    W, H = 1200, 96
    c = GOOGLE[(int(no) - 1) % 4]
    body = f"""
<g class="up">
  {sparkle(30, 50, 14, c, 0, "spin")}
  <text x="62" y="61" font-size="34" font-weight="700" letter-spacing="-.8" fill="{INK}">{e(title)}</text>
  <text x="{74 + tw(title, 34, .6):.0f}" y="61" font-size="17" fill="{MUTED}">{e(note)}</text>
  <text x="1184" y="58" text-anchor="end" class="mono" font-size="14" fill="{MUTED}">{no}</text>
  <line x1="16" y1="88" x2="1184" y2="88" stroke="{HAIR}" stroke-width="1.5"/>
  <line x1="16" y1="88" x2="96" y2="88" stroke="{c}" stroke-width="3" stroke-linecap="round"/>
</g>"""
    return svg(W, H, body, f"{no} — {title}")


# ================================================================== ABOUT
def about():
    W, H = 1200, 400
    now = [("Building", "AI products, LLM workflows and voice interfaces", BLUE),
           ("Exploring", "RAG, evaluation, fine-tuning and production NLP", RED),
           ("Leading", "NAXATRA AI — useful AI infrastructure for Bharat", YELLOW),
           ("Open to", "AI/ML & GenAI internships and ambitious collaborators", GREEN)]
    rows = "".join(
        f'<g class="up"{dl(.35 + i*.12)}><circle cx="672" cy="{110 + i*62}" r="6" fill="{c}"/>'
        f'<text x="692" y="{116 + i*62}" font-size="17" font-weight="700" fill="{INK}">{e(k)}</text>'
        f'<text x="692" y="{140 + i*62}" font-size="15.5" fill="{MUTED}">{e(v)}</text></g>'
        for i, (k, v, c) in enumerate(now))
    body = f"""
<rect x="16" y="10" width="1168" height="380" rx="30" fill="{SURFACE}"/>
<g class="up"{dl(.05)}>
  <text x="88" y="84" class="mono" font-size="14" letter-spacing="2" fill="{MUTED}">ABOUT</text>
  <text x="86" y="146" font-size="44" font-weight="700" letter-spacing="-1.4" fill="{INK}">I build AI that</text>
  <text x="86" y="200" font-size="44" font-weight="700" letter-spacing="-1.4" fill="{INK}">leaves the <tspan fill="{BLUE}">demo stage.</tspan></text>
</g>
<g class="up"{dl(.2)}>
  <text x="88" y="256" font-size="17" fill="{INK2}">Turning models, data and APIs into tools people actually use —</text>
  <text x="88" y="282" font-size="17" fill="{INK2}">shipped, measured, and improved after the first deploy.</text>
  <text x="88" y="338" font-size="15" font-style="italic" fill="{MUTED}">“Ideas are cheap. Useful systems are the work.”</text>
</g>
<line x1="626" y1="70" x2="626" y2="330" stroke="{HAIR}" stroke-width="1.5"/>
<text x="666" y="84" class="mono up" font-size="14" letter-spacing="2" fill="{MUTED}"{dl(.3)}>RIGHT NOW</text>
{rows}
{sparkle(1118, 58, 9, YELLOW, .5)}{sparkle(580, 352, 7, BLUE, 1.5)}"""
    return svg(W, H, body, "About: I build AI that leaves the demo stage. Building AI products, exploring RAG and evaluation, leading NAXATRA AI, open to AI/ML internships.")


# ================================================================== CONNECT PILLS
def gmail_icon(x, y, s):
    """Multicolour Gmail 'M' (simplified) — matches the sketch's (M) button."""
    k = s / 24
    return (f'<g transform="translate({x},{y}) scale({k:.4f})">'
            f'<path d="M1.6 5.5 L12 13.3 L22.4 5.5 V18.6 A1.6 1.6 0 0 1 20.8 20.2 H17.4 V10.9 L12 15 L6.6 10.9 V20.2 H3.2 A1.6 1.6 0 0 1 1.6 18.6 Z" fill="{RED}"/>'
            f'<path d="M1.6 5.5 V18.6 A1.6 1.6 0 0 0 3.2 20.2 H6.6 V10.9 Z" fill="{BLUE}"/>'
            f'<path d="M17.4 10.9 V20.2 H20.8 A1.6 1.6 0 0 0 22.4 18.6 V5.5 Z" fill="{GREEN}"/>'
            f'<path d="M22.4 5.5 L17.4 9.3 V4.8 L19.3 3.4 C20.6 2.4 22.4 3.3 22.4 4.9 Z" fill="{YELLOW}"/>'
            f'<path d="M1.6 5.5 V4.9 C1.6 3.3 3.4 2.4 4.7 3.4 L12 8.9 L17.4 4.8 V9.3 L12 13.3 Z" fill="#C5221F"/></g>')


def globe_icon(x, y, s, c):
    r = s / 2
    cx, cy = x + r, y + r
    return (f'<g fill="none" stroke="{c}" stroke-width="2"><circle cx="{cx}" cy="{cy}" r="{r-1}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r*.42:.1f}" ry="{r-1}"/><path d="M{x+1},{cy} H{x+s-1}"/></g>')


def connect_pill(kind):
    W, H = 280, 72
    spec = {
        "linkedin": ("LinkedIn", "in/tanmay-kala", lambda: icon("linkedin", 26, 22, 28, "#0A66C2")),
        "email": ("Gmail", "Say hello", lambda: gmail_icon(24, 20, 32)),
        "portfolio": ("Portfolio", "tanmaykala.dev", lambda: globe_icon(26, 22, 28, BLUE)),
        "github": ("GitHub", "@tanmayai23", lambda: icon("github", 26, 22, 28, INK)),
    }[kind]
    label, sub, ic = spec
    body = f"""
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="{(H-2)/2}" fill="{WHITE}" stroke="{HAIR}" stroke-width="1.5"/>
{ic()}
<text x="70" y="33" font-size="16.5" font-weight="700" fill="{INK}">{e(label)}</text>
<text x="70" y="53" font-size="13.5" fill="{MUTED}">{e(sub)}</text>
<circle cx="{W-36}" cy="{H/2}" r="16" fill="{SURFACE}"/>
<path d="M{W-41},{H/2+5} L{W-31},{H/2-5} M{W-39},{H/2-5} H{W-31} V{H/2+3}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>"""
    return svg(W, H, body, f"{label} — {sub}")


# ================================================================== TECH STACK
STACK = [
    ("Languages", [("python", "Python", "#3776AB"), ("typescript", "TypeScript", "#3178C6"),
                   ("javascript", "JavaScript", "#E8C400")]),
    ("AI · ML", [("pytorch", "PyTorch", "#EE4C2C"), ("tensorflow", "TensorFlow", "#FF6F00"),
                 ("huggingface", "Transformers", "#FFB000"), ("opencv", "OpenCV", "#5C3EE8"),
                 ("googlegemini", "Gemini", "#8E75B2")]),
    ("Web · Backend", [("react", "React", "#149ECA"), ("nextdotjs", "Next.js", INK), ("nodedotjs", "Node.js", "#5FA04E"),
                       ("fastapi", "FastAPI", "#009688"), ("flask", "Flask", INK)]),
    ("Cloud · Tools", [("docker", "Docker", "#2496ED"), ("amazonwebservices", "AWS", "#FF9900"),
                       ("googlecloud", "Google Cloud", BLUE), ("vercel", "Vercel", INK), ("git", "Git", "#F05032"),
                       ("github", "GitHub", INK), ("sqlite", "SQLite", "#003B57")]),
]
CAPS = ["LLMs", "RAG", "AI Agents", "NLP", "Speech · Whisper", "Computer Vision", "Vector Search", "Model Evaluation"]


def stack():
    W = 1200
    row_h, top = 128, 40
    H = top + row_h * len(STACK) + 130
    parts = [f'<rect x="16" y="10" width="1168" height="{H-20}" rx="30" fill="{SURFACE}"/>']
    n = 0
    for r, (cat, items) in enumerate(STACK):
        y = top + r * row_h
        if r:
            parts.append(f'<line x1="80" y1="{y-4}" x2="1120" y2="{y-4}" stroke="{HAIR}"/>')
        parts.append(f'<g class="up"{dl(r*.1)}><circle cx="86" cy="{y+56}" r="5" fill="{GOOGLE[r]}"/>'
                     f'<text x="102" y="{y+62}" font-size="17" font-weight="700" fill="{INK}">{e(cat)}</text></g>')
        for i, (slug, name, col) in enumerate(items):
            x = 290 + i * 122
            parts.append(
                f'<g class="up"{dl(.15 + n*.04)}>'
                f'<rect x="{x}" y="{y+14}" width="68" height="68" rx="18" fill="{WHITE}" stroke="{HAIR}"/>'
                f'{icon(slug, x+19, y+33, 30, col)}'
                f'<text x="{x+34}" y="{y+106}" text-anchor="middle" font-size="13" fill="{INK2}">{e(name)}</text></g>')
            n += 1
    y = top + row_h * len(STACK) + 16
    parts.append(f'<line x1="80" y1="{y-4}" x2="1120" y2="{y-4}" stroke="{HAIR}"/>')
    parts.append(f'<g class="up"{dl(.6)}><circle cx="86" cy="{y+40}" r="5" fill="{INK}"/>'
                 f'<text x="102" y="{y+46}" font-size="17" font-weight="700" fill="{INK}">Focus areas</text></g>')
    x, yy = 290, y + 22
    for i, cap in enumerate(CAPS):
        p, w = pill(x, yy, cap, INK2, WHITE, size=14, pad=16, h=36, weight=500)
        p = p.replace('fill="#FFFFFF"/>', f'fill="#FFFFFF" stroke="{HAIR}"/>', 1)
        if x + w > 1120:
            x, yy = 290, yy + 46
            p, w = pill(x, yy, cap, INK2, WHITE, size=14, pad=16, h=36, weight=500)
            p = p.replace('fill="#FFFFFF"/>', f'fill="#FFFFFF" stroke="{HAIR}"/>', 1)
        parts.append(f'<g class="up"{dl(.7 + i*.05)}>{p}</g>')
        x += w + 10
    H = max(H, yy + 36 + 34)
    parts[0] = f'<rect x="16" y="10" width="1168" height="{H-20}" rx="30" fill="{SURFACE}"/>'
    names = ", ".join(n for _, it in STACK for _, n, _ in it)
    return svg(W, H, "".join(parts), f"Tech stack: {names}. Focus: {', '.join(CAPS)}")


# ================================================================== PROJECTS
def viz(kind, cx, cy):
    """Tiny abstract illustrations, one per project, in Google colours."""
    if kind == "map":
        pts = [(-90, -40), (-30, 10), (40, -30), (90, 30), (-60, 60), (20, 70)]
        lines = f'<path d="M{cx-90},{cy-40} L{cx-30},{cy+10} L{cx+40},{cy-30} L{cx+90},{cy+30}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-dasharray="6 8" stroke-linecap="round"/>'
        dots = "".join(f'<circle cx="{cx+x}" cy="{cy+y}" r="{9 if i % 2 else 6}" fill="{GOOGLE[i % 4]}"/>'
                       f'<circle cx="{cx+x}" cy="{cy+y}" r="14" fill="{GOOGLE[i % 4]}" class="ripple"{dl(i*.5)}/>'
                       for i, (x, y) in enumerate(pts))
        return lines + dots
    if kind == "wave":
        return "".join(f'<rect x="{cx-70+i*14}" y="{cy - h/2}" width="7" height="{h}" rx="3.5" fill="{GOOGLE[i % 4]}" class="breathe"{dl(i*.15)}/>'
                       for i, h in enumerate([16, 34, 58, 82, 48, 96, 64, 36, 70, 30, 18]))
    if kind == "agent":
        nodes = [(0, 0, INK), (-62, -42, BLUE), (62, -42, RED), (-62, 42, YELLOW), (62, 42, GREEN)]
        ls = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+x}" y2="{cy+y}" stroke="{HAIR}" stroke-width="3"/>' for x, y, _ in nodes[1:])
        ns = "".join(f'<circle cx="{cx+x}" cy="{cy+y}" r="{20 if not i else 13}" fill="{c}" class="{"" if not i else "twinkle"}"{dl(i*.4)}/>'
                     for i, (x, y, c) in enumerate(nodes))
        return ls + ns + f'<text x="{cx}" y="{cy+5}" text-anchor="middle" class="mono" font-size="13" font-weight="700" fill="{WHITE}">AI</text>'
    if kind == "grid":
        out = []
        for r in range(5):
            for c in range(5):
                on = (r * 5 + c) in (6, 7, 8, 11, 13, 16, 17, 18, 12)
                col = GOOGLE[(r + c) % 4] if on else HAIR
                out.append(f'<rect x="{cx-70+c*29}" y="{cy-70+r*29}" width="24" height="24" rx="6" fill="{col}"'
                           + (f' class="twinkle"{dl((r+c)*.25)}' if on else "") + "/>")
        return "".join(out)
    if kind == "route":
        return (f'<path d="M{cx-80},{cy+60} C{cx-40},{cy-10} {cx+10},{cy+70} {cx+60},{cy-30}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>'
                f'<circle cx="{cx-80}" cy="{cy+60}" r="8" fill="{BLUE}"/>'
                f'<path transform="translate({cx+60},{cy-58})" d="M0,30 C-16,12 -16,-2 -16,-2 A16,16 0 1 1 16,-2 C16,-2 16,12 0,30Z" fill="{RED}"/>'
                f'<circle cx="{cx+60}" cy="{cy-60}" r="6" fill="{WHITE}"/>'
                + sparkle(cx - 10, cy - 50, 9, YELLOW, .3) + sparkle(cx + 10, cy + 60, 7, GREEN, 1.4))
    return ""


PROJECTS = [
    dict(slug="swachhvan", tag="FLAGSHIP · LIVE", tagc=GREEN, title="SwachhVan", viz="map",
         sub="AI smart-sanitation platform",
         desc=["Forecasts sanitation demand across city zones and", "dispatches vans before the problem shows up."],
         metrics=[("Top 25", "of 400+ teams"), ("−60%", "dispatch planning"), ("100+", "simulated bookings")],
         tech="Python · Forecasting · Next.js · Maps"),
    dict(slug="heydude", tag="VOICE AI", tagc=BLUE, title="Hey Dude", viz="wave",
         sub="Voice-first desktop assistant",
         desc=["Gemini conversation, face recognition,", "hotword detection and automation."],
         metric="<500 ms hotword", tech="Python · Gemini · OpenCV · SQLite"),
    dict(slug="marketbuddy", tag="AGENTIC AI", tagc=RED, title="Market Buddy", viz="agent",
         sub="Autonomous voice agent · CALL-E",
         desc=["Hackathon voice agent built for", "dependable conversational workflows."],
         metric="421 passing tests", tech="Agents · TypeScript · Testing"),
    dict(slug="trafficsign", tag="COMPUTER VISION", tagc=YELLOW, title="TrafficSignNet", viz="grid",
         sub="43-class CNN from scratch",
         desc=["Traffic-sign recognition in PyTorch,", "CPU-only and CLI-driven."],
         metric="96.82% accuracy", tech="Python · PyTorch · CNN"),
    dict(slug="travel", tag="NLP · GEO · LIVE", tagc=GREEN, title="Hey, where next?", viz="route",
         sub="AI travel assist",
         desc=["Surfaces interesting places along", "your journey, wherever you are."],
         metric="POIs within 10 km", tech="Python · Gemini API · Geolocation"),
]


def project_flagship(p):
    W, H = 1200, 340
    mets = "".join(
        f'<g class="up"{dl(.45 + i*.1)}><text x="{88 + i*190}" y="262" font-size="34" font-weight="700" letter-spacing="-1" fill="{INK}">{e(v)}</text>'
        f'<text x="{90 + i*190}" y="288" font-size="14" fill="{MUTED}">{e(l)}</text></g>'
        for i, (v, l) in enumerate(p["metrics"]))
    tag, _ = pill(88, 52, p["tag"], p["tagc"], WHITE, size=12, pad=14, h=28, mono=True, weight=700)
    body = f"""
<rect x="16" y="10" width="1168" height="320" rx="30" fill="{SURFACE}"/>
<g class="up">{tag}</g>
<g class="up"{dl(.1)}><text x="86" y="138" font-size="54" font-weight="700" letter-spacing="-1.8" fill="{INK}">{e(p['title'])}</text>
<text x="{96 + tw(p['title'], 54, .56):.0f}" y="138" font-size="20" fill="{MUTED}">{e(p['sub'])}</text></g>
<g class="up"{dl(.25)}>{"".join(f'<text x="88" y="{176 + i*25}" font-size="17" fill="{INK2}">{e(t)}</text>' for i, t in enumerate(p['desc']))}</g>
{mets}
<rect x="720" y="40" width="400" height="260" rx="24" fill="{WHITE}" stroke="{HAIR}"/>
<g>{viz(p['viz'], 920, 165)}</g>
<text x="744" y="284" class="mono" font-size="12" fill="{MUTED}">{e(p['tech'])}</text>
<text x="1100" y="284" text-anchor="end" font-size="13" font-weight="700" fill="{BLUE}">Open live ↗</text>"""
    return svg(W, H, body, f"{p['title']} — {p['sub']}. " + ", ".join(f"{v} {l}" for v, l in p["metrics"]))


def project_card(p):
    W, H = 590, 340
    tag, _ = pill(36, 40, p["tag"], p["tagc"], WHITE, size=11.5, pad=12, h=26, mono=True, weight=700)
    met, _ = pill(36, 236, p["metric"], WHITE, INK, size=13, pad=14, h=30, weight=600)
    body = f"""
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="28" fill="{SURFACE}"/>
<g class="up">{tag}</g>
<g class="up"{dl(.1)}><text x="34" y="114" font-size="34" font-weight="700" letter-spacing="-1" fill="{INK}">{e(p['title'])}</text>
<text x="36" y="142" font-size="15" fill="{MUTED}">{e(p['sub'])}</text></g>
<g class="up"{dl(.2)}>{"".join(f'<text x="36" y="{180 + i*22}" font-size="14.5" fill="{INK2}">{e(t)}</text>' for i, t in enumerate(p['desc']))}</g>
<g class="up"{dl(.3)}>{met}</g>
<text x="36" y="298" class="mono" font-size="11.5" fill="{MUTED}">{e(p['tech'])}</text>
<g transform="translate(0,0)">{viz(p['viz'], 470, 120)}</g>
<circle cx="{W-50}" cy="{H-50}" r="18" fill="{WHITE}" stroke="{HAIR}"/>
<path d="M{W-56},{H-44} L{W-44},{H-56} M{W-54},{H-56} H{W-44} V{H-46}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>"""
    return svg(W, H, body, f"{p['title']} — {p['sub']} · {p['metric']}")


# ================================================================== ACHIEVEMENT GALLERY
GALLERY = [
    dict(photo="google-ambassador.jpg", no="01", org="GOOGLE", c=BLUE, title="Google Student",
         title2="Ambassador 2026", lines=["Selected for the Gemini Student", "Ambassador Program. Earned the", "Explorer & Navigator badges."],
         chip="#TeamGemini", focus=.30),
    dict(photo="ieee-track-winner.jpg", no="02", org="IEEE", c=RED, title="IEEE Track", title2="Winner",
         lines=["Took the track-winner trophy", "home, with a stack of IEEE", "certificates to go with it."],
         chip="Track Winner", focus=.28),
    dict(photo="hack-for-green-bharat.jpg", no="03", org="MICROSOFT · UNSTOP", c=GREEN, title="Hack for", title2="Green Bharat",
         lines=["SwachhVan finished in the", "Top 25 of 400+ teams at", "Microsoft's sustainability hack."],
         chip="Top 25 / 400+", focus=.30),
    dict(photo="google-go-bananas.jpg", no="04", org="GOOGLE GEMINI", c=YELLOW, title="Go Bananas", title2="with Gemini",
         lines=["Recognised by the Google", "Gemini team in the Go Bananas", "campaign, swag kit included."],
         chip="Nano Banana", focus=.22),
]


def photo_b64(name, w, h, focus):
    im = Image.open(PHOTOS / name)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(.5, focus))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def achievement(a):
    W, H = 590, 420
    px, py, pw, ph = 22, 22, 260, 376
    b64 = photo_b64(a["photo"], pw * 2, ph * 2, a["focus"])
    chip, _ = pill(312, 324, a["chip"], WHITE, INK, size=12.5, pad=13, h=28, weight=600)
    body = f"""
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="32" fill="{SURFACE}"/>
<g clip-path="url(#ph)">
  <image href="data:image/jpeg;base64,{b64}" x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice" class="zoom"/>
  <rect x="{px}" y="{py + ph - 90}" width="{pw}" height="90" fill="url(#shade)"/>
</g>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22" fill="none" stroke="#000" stroke-opacity=".06"/>
<text x="{px + 18}" y="{py + ph - 20}" class="mono" font-size="13" font-weight="700" fill="{WHITE}">{a['no']} / 04</text>
<g class="up"{dl(.1)}>
  <circle cx="318" cy="66" r="6" fill="{a['c']}"/>
  <text x="332" y="71" class="mono" font-size="12" font-weight="700" letter-spacing="1.4" fill="{MUTED}">{e(a['org'])}</text>
  <text x="310" y="124" font-size="31" font-weight="700" letter-spacing="-.9" fill="{INK}">{e(a['title'])}</text>
  <text x="310" y="160" font-size="31" font-weight="700" letter-spacing="-.9" fill="{INK}">{e(a['title2'])}</text>
</g>
<g class="up"{dl(.25)}>{"".join(f'<text x="312" y="{206 + i*24}" font-size="15" fill="{INK2}">{e(t)}</text>' for i, t in enumerate(a['lines']))}</g>
<g class="up"{dl(.4)}>{chip}</g>
{sparkle(548, 54, 10, a['c'], .3)}"""
    defs = (f'<clipPath id="ph"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22"/></clipPath>'
            f'<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>')
    return svg(W, H, body, f"Achievement {a['no']}: {a['title']} {a['title2']} — {' '.join(a['lines'])}", defs=defs)


# ================================================================== FOOTER
def footer():
    W, H = 1200, 300
    body = f"""
<rect x="16" y="40" width="1168" height="240" rx="30" fill="{INK}"/>
<rect x="16" y="40" width="1168" height="240" rx="30" fill="url(#glow)"/>
<g class="up">
  <text x="600" y="134" text-anchor="middle" font-size="52" font-weight="700" letter-spacing="-1.8" fill="{WHITE}">Let's connect.</text>
  <text x="600" y="176" text-anchor="middle" font-size="18" fill="#A1A1A6">Building something consequential with AI? Let's compare notes.</text>
</g>
<g class="up"{dl(.3)}>
  <text x="600" y="232" text-anchor="middle" class="mono" font-size="15" fill="#F5F5F7">tanmaykala171206@gmail.com<tspan fill="{GREEN}" class="blink"> ▍</tspan></text>
</g>
{"".join(sparkle(x, y, s, c, d) for x, y, s, c, d in [(120, 110, 10, BLUE, 0), (1080, 100, 12, YELLOW, .7), (190, 240, 7, GREEN, 1.4), (1010, 236, 8, RED, 2.1)])}"""
    defs = (f'<radialGradient id="glow" cx=".5" cy="1.1" r=".75"><stop offset="0" stop-color="{BLUE}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>')
    return svg(W, H, body, "Let's connect — tanmaykala171206@gmail.com", defs=defs)


if __name__ == "__main__":
    print("Building assets/hello:")
    write("hero.svg", hero())
    write("about.svg", about())
    for no, title, note in [("01", "About", "the short version"), ("02", "Tech stack", "tools I ship with"),
                            ("03", "Projects", "selected work"), ("04", "Achievements", "moments worth framing"),
                            ("05", "Commit graph", "the daily practice")]:
        write(f"section-{no}.svg", section(no, title, note))
    for k in ["linkedin", "email", "portfolio", "github"]:
        write(f"connect-{k}.svg", connect_pill(k))
    write("stack.svg", stack())
    write(f"project-{PROJECTS[0]['slug']}.svg", project_flagship(PROJECTS[0]))
    for p in PROJECTS[1:]:
        write(f"project-{p['slug']}.svg", project_card(p))
    for a in GALLERY:
        write(f"achievement-{a['no']}.svg", achievement(a))
    write("footer.svg", footer())
