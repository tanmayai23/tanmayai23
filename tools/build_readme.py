"""Generates the "Hello World" light-theme SVG assets for the profile README.

Design language: Apple-style paper surfaces (#F5F5F7, hairlines, big type) with
Google's four colours used only as accents (sparkles, droplets, dots).
The header follows the hand-drawn sketch: a terminal card whose bottom edge melts
into drips, with sparkles scattered around it — and sparkles carry on down the page.

Typography: Geist (display + text), Instrument Serif Italic (editorial accents) and
Geist Mono (code). Each SVG embeds a WOFF subset of exactly the glyphs it uses, so
GitHub renders the same type for every viewer. Widths are measured from the fonts.

Run:  python tools/build_readme.py
      PREVIEW_DIR=some/dir python tools/build_readme.py   # final frame, no motion
Needs: Pillow, fontTools. Icons: tools/icons (simple-icons, CC0). Fonts: tools/fonts (OFL).
"""
import base64
import io
import os
import re
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"
FONTS = Path(__file__).resolve().parent / "fonts"
PHOTOS = ROOT / "assets" / "photos"
OUT = ROOT / "assets" / "hello"
PREVIEW = os.environ.get("PREVIEW_DIR")
if PREVIEW:
    OUT = Path(PREVIEW)
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- tokens
INK, INK2, MUTED, HAIR = "#1D1D1F", "#424245", "#6E6E73", "#E3E3E8"
SURFACE, WHITE = "#F5F5F7", "#FFFFFF"
BLUE, RED, YELLOW, GREEN = "#4285F4", "#EA4335", "#FBBC04", "#34A853"
GOOGLE = [BLUE, RED, YELLOW, GREEN]

STACKS = {
    "sans": "TKSans, -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Inter, Roboto, Arial, sans-serif",
    "serif": "TKSerif, 'Instrument Serif', 'New York', Georgia, 'Times New Roman', serif",
    "mono": "TKMono, 'Geist Mono', 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace",
}
FONT_FILES = {"sans": "Geist.ttf", "mono": "GeistMono.ttf", "serif": "InstrumentSerif-Italic.ttf"}
FAMILY = {"sans": "TKSans", "mono": "TKMono", "serif": "TKSerif"}

BASE_CSS = f"""
  text {{ font-family: {STACKS['sans']}; font-kerning: normal; text-rendering: geometricPrecision; }}
  .mono {{ font-family: {STACKS['mono']}; }}
  .serif {{ font-family: {STACKS['serif']}; font-style: italic; font-weight: 400; }}
  .up {{ animation: up .9s cubic-bezier(.2,.8,.2,1) both; }}
  .fade {{ animation: fade 1.2s ease both; }}
  .twinkle {{ animation: twinkle 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .glint {{ animation: glint 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .spin {{ animation: spin 14s linear infinite; transform-box: fill-box; transform-origin: center; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .drop {{ animation: drop 3.6s cubic-bezier(.55,0,.9,.5) infinite; transform-box: fill-box; transform-origin: center top; }}
  .breathe {{ animation: breathe 3.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .zoom {{ animation: zoom 18s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }}
  .ripple {{ animation: ripple 3.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes up {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .3; transform: scale(.55) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
  @keyframes glint {{ 0%,100% {{ opacity: 0; transform: scale(.2); }} 50% {{ opacity: 1; transform: scale(1); }} }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes drop {{ 0%,30% {{ opacity: 0; transform: translateY(0) scale(.4); }} 40% {{ opacity: 1; transform: translateY(0) scale(1); }}
                     85% {{ opacity: 1; transform: translateY(70px) scale(1,1.15); }} 100% {{ opacity: 0; transform: translateY(84px) scale(1.2,.6); }} }}
  .fall {{ animation: fall 3.6s cubic-bezier(.55,0,.9,.5) infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes fall {{ 0%,20% {{ opacity: 0; transform: translateY(0) scale(.6); }} 35% {{ opacity: 1; transform: translateY(6px) scale(1); }}
                     80% {{ opacity: 1; transform: translateY(54px) scale(1,1.15); }} 92%,100% {{ opacity: 0; transform: translateY(64px) scale(1.3,.4); }} }}
  @keyframes breathe {{ 0%,100% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(.55); }} }}
  @keyframes zoom {{ from {{ transform: scale(1); }} to {{ transform: scale(1.07); }} }}
  @keyframes ripple {{ 0% {{ opacity: .7; transform: scale(.2); }} 100% {{ opacity: 0; transform: scale(1.6); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


# ================================================================== FONTS
_instances, _used = {}, {}


def _font(fam, w):
    """Static instance of the variable font at a weight, kept as bytes (subsetting mutates fonts)."""
    key = (fam, w if fam != "serif" else 400)
    if key not in _instances:
        f = TTFont(FONTS / FONT_FILES[fam])
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": key[1]})
        buf = io.BytesIO()
        f.save(buf)
        f = TTFont(io.BytesIO(buf.getvalue()))
        _instances[key] = (buf.getvalue(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _instances[key]


def measure(text, size, fam="sans", w=400, ls=0.0):
    _, cmap, hmtx, upm = _font(fam, w)
    adv = sum(hmtx[cmap.get(ord(c), cmap[32])][0] for c in text)
    return adv * size / upm + ls * len(text)


def use(fam, w, text):
    key = (fam, 400 if fam == "serif" else w)
    missing = {c for c in text if ord(c) not in _font(*key)[1]}
    assert not missing, f"{fam} has no glyph for {missing!r}"
    _used.setdefault(key, set()).update(text)


def font_css():
    faces = []
    for (fam, w), chars in sorted(_used.items()):
        chars = "".join(sorted(chars | {" "}))
        data = _font(fam, w)[0]
        f = TTFont(io.BytesIO(data))
        opt = subset.Options()
        opt.layout_features = ["kern", "liga", "calt", "ss01"]
        opt.hinting = False
        opt.desubroutinize = True
        opt.name_IDs = [1, 2]
        opt.flavor = "woff"
        opt.drop_tables += ["meta"]
        s = subset.Subsetter(opt)
        s.populate(text=chars)
        s.subset(f)
        f.flavor = "woff"
        buf = io.BytesIO()
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        style = "italic" if fam == "serif" else "normal"
        faces.append(f"@font-face {{ font-family: {FAMILY[fam]}; font-weight: {w}; font-style: {style}; "
                     f"src: url(data:font/woff;base64,{b64}) format('woff'); }}")
    _used.clear()
    return "".join(faces)


# ================================================================== PRIMITIVES
def e(s):
    return escape(str(s), quote=True)


def dl(s):
    return f' style="animation-delay:{s:.2f}s"'


def T(x, y, runs, size, w=400, fill=INK, fam="sans", anchor=None, ls=0.0, cls="", extra=""):
    """Text element. runs: str, or [(text, {fam, w, fill, size})] for mixed sans/serif lines."""
    if isinstance(runs, str):
        runs = [(runs, {})]
    out = []
    for txt, o in runs:
        f2 = o.get("fam", fam)
        w2 = o.get("w", w)
        use(f2, w2, txt)
        attrs = ""
        if f2 != fam:
            attrs += f' class="{f2}"'
        if "w" in o:
            attrs += f' font-weight="{o["w"]}"'
        if "fill" in o:
            attrs += f' fill="{o["fill"]}"'
        if "size" in o:
            attrs += f' font-size="{o["size"]}"'
        out.append(f"<tspan{attrs}>{e(txt)}</tspan>" if attrs else e(txt))
    classes = " ".join(c for c in [fam if fam != "sans" else "", cls] if c)
    a = f' text-anchor="{anchor}"' if anchor else ""
    c = f' class="{classes}"' if classes else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{w}" fill="{fill}"{a}{l}{c}{extra}>{"".join(out)}</text>'


def width(runs, size, w=400, fam="sans", ls=0.0):
    if isinstance(runs, str):
        runs = [(runs, {})]
    return sum(measure(t, o.get("size", size), o.get("fam", fam), o.get("w", w), ls) for t, o in runs)


def svg(w, h, body, label, css="", defs=""):
    if PREVIEW:
        css += "* { animation: none !important; }"
        body = body.replace('visibility="hidden"', "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><title>{e(label)}</title>'
            f'<style>{font_css()}{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:<28} {len(content.encode()) / 1024:7.1f} KB")


def sparkle(x, y, s, fill, delay=0.0, cls="twinkle"):
    """Four-point concave star (the sketch's asterisks, rendered Gemini-style)."""
    d = f"M0,{-s} Q0,0 {s},0 Q0,0 0,{s} Q0,0 {-s},0 Q0,0 0,{-s}Z"
    return f'<g transform="translate({x},{y})"><path d="{d}" fill="{fill}" class="{cls}"{dl(delay)}/></g>'


SPARKLE_SCALE = 1.6


def sparkles(spots):
    """spots: [(x, y, size, colour_index_or_hex, delay)] — colour int picks a Google colour."""
    out = []
    for x, y, s, c, d in spots:
        col = GOOGLE[c % 4] if isinstance(c, int) else c
        out.append(sparkle(x, y, round(s * SPARKLE_SCALE, 1), col, d, "glint" if s <= 5 else "twinkle"))
    return "".join(out)


def icon_path(slug):
    raw = (ICONS / f"{slug}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', raw).group(1)


def icon(slug, x, y, size, fill):
    return f'<path transform="translate({x},{y}) scale({size / 24:.4f})" d="{icon_path(slug)}" fill="{fill}"/>'


def pill(x, y, text, fg, bg, size=13, pad=14, h=30, fam="sans", w=600, ls=0.0, stroke=None):
    pw = width(text, size, w, fam, ls) + pad * 2
    st = f' stroke="{stroke}"' if stroke else ""
    return (f'<rect x="{x:.1f}" y="{y}" width="{pw:.1f}" height="{h}" rx="{h/2}" fill="{bg}"{st}/>'
            + T(x + pw / 2, y + h / 2 + size * .35, text, size, w, fg, fam, "middle", ls)), pw


def arrow(cx, cy, r=18, bg=WHITE):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{bg}" stroke="{HAIR}"/>'
            f'<path d="M{cx-6},{cy+6} L{cx+6},{cy-6} M{cx-4},{cy-6} H{cx+6} V{cy+4}" fill="none" stroke="{INK}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')


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


def typed(text, x, y, size, w, fill, start, step, fam="sans", ls=0.0, accent_last=None):
    """Per-character SMIL reveal so the font keeps its natural spacing."""
    use(fam, w, text)
    spans = []
    for i, c in enumerate(text):
        f = f' fill="{accent_last}"' if accent_last and i == len(text) - 1 else ""
        spans.append(f'<tspan visibility="hidden"{f}>{e(c)}<set attributeName="visibility" to="visible" '
                     f'begin="{start + i*step:.2f}s" fill="freeze"/></tspan>')
    cls = f' class="{fam}"' if fam != "sans" else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'letter-spacing="{ls}"{cls}>{"".join(spans)}</text>')


def melting_terminal(*, window, prompt, line1, line2, pieces, status, drips, stars, label, H=600, flip=False):
    """The sketch's melting terminal card. The header drips downward; the footer is flipped so its
    drips rise from the top edge, with drops falling onto the tips (as in the second sketch)."""
    W = 1200
    x0, y0, x1, y1 = 40, 40, 1160, 420
    shape = melt_path(x0, y0, x1, y1, 30, drips)
    long_drips = sorted(drips, key=lambda d: -d[2])[:4]
    off = H - y1 - y0 if flip else 0  # content shift so the card sits below the upward drips
    if flip:
        drops = "".join(
            f'<circle cx="{cx}" cy="{max(H - (y1 + L + br) - 66, br + 6)}" r="{br*.55:.1f}" fill="{c}" class="fall"{dl(i * .9)}/>'
            for i, ((cx, _, L, br), c) in enumerate(zip(sorted(long_drips), GOOGLE)))
        # stars outside the card mirror to the other side; glints inside move with the card
        stars = [(x, H - y if (y > y1 or y < y0) else y + off, sz, c, d) for x, y, sz, c, d in stars]
    else:
        drops = "".join(
            f'<circle cx="{cx}" cy="{y1 + L + br + 8}" r="{br*.55:.1f}" fill="{c}" class="drop"{dl(i * .9)}/>'
            for i, ((cx, _, L, br), c) in enumerate(zip(sorted(long_drips), GOOGLE)))

    title_bar = (
        "".join(f'<circle cx="{78 + i*22}" cy="76" r="6.5" fill="{c}"/>' for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]))
        + T(600, 81, window, 13, 500, MUTED, "mono", "middle")
        + f'<line x1="{x0}" y1="108" x2="{x1}" y2="108" stroke="{HAIR}"/>')

    tile = f"""
<g class="up"{dl(.1)}>
  <rect x="96" y="168" width="156" height="156" rx="38" fill="{INK}"/>
  <rect x="96" y="168" width="156" height="156" rx="38" fill="url(#tileSheen)"/>
  <path d="M134,216 L163,242 L134,268" fill="none" stroke="{WHITE}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="176" y="258" width="42" height="10" rx="5" fill="{GREEN}" class="blink"/>
</g>"""

    s1 = .5
    s2 = s1 + len(line1) * .09 + .35
    end = s2 + len(line2) * .09
    # subtitle pieces separated by sparkles, laid out with measured widths
    sx, sub = 296, ""
    for i, runs in enumerate(pieces):
        if i:
            sub += sparkle(sx + 20, 375, 9, GOOGLE[i], i * .7)
            sx += 40
        sub += T(sx, 382, runs, 19, 400, MUTED)
        sx += width(runs, 19)
    text = f"""
{T(296, 172, prompt, 15, 400, MUTED, "mono", cls="fade", extra=dl(.2))}
{typed(line1, 292, 246, 84, 400, INK2, s1, .09, "serif", -1)}
{typed(line2, 290, 330, 88, 700, INK, s2, .09, "sans", -4.2, accent_last=BLUE)}
<g class="up"{dl(end + .45)}>{sub}</g>"""

    bw = width(status, 13.5, 500) + 46
    badge = f"""
<g class="fade"{dl(end + .8)}>
  <rect x="{1116 - bw:.1f}" y="140" width="{bw:.1f}" height="34" rx="17" fill="{WHITE}" stroke="{HAIR}"/>
  <circle cx="{1116 - bw + 20:.1f}" cy="157" r="5" fill="{GREEN}"/><circle cx="{1116 - bw + 20:.1f}" cy="157" r="5" fill="{GREEN}" class="ripple"/>
  {T(1116 - bw + 34, 161.5, status, 13.5, 500, INK2)}
</g>"""

    defs = f"""
<linearGradient id="card" x1="0" y1="{1 if flip else 0}" x2="0" y2="{0 if flip else 1}"><stop offset="0" stop-color="{WHITE}"/><stop offset=".55" stop-color="{SURFACE}"/><stop offset="1" stop-color="#EDEDF2"/></linearGradient>
<linearGradient id="tileSheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="soft" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#1D1D1F" flood-opacity=".08"/></filter>"""
    body = f"""
<g filter="url(#soft)"><path d="{shape}" fill="url(#card)" stroke="{HAIR}" stroke-width="1.5"{f' transform="translate(0,{H}) scale(1,-1)"' if flip else ""}/></g>
<g transform="translate(0,{off})">{title_bar}{tile}{text}{badge}</g>{drops}{sparkles(stars)}"""
    return svg(W, H, body, label, defs=defs)


def hero():
    return melting_terminal(
        window="tanmay — zsh — hello-world", prompt='~ $ echo "$GREETING"',
        line1="Hello World,", line2="I'm Tanmay.",
        pieces=[[("GenAI & NLP Engineer", {})], [("Founder, ", {}), ("NAXATRA AI", {"fill": INK, "w": 600})],
                [("CS @ VIT Bhopal", {})]],
        status="Open to internships",
        drips=[(250, 46, 70, 15), (520, 38, 118, 13), (580, 26, 40, 10), (865, 44, 92, 14), (1060, 30, 46, 11)],
        stars=[(150, 492, 11, 0, 0), (395, 472, 7, 2, .8), (700, 494, 13, 1, 1.6), (980, 528, 8, 3, .4),
               (1110, 492, 10, 0, 2.1), (22, 250, 9, 3, 1.2), (1180, 150, 10, 2, 2.6), (330, 550, 6, 1, 1.9),
               (1180, 345, 6, 0, .6), (60, 20, 7, 1, 1.1), (640, 18, 5, 2, .3), (1120, 18, 8, 3, 1.7),
               (790, 566, 5, 0, 2.4), (460, 522, 4, 3, 1.3), (1040, 462, 4, 2, .9),
               (1060, 250, 9, 1, .5), (1110, 300, 5, 2, 1.8), (1000, 330, 6, 0, 2.8), (262, 352, 5, 3, 1.4)],
        label="Hello World, I'm Tanmay — GenAI & NLP engineer, founder of NAXATRA AI, CS at VIT Bhopal")


def footer():
    return melting_terminal(
        window="tanmay — zsh — lets-connect", prompt="~ $ ./say-hello --to you",
        line1="Have an idea?", line2="Let's connect.",
        pieces=[[("tanmaykala171206@gmail.com", {"fill": INK, "w": 500})], [("in/tanmay-kala", {})],
                [("@Tanmayai23", {})]],
        status="Inbox open", flip=True,
        drips=[(170, 34, 52, 11), (410, 44, 90, 14), (470, 26, 38, 10), (760, 40, 72, 13), (985, 46, 96, 15)],
        stars=[(90, 500, 10, 1, .3), (300, 470, 7, 3, 1.1), (610, 505, 13, 0, 1.9), (880, 470, 8, 2, .6),
               (1110, 520, 11, 1, 2.3), (22, 280, 9, 0, 1.5), (1180, 120, 10, 3, .2), (540, 560, 6, 2, 2.6),
               (1180, 360, 6, 1, 1.0), (80, 18, 7, 2, .8), (560, 18, 5, 0, 1.6), (1100, 18, 8, 1, 2.0),
               (230, 566, 5, 3, 2.9), (1050, 455, 4, 0, .5), (700, 456, 4, 1, 1.3),
               (1060, 250, 9, 2, .9), (1110, 305, 5, 0, 2.2), (995, 335, 6, 3, .4), (262, 352, 5, 1, 1.7)],
        label="Have an idea? Let's connect — tanmaykala171206@gmail.com · LinkedIn in/tanmay-kala · X @Tanmayai23")


# ================================================================== CONNECT DOCK
def gmail_icon(x, y, s):
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
    return (f'<g fill="none" stroke="{c}" stroke-width="2.2"><circle cx="{cx}" cy="{cy}" r="{r-1}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r*.42:.1f}" ry="{r-1}"/><path d="M{x+1},{cy} H{x+s-1}"/></g>')


DOCK = {
    "linkedin": ("LinkedIn", "in/tanmay-kala", lambda: icon("linkedin", 52, 40, 40, "#0A66C2"), 0),
    "x": ("X", "@Tanmayai23", lambda: icon("x", 54, 42, 36, INK), 1),
    "email": ("Gmail", "say hello", lambda: gmail_icon(50, 38, 44), 2),
    "portfolio": ("Portfolio", "tanmaykala.dev", lambda: globe_icon(52, 40, 40, BLUE), 3),
    "github": ("GitHub", "@tanmayai23", lambda: icon("github", 52, 40, 40, INK), 0),
}


def dock_tile(kind):
    """macOS-dock style app tile: icon on a white squircle, name below, a sparkle on the corner."""
    W, H = 144, 176
    label, sub, ic, ci = DOCK[kind]
    body = f"""
<rect x="24" y="12" width="96" height="96" rx="26" fill="{WHITE}" stroke="{HAIR}" stroke-width="1.5"/>
<rect x="24" y="12" width="96" height="96" rx="26" fill="url(#sheen)"/>
{ic()}
{T(72, 140, label, 17, 600, INK, anchor="middle", ls=-.3)}
{T(72, 162, sub, 15, 400, MUTED, "serif", "middle")}
{sparkles([(116, 16, 9, ci, ci * .5), (20, 100, 4, ci + 1, 1.2 + ci * .3)])}"""
    defs = (f'<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{SURFACE}"/></linearGradient>')
    return svg(W, H, body, f"{label} — {sub}", defs=defs)


# ================================================================== SECTION TITLES
def section(no, title, note):
    W, H = 1200, 112
    c = int(no) - 1
    tw_ = width(title, 44, 600, ls=-1.6)
    body = f"""
<g class="up">
  {sparkle(30, 58, 20, GOOGLE[c % 4], 0, "spin")}
  {T(62, 74, title, 44, 600, INK, ls=-1.6)}
  {T(76 + tw_, 74, note, 27, 400, MUTED, "serif")}
  {T(1184, 70, f"{no} / 05", 13, 500, MUTED, "mono", "end", 1)}
  <line x1="16" y1="102" x2="1184" y2="102" stroke="{HAIR}" stroke-width="1.5"/>
  <line x1="16" y1="102" x2="96" y2="102" stroke="{GOOGLE[c % 4]}" stroke-width="3" stroke-linecap="round"/>
</g>
{sparkles([(1084, 40, 7, c + 1, .4), (1050, 70, 4, c + 2, 1.3), (1112, 82, 5, c + 3, 2.0), (960 - c * 40, 36, 4, c, .9)])}"""
    return svg(W, H, body, f"{no} — {title}, {note}")


# ================================================================== ABOUT
def about():
    W, H = 1200, 430
    now = [("Building", "AI products, LLM workflows and voice interfaces", 0),
           ("Exploring", "RAG, evaluation, fine-tuning and production NLP", 1),
           ("Leading", "NAXATRA AI — useful AI infrastructure for Bharat", 2),
           ("Open to", "AI/ML & GenAI internships, ambitious collaborators", 3)]
    rows = "".join(
        f'<g class="up"{dl(.35 + i*.12)}>{sparkle(680, 118 + i*66, 10, GOOGLE[c], i*.6, "twinkle")}'
        + T(700, 124 + i*66, k, 18, 600, INK, ls=-.2)
        + T(700, 149 + i*66, v, 16, 400, MUTED) + "</g>"
        for i, (k, v, c) in enumerate(now))
    body = f"""
<rect x="16" y="10" width="1168" height="410" rx="32" fill="{SURFACE}"/>
<g class="up"{dl(.05)}>
  {T(88, 86, "ABOUT", 12.5, 500, MUTED, "mono", ls=3)}
  {T(85, 160, "I build AI that", 54, 600, INK, ls=-2.4)}
  {T(85, 222, [("leaves the ", {}), ("demo stage.", {"fam": "serif", "fill": BLUE, "size": 62})], 54, 600, INK, ls=-2.4)}
</g>
<g class="up"{dl(.2)}>
  {T(88, 276, "Turning models, data and APIs into tools people actually", 18, 400, INK2)}
  {T(88, 302, "use — shipped, measured, and improved after the first deploy.", 18, 400, INK2)}
  {T(88, 362, "“Ideas are cheap. Useful systems are the work.”", 24, 400, MUTED, "serif")}
</g>
<line x1="640" y1="70" x2="640" y2="360" stroke="{HAIR}" stroke-width="1.5"/>
{T(676, 86, "RIGHT NOW", 12.5, 500, MUTED, "mono", ls=3, cls="up", extra=dl(.3))}
{rows}
{sparkles([(1140, 52, 11, 2, .5), (1110, 80, 5, 0, 1.4), (600, 380, 8, 0, 1.5), (560, 64, 5, 1, 2.2), (1150, 390, 6, 3, .8), (420, 120, 4, 3, 1.9)])}"""
    return svg(W, H, body, "About: I build AI that leaves the demo stage. Building AI products, exploring RAG and evaluation, leading NAXATRA AI, open to AI/ML internships.")


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
    parts = []
    n = 0
    for r, (cat, items) in enumerate(STACK):
        y = top + r * row_h
        if r:
            parts.append(f'<line x1="80" y1="{y-4}" x2="1120" y2="{y-4}" stroke="{HAIR}"/>')
        parts.append(f'<g class="up"{dl(r*.1)}>{sparkle(86, y + 55, 10, GOOGLE[r], r * .5)}'
                     + T(106, y + 61, cat, 18, 600, INK, ls=-.2) + "</g>")
        for i, (slug, name, col) in enumerate(items):
            x = 290 + i * 122
            parts.append(
                f'<g class="up"{dl(.15 + n*.04)}>'
                f'<rect x="{x}" y="{y+14}" width="68" height="68" rx="19" fill="{WHITE}" stroke="{HAIR}"/>'
                f'{icon(slug, x+19, y+33, 30, col)}'
                + T(x + 34, y + 106, name, 13.5, 500, INK2, anchor="middle") + "</g>")
            n += 1
    # a constellation in the empty half of the Languages row
    parts.append(sparkles([(860, 70, 16, 0, 0), (930, 110, 9, 1, .7), (1000, 62, 12, 2, 1.4), (1070, 104, 7, 3, 2.1),
                           (900, 50, 4, 2, 1.1), (1040, 40, 5, 0, .3), (1110, 70, 4, 1, 1.8)]))
    parts.append(T(1112, 140, "and always learning", 19, 400, MUTED, "serif", "end"))
    y = top + row_h * len(STACK) + 16
    parts.append(f'<line x1="80" y1="{y-4}" x2="1120" y2="{y-4}" stroke="{HAIR}"/>')
    parts.append(f'<g class="up"{dl(.6)}>{sparkle(86, y + 39, 10, INK, .2)}' + T(106, y + 45, "Focus areas", 18, 600, INK, ls=-.2) + "</g>")
    x, yy = 290, y + 22
    for i, cap in enumerate(CAPS):
        w = width(cap, 14.5, 500) + 34
        if x + w > 1130:
            x, yy = 290, yy + 48
        p, w = pill(x, yy, cap, INK2, WHITE, size=14.5, pad=17, h=38, w=500, stroke=HAIR)
        parts.append(f'<g class="up"{dl(.7 + i*.05)}>{p}</g>')
        x += w + 10
    H = yy + 38 + 44
    parts.insert(0, f'<rect x="16" y="10" width="1168" height="{H-20}" rx="32" fill="{SURFACE}"/>')
    parts.append(sparkles([(1150, H - 50, 8, 3, 1.0), (50, H - 40, 5, 0, 2.2)]))
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
        return lines + dots + sparkles([(cx + 120, cy - 70, 9, 2, .4), (cx - 130, cy + 20, 6, 0, 1.6)])
    if kind == "wave":
        return "".join(f'<rect x="{cx-70+i*14}" y="{cy - h/2}" width="7" height="{h}" rx="3.5" fill="{GOOGLE[i % 4]}" class="breathe"{dl(i*.15)}/>'
                       for i, h in enumerate([16, 34, 58, 82, 48, 96, 64, 36, 70, 30, 18]))
    if kind == "agent":
        nodes = [(0, 0, INK), (-62, -42, BLUE), (62, -42, RED), (-62, 42, YELLOW), (62, 42, GREEN)]
        ls = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+x}" y2="{cy+y}" stroke="{HAIR}" stroke-width="3"/>' for x, y, _ in nodes[1:])
        ns = "".join(f'<circle cx="{cx+x}" cy="{cy+y}" r="{20 if not i else 13}" fill="{c}" class="{"" if not i else "twinkle"}"{dl(i*.4)}/>'
                     for i, (x, y, c) in enumerate(nodes))
        return ls + ns + T(cx, cy + 5, "AI", 13, 600, WHITE, "mono", "middle")
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
         sub="voice-first desktop assistant",
         desc=["Gemini conversation, face recognition,", "hotword detection and automation."],
         metric="<500 ms hotword", tech="Python · Gemini · OpenCV · SQLite"),
    dict(slug="marketbuddy", tag="AGENTIC AI", tagc=RED, title="Market Buddy", viz="agent",
         sub="autonomous voice agent · CALL-E",
         desc=["Hackathon voice agent built for", "dependable conversational workflows."],
         metric="421 passing tests", tech="Agents · TypeScript · Testing"),
    dict(slug="trafficsign", tag="COMPUTER VISION", tagc="#B07D00", title="TrafficSignNet", viz="grid",
         sub="a 43-class CNN, from scratch",
         desc=["Traffic-sign recognition in PyTorch,", "CPU-only and CLI-driven."],
         metric="96.82% accuracy", tech="Python · PyTorch · CNN"),
    dict(slug="travel", tag="NLP · GEO · LIVE", tagc=GREEN, title="Hey, where next?", viz="route",
         sub="an AI travel assist",
         desc=["Surfaces interesting places along", "your journey, wherever you are."],
         metric="POIs within 10 km", tech="Python · Gemini API · Geolocation"),
]


MORE = [("whisper", "Whisper Transcribe", "live demo", 0), ("vibehub", "VibeHub", "live demo", 1),
        ("repos", "All repositories", "every project, open source", 3)]


def link_card(title, sub, c):
    """Compact link chip for smaller projects — sits under the project grid."""
    W, H = 384, 96
    body = f"""
<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="26" fill="{SURFACE}"/>
<circle cx="50" cy="{H/2}" r="22" fill="{WHITE}" stroke="{HAIR}"/>
{sparkle(50, H/2, 11, GOOGLE[c], c * .6, "spin")}
{T(88, 45, title, 19, 600, INK, ls=-.4)}
{T(88, 69, sub, 17, 400, MUTED, "serif")}
{arrow(W - 44, H / 2, 17)}
{sparkles([(W - 82, 22, 4, c + 1, 1.2 + c * .4)])}"""
    return svg(W, H, body, f"{title} — {sub}")


def project_flagship(p):
    W, H = 1200, 360
    mets = "".join(
        f'<g class="up"{dl(.45 + i*.1)}>' + T(88 + i*196, 292, v, 40, 600, INK, ls=-1.6)
        + T(90 + i*196, 318, l, 14.5, 400, MUTED) + "</g>"
        for i, (v, l) in enumerate(p["metrics"]))
    tag, _ = pill(88, 52, p["tag"], p["tagc"], WHITE, size=11.5, pad=14, h=28, fam="mono", w=600, ls=1.2, stroke=HAIR)
    body = f"""
<rect x="16" y="10" width="1168" height="340" rx="32" fill="{SURFACE}"/>
<g class="up">{tag}</g>
<g class="up"{dl(.1)}>{T(84, 136, p['title'], 66, 700, INK, ls=-3)}
{T(88, 174, p['sub'], 28, 400, MUTED, "serif")}</g>
<g class="up"{dl(.25)}>{"".join(T(88, 212 + i*25, t, 17, 400, INK2) for i, t in enumerate(p['desc']))}</g>
{mets}
<rect x="730" y="40" width="414" height="280" rx="26" fill="{WHITE}" stroke="{HAIR}"/>
<g>{viz(p['viz'], 937, 170)}</g>
{T(756, 300, p['tech'], 12, 400, MUTED, "mono")}
{T(1120, 300, "Open live ↗", 13.5, 600, BLUE, anchor="end")}
{sparkles([(690, 40, 9, 2, .6), (700, 330, 5, 0, 1.6), (40, 330, 6, 3, 2.3)])}"""
    return svg(W, H, body, f"{p['title']} — {p['sub']}. " + ", ".join(f"{v} {l}" for v, l in p["metrics"]))


def project_card(p, k):
    W, H = 590, 350
    tag, _ = pill(36, 40, p["tag"], p["tagc"], WHITE, size=11, pad=12, h=26, fam="mono", w=600, ls=1.1, stroke=HAIR)
    met, _ = pill(36, 244, p["metric"], WHITE, INK, size=13.5, pad=15, h=32, w=600)
    body = f"""
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="30" fill="{SURFACE}"/>
<g class="up">{tag}</g>
<g class="up"{dl(.1)}>{T(34, 118, p['title'], 40, 700, INK, ls=-1.6)}
{T(36, 148, p['sub'], 21, 400, MUTED, "serif")}</g>
<g class="up"{dl(.2)}>{"".join(T(36, 188 + i*23, t, 15, 400, INK2) for i, t in enumerate(p['desc']))}</g>
<g class="up"{dl(.3)}>{met}</g>
{T(36, 308, p['tech'], 11.5, 400, MUTED, "mono")}
<g>{viz(p['viz'], 470, 120)}</g>
{arrow(W - 50, H - 50)}
{sparkles([(548, 230, 7, k, .4 + k * .3), (360, 44, 5, k + 1, 1.5), (510, 270, 4, k + 2, 2.2)])}"""
    return svg(W, H, body, f"{p['title']} — {p['sub']} · {p['metric']}")


# ================================================================== ACHIEVEMENT GALLERY
GALLERY = [
    dict(photo="google-ambassador.jpg", no="01", org="GOOGLE", c=0, title="Google Student",
         title2="Ambassador, 2026", lines=["Selected for the Gemini Student", "Ambassador Program. Earned the", "Explorer & Navigator badges."],
         chip="#TeamGemini", focus=.30),
    dict(photo="ieee-track-winner.jpg", no="02", org="IEEE", c=1, title="IEEE Track", title2="Winner",
         lines=["Took the track-winner trophy", "home, with a stack of IEEE", "certificates to go with it."],
         chip="Track Winner", focus=.28),
    dict(photo="hack-for-green-bharat.jpg", no="03", org="MICROSOFT · UNSTOP", c=3, title="Hack for", title2="Green Bharat",
         lines=["SwachhVan finished in the", "Top 25 of 400+ teams at", "Microsoft's sustainability hack."],
         chip="Top 25 / 400+", focus=.30),
    dict(photo="google-go-bananas.jpg", no="04", org="GOOGLE GEMINI", c=2, title="Go Bananas", title2="with Gemini",
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
    W, H = 590, 430
    px, py, pw, ph = 22, 22, 260, 386
    c = a["c"]
    b64 = photo_b64(a["photo"], pw * 2, ph * 2, a["focus"])
    chip, _ = pill(312, 338, a["chip"], WHITE, INK, size=13, pad=14, h=30, w=600)
    body = f"""
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="32" fill="{SURFACE}"/>
<g clip-path="url(#ph)">
  <image href="data:image/jpeg;base64,{b64}" x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice" class="zoom"/>
  <rect x="{px}" y="{py + ph - 96}" width="{pw}" height="96" fill="url(#shade)"/>
</g>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22" fill="none" stroke="#000" stroke-opacity=".06"/>
{T(px + 18, py + ph - 20, f"{a['no']} / 04", 12.5, 600, WHITE, "mono", ls=1)}
{sparkles([(px + pw - 22, py + 26, 12, WHITE, .2), (px + pw - 46, py + 50, 5, WHITE, 1.3)])}
<g class="up"{dl(.1)}>
  {sparkle(316, 64, 9, GOOGLE[c], 0)}
  {T(334, 69, a['org'], 11.5, 600, MUTED, "mono", ls=1.6)}
  {T(309, 126, a['title'], 34, 700, INK, ls=-1.4)}
  {T(310, 166, a['title2'], 38, 400, GOOGLE[c] if c != 2 else "#B07D00", "serif")}
</g>
<g class="up"{dl(.25)}>{"".join(T(312, 212 + i*25, t, 15.5, 400, INK2) for i, t in enumerate(a['lines']))}</g>
<g class="up"{dl(.4)}>{chip}</g>
{sparkles([(552, 52, 10, c, .3), (530, 396, 6, c + 1, 1.4), (566, 300, 4, c + 2, 2.1)])}"""
    defs = (f'<clipPath id="ph"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22"/></clipPath>'
            f'<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>')
    return svg(W, H, body, f"Achievement {a['no']}: {a['title']} {a['title2']} — {' '.join(a['lines'])}", defs=defs)


if __name__ == "__main__":
    print(f"Building {OUT}:")
    write("hero.svg", hero())
    for k in DOCK:
        write(f"dock-{k}.svg", dock_tile(k))
    write("about.svg", about())
    for no, title, note in [("01", "About", "the short version"), ("02", "Tech stack", "tools I ship with"),
                            ("03", "Projects", "selected work"), ("04", "Achievements", "moments worth framing"),
                            ("05", "Commit graph", "the daily practice")]:
        write(f"section-{no}.svg", section(no, title, note))
    write("stack.svg", stack())
    write(f"project-{PROJECTS[0]['slug']}.svg", project_flagship(PROJECTS[0]))
    for i, p in enumerate(PROJECTS[1:]):
        write(f"project-{p['slug']}.svg", project_card(p, i))
    for slug, title, sub, c in MORE:
        write(f"more-{slug}.svg", link_card(title, sub, c))
    for a in GALLERY:
        write(f"achievement-{a['no']}.svg", achievement(a))
    write("footer.svg", footer())
