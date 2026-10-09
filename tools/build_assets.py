"""Generates the "TanmayGPT" chat-style profile README assets.

Every asset is written twice (name-dark.svg / name-light.svg); the README picks
one with <picture> + prefers-color-scheme, which follows the viewer's GitHub theme.

Run:  python tools/build_assets.py
Edit CHAT_TOP / CHAT_END / PROJECTS below and re-run.
"""
import base64
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

DARK = dict(bg="#0D1117", card="#161B22", line="#30363D", text="#E6EDF3", soft="#C9D1D9",
            muted="#8B949E", teal="#2DD4BF", cyan="#38BDF8", violet="#A78BFA", amber="#FBBF24",
            pink="#F472B6", green="#3FB950", glow=".18", chip=".10",
            u1="#2DD4BF", u2="#38BDF8", utext="#04221F")
LIGHT = dict(bg="#FFFFFF", card="#F6F8FA", line="#D0D7DE", text="#1F2328", soft="#31373D",
             muted="#59636E", teal="#0F766E", cyan="#0369A1", violet="#6D28D9", amber="#B45309",
             pink="#BE185D", green="#1A7F37", glow=".09", chip=".07",
             u1="#0F766E", u2="#0369A1", utext="#FFFFFF")

SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', SFMono-Regular, Consolas, 'Courier New', monospace"

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .pop {{ animation: pop .45s cubic-bezier(.2,.8,.2,1.2) both; transform-box: fill-box; }}
  .popL {{ transform-origin: left bottom; }}
  .popR {{ transform-origin: right bottom; }}
  .typing {{ opacity: 0; animation: show .7s linear both; animation-fill-mode: none; }}
  .dot {{ animation: bounce 1s ease-in-out infinite; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .ping {{ animation: ping 2s cubic-bezier(0,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes pop {{ from {{ opacity: 0; transform: translateY(12px) scale(.94); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes show {{ 0%,100% {{ opacity: 1; }} }}
  @keyframes bounce {{ 0%,60%,100% {{ transform: translateY(0); opacity: .45; }} 30% {{ transform: translateY(-5px); opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes ping {{ 0% {{ opacity: .8; transform: scale(1); }} 80%,100% {{ opacity: 0; transform: scale(2.6); }} }}
  @media (prefers-reduced-motion: reduce) {{ .pop, .dot, .blink, .ping {{ animation: none !important; }} }}
"""

PHOTO = base64.b64encode((ROOT / "avatar.jpg").read_bytes()).decode()
W, PAD, FS, LH = 1000, 36, 19, 30   # canvas width, side padding, message font size, line height


def e(s):
    return escape(str(s), quote=True)


def dl(s):
    return f' style="animation-delay:{s:.2f}s"'


def sans_w(text, size):
    return len(text) * size * 0.53


def mono_w(text, size):
    return len(text) * size * 0.6


def bubble(x, y, w, h, r=20, tl=None, br=None, **attrs):
    """Rounded rect path with optional tighter top-left / bottom-right corner (chat tail)."""
    tl = r if tl is None else tl
    br = r if br is None else br
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return (f'<path d="M{x+tl},{y} H{x+w-r} Q{x+w},{y} {x+w},{y+r} V{y+h-br} Q{x+w},{y+h} {x+w-br},{y+h} '
            f'H{x+r} Q{x},{y+h} {x},{y+h-r} V{y+tl} Q{x},{y} {x+tl},{y} Z" {a}/>')


def avatar_defs():
    return (f'<clipPath id="avc"><circle cx="20" cy="20" r="20"/></clipPath>'
            f'<symbol id="av" viewBox="0 0 40 40" overflow="visible"><image width="40" height="40" '
            f'href="data:image/jpeg;base64,{PHOTO}" clip-path="url(#avc)"/></symbol>')


def photo(x, y, size):
    return f'<use href="#av" x="{x}" y="{y}" width="{size}" height="{size}"/>'


# ----------------------------------------------------------------- content
CHAT_TOP = [
    ("user", "Who is Tanmay?"),
    ("ai", "text", [
        [("Tanmay Kala", "text", True), (" — Generative AI & NLP engineer", "soft", False)],
        [("and founder of ", "soft", False), ("Naxatra AI", "teal", True), (".", "soft", False)],
        [("B.Tech CSE (AI & ML) @ VIT Bhopal, class of '28.", "soft", False)],
        [("He doesn't stop at demos. He ships AI products.", "text", True)],
    ]),
    ("user", "Impressive. Any proof?"),
    ("ai", "stats", "Here are the receipts:", [
        ("5+", "AI products live", "teal"), ("Top 25", "of 400+ teams", "cyan"),
        ("96.82%", "CNN accuracy", "pink"), ("421", "tests passing", "amber"),
    ]),
    ("user", "What is he working on right now?"),
    ("ai", "text", [
        [("▸ ", "teal", True), ("Building Naxatra AI", "text", True), (" — AI for civic problems", "soft", False)],
        [("▸ ", "violet", True), ("Voice agents", "text", True), (" with LangGraph + CALL-E", "soft", False)],
        [("▸ ", "amber", True), ("Freshly certified:", "text", True), (" OCI Generative AI Pro", "soft", False)],
    ]),
    ("user", "Show me his best work."),
    ("ai", "text", [[("Tap any card below ", "soft", False), ("↓", "teal", True)]]),
]

CHAT_END = [
    ("user", "Okay, I'm convinced. How do we hire him?"),
    ("ai", "text", [
        [("He's ", "soft", False), ("open to AI/ML & GenAI internships", "green", True), (".", "soft", False)],
        [("LinkedIn, email and portfolio are right below. Say hi!", "soft", False)],
    ]),
]


# ------------------------------------------------------------------ chat
def chat(T, msgs, header, composer, start=.3):
    items, defs_extra = [], []
    y = (72 + 30) if header else 30
    t = start
    clip_n = 0
    TYPE, LINE_T = .75, .42

    for m in msgs:
        if m[0] == "user":
            text = m[1]
            w = sans_w(text, FS) + 44
            h = 50
            x = W - PAD - w
            items.append(f'<g class="pop popR"{dl(t)}>'
                         + bubble(x, y, w, h, br=6, fill="url(#ub)")
                         + f'<text x="{x+22}" y="{y+32}" class="sans" font-size="{FS}" font-weight="600" fill="{T["utext"]}">{e(text)}</text></g>')
            y += h + 18
            t += .55
            continue

        bx = PAD + 54
        # typing indicator, then avatar stays
        items.append(f'<g class="pop popL"{dl(t)}>{photo(PAD, y + 2, 40)}</g>')
        items.append(f'<g class="typing" style="animation-delay:{t:.2f}s;animation-duration:{TYPE}s">'
                     + bubble(bx, y, 76, 46, tl=6, fill=T["card"], stroke=T["line"])
                     + "".join(f'<circle cx="{bx+22+i*16}" cy="{y+23}" r="4.5" fill="{T["muted"]}" class="dot" style="animation-delay:{i*.15:.2f}s"/>' for i in range(3))
                     + '</g>')
        t += TYPE

        if m[1] == "text":
            lines = m[2]
            lw = max(sum(sans_w(s, FS) for s, _, _ in ln) for ln in lines)
            w, h = lw + 48, len(lines) * LH + 26
            body = [bubble(bx, y, w, h, tl=6, fill=T["card"], stroke=T["line"])]
            for i, ln in enumerate(lines):
                clip_n += 1
                ly = y + 13 + (i + 1) * LH - 8
                full = sum(sans_w(s, FS) for s, _, _ in ln) + 30
                defs_extra.append(f'<clipPath id="tw{clip_n}"><rect x="{bx+16}" y="{ly-FS-2}" width="0" height="{FS+10}">'
                                  f'<animate attributeName="width" from="0" to="{full:.0f}" begin="{t + i*LINE_T:.2f}s" '
                                  f'dur="{LINE_T:.2f}s" fill="freeze"/></rect></clipPath>')
                spans = "".join(f'<tspan fill="{T[c]}"{" font-weight=\"700\"" if b else ""}>{e(s)}</tspan>' for s, c, b in ln)
                body.append(f'<text x="{bx+24}" y="{ly}" class="sans" font-size="{FS}" xml:space="preserve" clip-path="url(#tw{clip_n})">{spans}</text>')
            items.append(f'<g class="pop popL"{dl(t)}>{"".join(body)}</g>')
            t += len(lines) * LINE_T
        else:  # stats
            intro, stats = m[2], m[3]
            tw, gap = 172, 12
            w = 24 * 2 + len(stats) * tw + (len(stats) - 1) * gap
            h = 64 + 104
            body = [bubble(bx, y, w, h, tl=6, fill=T["card"], stroke=T["line"]),
                    f'<text x="{bx+24}" y="{y+40}" class="sans" font-size="{FS}" fill="{T["soft"]}">{e(intro)}</text>']
            items.append(f'<g class="pop popL"{dl(t)}>{"".join(body)}</g>')
            for i, (val, lab, c) in enumerate(stats):
                tx = bx + 24 + i * (tw + gap)
                items.append(f'<g class="pop popL"{dl(t + .25 + i*.18)}>'
                             f'<rect x="{tx}" y="{y+60}" width="{tw}" height="88" rx="14" fill="{T[c]}" fill-opacity="{T["chip"]}" stroke="{T[c]}" stroke-opacity=".35"/>'
                             f'<text x="{tx+16}" y="{y+100}" class="sans" font-size="30" font-weight="800" letter-spacing="-1" fill="{T[c]}">{e(val)}</text>'
                             f'<text x="{tx+16}" y="{y+128}" class="sans" font-size="14.5" fill="{T["soft"]}">{e(lab)}</text></g>')
            t += .25 + len(stats) * .18
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
                f'<text x="{PAD+56}" y="55" class="sans" font-size="13.5" fill="{T["muted"]}"><tspan fill="{T["green"]}">● online</tspan>  ·  trained on 2 years of shipping AI</text>'
                f'<rect x="{W-PAD-206}" y="22" width="206" height="28" rx="14" fill="{T["teal"]}" fill-opacity="{T["chip"]}" stroke="{T["teal"]}" stroke-opacity=".35"/>'
                f'<text x="{W-PAD-103}" y="41" text-anchor="middle" class="mono" font-size="12.5" fill="{T["teal"]}">model: tanmay-kala-v2</text>')
    defs = f"""
  {avatar_defs()}
  <clipPath id="win"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="ub" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T['u1']}"/><stop offset="1" stop-color="{T['u2']}"/></linearGradient>
  <radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{T['teal']}" stop-opacity="{T['glow']}"/><stop offset=".6" stop-color="{T['teal']}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{T['muted']}" fill-opacity=".16"/></pattern>
  {''.join(defs_extra)}
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
            f'<defs>{defs}</defs>{body}</svg>\n')


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
    for mode, T in (("dark", DARK), ("light", LIGHT)):
        for name, content in [(f"chat-{mode}.svg", chat(T, CHAT_TOP, header=True, composer=False)),
                              (f"chat-end-{mode}.svg", chat(T, CHAT_END, header=False, composer=True))]:
            (OUT / name).write_text(content, encoding="utf-8")
            print(f"  assets/{name}")
        for i, p in enumerate(PROJECTS):
            (OUT / f"card-{p['slug']}-{mode}.svg").write_text(card(T, i, p), encoding="utf-8")
            print(f"  assets/card-{p['slug']}-{mode}.svg")
