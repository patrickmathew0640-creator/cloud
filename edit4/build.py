"""Generate index.html (HyperFrames composition) and sfx_cues.json for the Power BI MCP ad.

The talking-head track is assets/cut_*.mp4: the source with dead air removed
(src 2.40-11.80, 12.70-22.2667, 22.80-69.1667 -> output 0-65.333). Times below are OUTPUT seconds unless
they go through out(), which maps a source-timeline time (from the transcript) to the output timeline.

    python3 build.py        # 1080p proxy footage (fast preview / snapshots)
    python3 build.py 4k     # 4K footage for the final 2160x3840 render
"""
import json
import re
import sys

SPK_END = 65.333
DURATION = 69.5
PH = 900          # top panel height in split mode
SPLIT_Y = -540    # footage offset inside the bottom panel (keeps her face centred)
VIDEO = "assets/cut_4k.mp4" if len(sys.argv) > 1 and sys.argv[1] == "4k" else "assets/cut_1080.mp4"


def out(src):
    off = 2.40 if src < 11.80 else 3.30 if src < 22.2667 else 3.8333
    return round(src - off, 3)


# English captions for the Tamil voice-over (source times). *word* = highlight.
CAPTIONS = [
    (4.62, 6.10, "And I think *you’ll love it too*"),
    (6.16, 7.60, "But *who* builds"),
    (7.60, 9.24, "a dashboard *like this*?"),
    (9.28, 10.30, "A *Power BI developer*?"),
    (10.30, 11.78, "A *data analyst*?"),
    (12.76, 14.12, "*Whoever* it is…"),
    (14.16, 15.45, "just give *Claude AI*"),
    (15.45, 17.40, "access to *your data*"),
    (17.40, 18.94, "and say: “In *10–15 minutes*,"),
    (18.94, 20.70, "I want *this dashboard*”"),
    (20.70, 22.20, "and it *delivers!*"),
    (22.85, 24.40, "A *professional* Power BI dashboard"),
    (24.40, 25.86, "*requirements*, *data prep*,"),
    (25.86, 27.55, "*modeling*, *DAX*, *visuals*,"),
    (27.55, 29.20, "*testing*… so many *stages*"),
    (29.26, 31.70, "So a *proper* dashboard"),
    (31.70, 33.60, "takes *hours… even days*"),
    (33.66, 35.60, "*But* we took the same workflow"),
    (35.60, 37.90, "*Claude AI + Power BI MCP*"),
    (37.90, 39.70, "and *automated* it"),
    (39.78, 41.70, "Gave only the *access it needs*"),
    (41.70, 43.70, "told it *which dashboard* we want"),
    (43.82, 45.20, "and within *10–15 minutes*"),
    (45.20, 46.80, "the dashboard was *ready!*"),
    (46.84, 48.70, "*This* is the power of"),
    (48.70, 50.15, "*AI + MCP* Power BI *automation*"),
    (50.20, 52.00, "From *installation*"),
    (52.00, 53.50, "to *dashboard creation*"),
    (53.50, 54.62, "*A–Z complete PDF guide*"),
    (54.66, 56.70, "+ *MCP integration toolkit*"),
    (56.70, 58.95, "+ *step-by-step video* lessons"),
    (59.32, 60.75, "The *complete package*"),
    (60.75, 62.80, "for just *₹299*"),
    (62.86, 64.00, "Want this"),
    (64.00, 66.30, "*AI + Power BI MCP* workflow?"),
    (66.30, 67.85, "*Comment “LINK”*"),
    (67.85, 69.10, "and we’ll *share it!*"),
]

# Speaker layout: (start, mode). "full" = full frame, "split" = graphics panel on top, speaker below.
MODES = [(0.0, "full"), (18.97, "split"), (25.43, "full"), (29.83, "split"), (39.99, "full"),
         (46.37, "split"), (55.47, "full"), (59.03, "split")]

# Zoom moves on the speaker: (start, end, from, to, transform-origin)
ZOOMS = [
    (0.00, 2.25, 1.000, 1.040, "56% 46%"),   # push in on the tablet during the hook
    (2.25, 6.00, 1.024, 1.040, "30% 25%"),
    (6.00, 9.40, 1.040, 1.056, "28% 22%"),   # punch-in on "But who builds…"
    (9.40, 11.40, 1.048, 1.020, "42% 27%"),
    (11.40, 17.75, 1.000, 1.000, "42% 27%"),
    (17.75, 18.97, 1.056, 1.080, "42% 27%"),  # "and it delivers!"
    (18.97, 25.43, 1.000, 1.020, "50% 52%"),
    (25.43, 27.91, 1.000, 1.032, "50% 50%"),
    (27.91, 28.75, 1.056, 1.064, "50% 50%"),  # "HOURS"
    (28.75, 29.83, 1.096, 1.112, "50% 50%"),  # "DAYS"
    (29.83, 35.95, 1.000, 1.020, "50% 52%"),
    (35.95, 39.99, 1.024, 1.000, "50% 52%"),
    (39.99, 43.01, 1.032, 1.032, "50% 50%"),
    (43.01, 45.41, 1.032, 1.052, "50% 50%"),
    (45.41, 46.37, 1.088, 1.096, "50% 50%"),  # "automation"
    (46.37, 55.47, 1.000, 1.020, "50% 52%"),
    (55.47, 56.99, 1.016, 1.036, "50% 50%"),
    (56.99, 59.03, 1.080, 1.064, "50% 50%"),  # "₹299"
    (59.03, 65.33, 1.000, 1.024, "50% 52%"),
]

SFX = [
    # hook
    ("impact", 0.02, 0.45), ("whoosh", 0.00, 0.30), ("pop", 0.42, 0.26), ("boom", 0.80, 0.45), ("pop", 1.22, 0.24),
    ("whoosh_soft", 2.18, 0.22),
    # roles
    ("pop", out(9.28) - 0.05, 0.26), ("pop", out(10.30) - 0.05, 0.26), ("whoosh", 9.22, 0.40), ("click", 9.50, 0.45), ("click", 9.62, 0.45),
    # chat b-roll
    ("whoosh", 11.30, 0.35), ("blip", 12.25, 0.30), ("typing", 13.55, 0.32), ("blip", 15.55, 0.32),
    ("click", 15.85, 0.45), ("click", 16.15, 0.45), ("click", 16.45, 0.45), ("click", 16.75, 0.45),
    ("ding", 17.00, 0.22), ("pop", 17.05, 0.24), ("whoosh", 17.62, 0.35), ("pop", 17.95, 0.28),
    # stages panel
    ("whoosh", 18.86, 0.38),
    *[("pop", t, 0.22) for t in (out(24.46), out(25.18), out(25.88), out(26.70), out(27.12), out(27.58))],
    ("whoosh_soft", 25.32, 0.25),
    # hours -> days
    ("impact", out(31.74), 0.30), ("impact", out(32.58), 0.42),
    # BUT drop
    ("impact", 29.83, 0.60), ("boom", 29.83, 0.55), ("whoosh", 29.70, 0.35),
    ("pop", out(35.66), 0.24), ("pop", out(36.58), 0.24), ("blip", out(37.22), 0.28), ("ding", out(38.84), 0.24),
    # access + prompt
    ("whoosh_soft", 35.88, 0.25), ("click", 36.55, 0.45), ("click", 36.85, 0.45), ("click", 37.15, 0.45),
    ("typing", 37.85, 0.30), ("blip", 39.45, 0.30),
    # montage
    ("whoosh", 39.88, 0.45), *[("snap", round(40.15 + i * 0.27, 2), 0.35) for i in range(7)],
    ("impact", out(45.92), 0.45), ("ding", out(45.92) + 0.05, 0.25), ("whoosh", 42.92, 0.35),
    # AI + MCP
    ("pop", out(47.66), 0.26), ("pop", out(48.18), 0.26), ("impact", out(49.24), 0.35),
    # package
    ("whoosh", 46.28, 0.38), ("pop", 46.60, 0.22),
    ("pop", 49.55, 0.26), ("pop", out(55.20) - 0.1, 0.26), ("pop", out(57.06) - 0.1, 0.26),
    *[("click", round(54.15 + i * 0.2, 2), 0.4) for i in range(4)],
    # price
    ("whoosh_soft", 55.40, 0.25), ("pop", out(59.48), 0.24), ("kaching", out(60.82) - 0.05, 0.55), ("impact", out(60.82), 0.40),
    ("pop", out(60.82) + 0.6, 0.22),
    # CTA
    ("whoosh", 58.95, 0.38), ("pop", 59.30, 0.22),
    *[("click", round(out(66.36) - 0.05 + i * 0.13, 2), 0.5) for i in range(4)],
    ("blip", out(67.28), 0.32), ("pop", out(67.28) + 0.25, 0.26), ("pop", out(67.92), 0.24),
    # end card
    ("swell", 64.15, 0.50), ("impact", 65.33, 0.55), ("boom", 65.33, 0.40),
    ("pop", 65.90, 0.24), ("pop", 66.25, 0.24), ("pop", 66.60, 0.24), ("ding", 67.05, 0.24), ("click", 67.75, 0.45),
]


def caption_html(i, text):
    words = []
    for tok in re.split(r"(\*[^*]+\*)", text):
        if not tok:
            continue
        hl = tok.startswith("*")
        for w in tok.strip("*").split():
            words.append(f'<span class="{"w hl" if hl else "w"}">{w}</span>')
    return f'<div id="cap{i}" class="cap"><div class="capbox">{" ".join(words)}</div></div>'


CHECK = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="#2dd4bf"/><path d="M19 33l9 9 18-19" stroke="#06221f" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="#ff4d5e"/><path d="M22 22l20 20M42 22l-20 20" stroke="#fff" stroke-width="7" stroke-linecap="round"/></svg>'
ARROW = '<svg viewBox="0 0 48 48"><path d="M8 24h30M26 12l12 12-12 12" stroke="currentColor" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BARS = '<svg viewBox="0 0 64 64"><rect x="8" y="34" width="12" height="22" rx="3" fill="#f2c811"/><rect x="26" y="20" width="12" height="36" rx="3" fill="#f2c811" opacity=".85"/><rect x="44" y="8" width="12" height="48" rx="3" fill="#f2c811" opacity=".7"/></svg>'
SPARK = '<svg viewBox="0 0 64 64"><g stroke="#e07a52" stroke-width="7" stroke-linecap="round">' + "".join(
    f'<path d="M32 32L{32 + 26 * c:.1f} {32 + 26 * s:.1f}"/>' for c, s in
    ((1, 0), (.7071, .7071), (0, 1), (-.7071, .7071), (-1, 0), (-.7071, -.7071), (0, -1), (.7071, -.7071))) + '</g></svg>'
PLUG = '<svg viewBox="0 0 64 64"><path d="M24 6v14M40 6v14" stroke="#0a0a0b" stroke-width="6" stroke-linecap="round"/><path d="M16 20h32v10a16 16 0 0 1-32 0z" fill="#0a0a0b"/><path d="M32 46v12" stroke="#0a0a0b" stroke-width="6" stroke-linecap="round"/></svg>'
CLOCK = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#1b1b1f" stroke="#ff4d5e" stroke-width="7"/><path id="hand1" d="M50 50V20" stroke="#fff" stroke-width="6" stroke-linecap="round"/><path id="hand2" d="M50 50h20" stroke="#ff4d5e" stroke-width="6" stroke-linecap="round"/><circle cx="50" cy="50" r="5" fill="#fff"/></svg>'
PERSON = '<svg viewBox="0 0 64 64"><circle cx="32" cy="22" r="12" fill="#c8ccd4"/><path d="M10 58c2-14 11-20 22-20s20 6 22 20z" fill="#c8ccd4"/></svg>'
STAGE_ICONS = [
    '<svg viewBox="0 0 64 64"><rect x="14" y="8" width="36" height="48" rx="5" fill="none" stroke="#fff" stroke-width="5"/><path d="M22 24h20M22 34h20M22 44h12" stroke="#fff" stroke-width="5" stroke-linecap="round"/></svg>',
    '<svg viewBox="0 0 64 64"><ellipse cx="32" cy="14" rx="20" ry="7" fill="none" stroke="#fff" stroke-width="5"/><path d="M12 14v34c0 4 9 7 20 7s20-3 20-7V14M12 31c0 4 9 7 20 7s20-3 20-7" fill="none" stroke="#fff" stroke-width="5"/></svg>',
    '<svg viewBox="0 0 64 64"><g fill="none" stroke="#fff" stroke-width="5"><rect x="6" y="8" width="20" height="16" rx="3"/><rect x="38" y="8" width="20" height="16" rx="3"/><rect x="22" y="40" width="20" height="16" rx="3"/><path d="M16 24v8h32v-8M32 32v8"/></g></svg>',
    '<svg viewBox="0 0 64 64"><text x="32" y="44" text-anchor="middle" font-family="JBMono" font-weight="700" font-size="30" fill="#fff">fx</text></svg>',
    '<svg viewBox="0 0 64 64"><g fill="#fff"><rect x="8" y="34" width="10" height="22" rx="2"/><rect x="24" y="22" width="10" height="34" rx="2"/><rect x="40" y="12" width="10" height="44" rx="2"/></g></svg>',
    '<svg viewBox="0 0 64 64"><path d="M14 33l12 12 24-26" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
]
STAGES = ["Requirements", "Data prep", "Modeling", "DAX", "Visuals", "Testing"]
STAGE_T = [out(24.46), out(25.18), out(25.88), out(26.70), out(27.12), out(27.58)]
PKG_ICONS = [
    '<svg viewBox="0 0 64 64"><path d="M14 6h26l12 12v40H14z" fill="#ff4d5e"/><path d="M40 6v12h12" fill="#ffb3ba"/><text x="33" y="46" text-anchor="middle" font-family="Outfit" font-weight="900" font-size="15" fill="#fff">PDF</text></svg>',
    '<svg viewBox="0 0 64 64"><rect x="6" y="20" width="52" height="34" rx="6" fill="#2dd4bf"/><path d="M22 20v-6a4 4 0 0 1 4-4h12a4 4 0 0 1 4 4v6" fill="none" stroke="#2dd4bf" stroke-width="5"/><rect x="6" y="32" width="52" height="5" fill="#0f766e"/><rect x="27" y="29" width="10" height="11" rx="2" fill="#f2c811"/></svg>',
    '<svg viewBox="0 0 64 64"><rect x="4" y="12" width="56" height="40" rx="8" fill="#8fb4ff"/><path d="M27 23v18l15-9z" fill="#0a0a0b"/></svg>',
]
DASH = ["01-sales", "03-hr", "02-finance", "05-ecommerce", "04-marketing", "06-supply", "08-support", "10-projects"]


def build():
    caps = "\n        ".join(caption_html(i, c[2]) for i, c in enumerate(CAPTIONS))
    caps_js = [[f"#cap{i}", out(s), out(e)] for i, (s, e, _) in enumerate(CAPTIONS)]
    stages = "".join(
        f'<div class="stg" id="stg{i}"><div class="si">{STAGE_ICONS[i]}</div><div class="sn">{i + 1:02d}</div><div class="sl">{name}</div></div>'
        for i, name in enumerate(STAGES))
    montage = "".join(f'<img class="mimg" id="m{i}" src="assets/dash/{n}.jpg" alt="">' for i, n in enumerate(DASH))
    pk = [("A–Z Complete PDF Guide", "Installation to dashboard creation"),
          ("MCP Integration Toolkit", "Server + one-click Windows setup"),
          ("Step-by-step Video", "Follow along, screen by screen")]
    pkg = "".join(
        f'<div class="pkc" id="pk{i}"><div class="pki">{PKG_ICONS[i]}</div><div><div class="pkt">{t}</div><div class="pks">{s}</div></div><div class="pkk">{CHECK}</div></div>'
        for i, (t, s) in enumerate(pk))
    rep = {
        "{{CAPTIONS}}": caps, "{{STAGES}}": stages, "{{MONTAGE}}": montage, "{{PKG}}": pkg,
        "{{CHECK}}": CHECK, "{{CROSS}}": CROSS, "{{ARROW}}": ARROW, "{{BARS}}": BARS, "{{SPARK}}": SPARK, "{{PLUG}}": PLUG,
        "{{CLOCK}}": CLOCK, "{{PERSON}}": PERSON, "{{VIDEO}}": VIDEO,
        "{{CAPS_JS}}": json.dumps(caps_js), "{{MODES_JS}}": json.dumps(MODES), "{{ZOOMS_JS}}": json.dumps(ZOOMS),
        "{{STAGE_T}}": json.dumps(STAGE_T), "{{DURATION}}": str(DURATION), "{{SPK_END}}": str(SPK_END),
        "{{PH}}": str(PH), "{{SPLIT_Y}}": str(SPLIT_Y), "{{NDASH}}": str(len(DASH)),
        "{{T}}": json.dumps({k: out(v) for k, v in {
            "roleA": 9.28, "roleB": 10.30, "hours": 31.74, "days": 32.58, "claude": 35.66, "pbi": 36.58, "mcp": 37.22,
            "automate": 38.84, "access": 40.36, "which": 41.74, "ready": 45.92, "ai": 47.66, "plusmcp": 48.18,
            "automation": 49.24, "pdf": 53.56, "toolkit": 55.20, "video": 57.06, "package": 59.48, "price": 60.82,
            "want": 62.86, "link": 66.36, "comment": 67.28, "share": 67.92}.items()}),
    }
    html = TEMPLATE
    for k, v in rep.items():
        html = html.replace(k, v)
    assert "{{" not in html, re.findall(r"\{\{\w+\}\}", html)
    open("index.html", "w").write(html)
    json.dump(sorted(([n, round(t, 3), v] for n, t, v in SFX), key=lambda c: c[1]), open("sfx_cues.json", "w"), indent=1)


TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Outfit"; font-weight: 500; src: url("assets/fonts/outfit-500.woff2") format("woff2"); }
      @font-face { font-family: "Outfit"; font-weight: 600; src: url("assets/fonts/outfit-600.woff2") format("woff2"); }
      @font-face { font-family: "Outfit"; font-weight: 700; src: url("assets/fonts/outfit-700.woff2") format("woff2"); }
      @font-face { font-family: "Outfit"; font-weight: 800; src: url("assets/fonts/outfit-800.woff2") format("woff2"); }
      @font-face { font-family: "Outfit"; font-weight: 900; src: url("assets/fonts/outfit-900.woff2") format("woff2"); }
      @font-face { font-family: "Outfit"; font-weight: 500; src: url("assets/fonts/outfit-ext-500.woff2") format("woff2"); unicode-range: U+20A0-20C0, U+0100-024F; }
      @font-face { font-family: "Outfit"; font-weight: 700; src: url("assets/fonts/outfit-ext-700.woff2") format("woff2"); unicode-range: U+20A0-20C0, U+0100-024F; }
      @font-face { font-family: "Outfit"; font-weight: 800; src: url("assets/fonts/outfit-ext-800.woff2") format("woff2"); unicode-range: U+20A0-20C0, U+0100-024F; }
      @font-face { font-family: "Outfit"; font-weight: 900; src: url("assets/fonts/outfit-ext-900.woff2") format("woff2"); unicode-range: U+20A0-20C0, U+0100-024F; }
      @font-face { font-family: "JBMono"; font-weight: 500; src: url("assets/fonts/jbmono-500.woff2") format("woff2"); }
      @font-face { font-family: "JBMono"; font-weight: 700; src: url("assets/fonts/jbmono-700.woff2") format("woff2"); }
      :root { --bg: #0a0a0b; --surface: #141416; --surface2: #1b1b1f; --line: #2a2a30; --ink: #f5f6f8; --text: #c8ccd4; --muted: #8a909c;
              --y: #f2c811; --teal: #2dd4bf; --red: #ff4d5e; --orange: #e07a52; --blue: #8fb4ff; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--bg); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Outfit", sans-serif; color: var(--ink); }
      svg { display: block; }
      .lay { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
      #chat, #mont, #end { opacity: 0; }

      /* ---------- speaker ---------- */
      #spk { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; z-index: 1; background: var(--bg); }
      #spkm, #spkz { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
      #spkv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }

      /* ---------- top panel (split mode) ---------- */
      #panel { position: absolute; left: 0; top: 0; width: 1080px; height: {{PH}}px; z-index: 3; overflow: hidden;
               background: radial-gradient(ellipse at 18% 0%, rgba(242,200,17,.16), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 100% 100%, rgba(45,212,191,.14), rgba(0,0,0,0) 55%), var(--bg); }
      #pgrid { position: absolute; left: -120px; top: -120px; width: 1320px; height: 1140px;
               background-image: linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px); background-size: 60px 60px; }
      #pline { position: absolute; left: 0; top: {{PH}}px; width: 1080px; height: 8px; margin-top: -4px; z-index: 4; background: linear-gradient(90deg, var(--y), #ffe680, var(--teal)); box-shadow: 0 0 30px rgba(242,200,17,.7); transform-origin: 0 50%; }
      .ps { position: absolute; left: 0; top: 0; width: 1080px; height: {{PH}}px; }
      .kick { display: inline-flex; align-items: center; gap: 12px; font-weight: 800; font-size: 30px; letter-spacing: 4px; text-transform: uppercase; color: var(--y);
              background: rgba(242,200,17,.12); border: 2px solid rgba(242,200,17,.4); padding: 8px 22px; border-radius: 999px; }
      .ph { font-weight: 900; font-size: 74px; line-height: 1.02; letter-spacing: -1px; }
      .ph b { color: var(--y); }
      .phead { position: absolute; left: 60px; right: 60px; top: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 18px; }

      /* P1 stages */
      #stgrid { position: absolute; left: 60px; top: 390px; width: 960px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
      .stg { height: 150px; border-radius: 26px; background: var(--surface); border: 2px solid var(--line); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; position: relative; }
      .stg .si { width: 56px; height: 56px; } .stg .sl { font-weight: 800; font-size: 34px; }
      .stg .sn { position: absolute; left: 16px; top: 12px; font-family: "JBMono"; font-weight: 700; font-size: 22px; color: var(--muted); }
      #slow { position: absolute; left: 90px; right: 90px; top: 742px; display: flex; align-items: center; gap: 20px; font-weight: 700; font-size: 28px; color: var(--muted); }
      #slowtrack { flex: 1; height: 16px; border-radius: 99px; background: var(--surface2); overflow: hidden; }
      #slowbar { width: 100%; height: 100%; background: repeating-linear-gradient(45deg, var(--red), var(--red) 14px, #c93342 14px, #c93342 28px); transform-origin: 0 50%; }

      /* P2 connect */
      #nodes { position: absolute; left: 0; top: 400px; width: 1080px; height: 300px; }
      .node { position: absolute; top: 0; width: 250px; display: flex; flex-direction: column; align-items: center; gap: 18px; }
      .node .nb { width: 190px; height: 190px; border-radius: 48px; background: var(--surface); border: 3px solid var(--line); display: flex; align-items: center; justify-content: center; box-shadow: 0 20px 50px rgba(0,0,0,.5); }
      .node .nb svg { width: 110px; height: 110px; }
      .node .nl { font-weight: 800; font-size: 38px; }
      #nC { left: 40px; } #nC .nb { border-color: rgba(224,122,82,.7); box-shadow: 0 0 60px rgba(224,122,82,.35); }
      #nP { right: 40px; } #nP .nb { border-color: rgba(242,200,17,.7); box-shadow: 0 0 60px rgba(242,200,17,.35); }
      #nM { left: 415px; } #nM .nb { background: var(--y); border-color: #ffe680; box-shadow: 0 0 80px rgba(242,200,17,.6); }
      #links { position: absolute; left: 0; top: 400px; width: 1080px; height: 190px; }
      #auto { position: absolute; left: 0; right: 0; top: 770px; display: flex; justify-content: center; }
      .pill { display: inline-flex; align-items: center; gap: 14px; font-weight: 800; font-size: 34px; padding: 12px 30px; border-radius: 999px; }
      .pill svg { width: 40px; height: 40px; }
      #auto .pill { background: rgba(45,212,191,.15); border: 2px solid var(--teal); color: var(--teal); }

      /* P3 access + prompt */
      #acc { position: absolute; left: 90px; right: 90px; top: 330px; display: flex; justify-content: space-between; gap: 18px; }
      .acc { flex: 1; display: flex; align-items: center; gap: 14px; background: var(--surface); border: 2px solid var(--line); border-radius: 22px; padding: 22px 20px; font-weight: 700; font-size: 29px; }
      .acc svg { width: 42px; height: 42px; flex: none; }
      #prompt { position: absolute; left: 90px; right: 90px; top: 500px; background: var(--surface2); border: 2px solid var(--line); border-radius: 30px; padding: 30px 34px; }
      #prompt .who { font-weight: 700; font-size: 24px; color: var(--muted); margin-bottom: 10px; letter-spacing: 2px; text-transform: uppercase; }
      #ptxt { font-weight: 600; font-size: 40px; line-height: 1.25; min-height: 150px; }
      .caret { display: inline-block; width: 4px; height: 42px; background: var(--y); vertical-align: -6px; margin-left: 4px; }
      #psend { position: absolute; right: 26px; bottom: 22px; width: 64px; height: 64px; border-radius: 50%; background: var(--y); color: #0a0a0b; display: flex; align-items: center; justify-content: center; }
      #psend svg { width: 36px; height: 36px; transform: rotate(-90deg); }

      /* P4 package */
      #pkgs { position: absolute; left: 70px; right: 70px; top: 300px; display: flex; flex-direction: column; gap: 16px; }
      .pkc { display: flex; align-items: center; gap: 26px; background: var(--surface); border: 2px solid var(--line); border-radius: 28px; padding: 14px 28px; }
      .pki { width: 84px; height: 84px; flex: none; } .pki svg { width: 84px; height: 84px; }
      .pkt { font-weight: 800; font-size: 40px; } .pks { font-weight: 500; font-size: 26px; color: var(--muted); margin-top: 2px; }
      .pkk { margin-left: auto; width: 52px; height: 52px; flex: none; } .pkk svg { width: 52px; height: 52px; }
      #stats { position: absolute; left: 70px; right: 70px; top: 690px; display: flex; justify-content: space-between; }
      .st { font-weight: 700; font-size: 25px; color: var(--muted); text-align: center; } .st b { display: block; font-size: 40px; color: var(--ink); font-weight: 900; }

      /* P5 CTA */
      #cbox { position: absolute; left: 90px; right: 90px; top: 360px; height: 120px; border-radius: 999px; background: var(--surface2); border: 3px solid var(--line); display: flex; align-items: center; padding: 0 40px; gap: 22px; }
      #cav { width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, var(--y), var(--teal)); flex: none; }
      #ctxt { font-weight: 800; font-size: 50px; color: var(--ink); letter-spacing: 2px; }
      #cph { position: absolute; left: 132px; font-weight: 500; font-size: 40px; color: var(--muted); }
      #cpost { position: absolute; right: 30px; font-weight: 800; font-size: 36px; color: var(--y); }
      #cbub { position: absolute; left: 90px; top: 520px; display: flex; align-items: center; gap: 20px; }
      #cbub .av { width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, var(--y), var(--teal)); }
      #cbub .bb { background: var(--ink); color: #0a0a0b; font-weight: 900; font-size: 46px; padding: 16px 34px; border-radius: 36px 36px 36px 8px; }
      #heart { position: absolute; left: 470px; top: 528px; width: 72px; height: 72px; }
      #url { position: absolute; left: 0; right: 0; top: 700px; display: flex; justify-content: center; }
      #url .pill { background: var(--y); color: #0a0a0b; font-size: 40px; padding: 16px 38px; box-shadow: 0 10px 40px rgba(242,200,17,.45); }

      /* ---------- full-frame overlays ---------- */
      #hook { position: absolute; left: 0; top: 1060px; width: 1080px; z-index: 6; display: flex; flex-direction: column; align-items: center; text-align: center; }
      #hk0 { margin-bottom: 16px; } #hk0 .kick { background: var(--y); color: #0a0a0b; border-color: var(--y); font-size: 34px; }
      #hk1 { font-weight: 900; font-size: 104px; line-height: .98; text-transform: uppercase; -webkit-text-stroke: 12px #0a0a0b; paint-order: stroke fill; text-shadow: 0 8px 30px rgba(0,0,0,.6); }
      #hk2 { font-weight: 900; font-size: 168px; line-height: .95; text-transform: uppercase; color: var(--y); -webkit-text-stroke: 16px #0a0a0b; paint-order: stroke fill; text-shadow: 0 10px 0 rgba(0,0,0,.35), 0 0 60px rgba(242,200,17,.55); }
      #hk3 { margin-top: 14px; font-weight: 900; font-size: 64px; text-transform: uppercase; background: #0a0a0b; padding: 6px 30px; border-radius: 18px; }
      #hk3 b { color: var(--y); }
      #hkarrow { position: absolute; left: 820px; top: -170px; width: 120px; height: 150px; color: var(--y); }

      #roles { position: absolute; left: 540px; top: 240px; width: 510px; z-index: 6; display: flex; flex-direction: column; gap: 22px; }
      .role { display: flex; align-items: center; gap: 18px; background: rgba(10,10,11,.86); border: 2px solid var(--line); border-radius: 26px; padding: 18px 24px; position: relative; box-shadow: 0 18px 40px rgba(0,0,0,.45); }
      .role .ri { width: 86px; height: 86px; border-radius: 50%; background: var(--surface2); display: flex; align-items: center; justify-content: center; flex: none; } .role .ri svg { width: 46px; height: 46px; }
      .role .rt { font-weight: 800; font-size: 46px; line-height: 1.05; } .role .rq { color: var(--y); }
      .role .rx { position: absolute; right: -16px; top: -16px; width: 60px; height: 60px; }

      #deliv { position: absolute; left: 0; right: 0; top: 1030px; z-index: 6; display: flex; justify-content: center; }
      #deliv .pill { background: var(--teal); color: #06221f; font-size: 48px; padding: 16px 40px; box-shadow: 0 14px 40px rgba(45,212,191,.5); }
      #deliv .pill svg { width: 54px; height: 54px; }

      #hd { position: absolute; left: 0; top: 150px; width: 1080px; z-index: 6; display: flex; flex-direction: column; align-items: center; }
      #hdrow { display: flex; align-items: center; gap: 18px; } #hdrow .big { font-size: 112px; }
      #hdclock { width: 108px; height: 108px; }
      .big { font-weight: 900; font-size: 132px; line-height: 1; text-transform: uppercase; -webkit-text-stroke: 14px #0a0a0b; paint-order: stroke fill; text-shadow: 0 8px 0 rgba(0,0,0,.45), 0 10px 40px rgba(0,0,0,.5); }
      #hdH { color: #fff; } #hdD { color: var(--red); }
      #hdarr { width: 70px; height: 70px; color: #fff; }
      #hdsub { margin-top: 18px; font-weight: 800; font-size: 44px; background: var(--red); padding: 6px 28px; border-radius: 16px; text-transform: uppercase; }

      #pw { position: absolute; left: 0; top: 140px; width: 1080px; z-index: 6; display: flex; flex-direction: column; align-items: center; }
      #pwrow { display: flex; align-items: center; gap: 22px; }
      #pwAI { color: var(--orange); } #pwP { color: #fff; } #pwM { color: var(--y); }
      #pwsub { margin-top: 18px; font-weight: 900; font-size: 54px; text-transform: uppercase; background: var(--y); color: #0a0a0b; padding: 8px 32px; border-radius: 18px; box-shadow: 0 10px 40px rgba(242,200,17,.45); }

      #price { position: absolute; left: 0; top: 110px; width: 1080px; z-index: 6; display: flex; flex-direction: column; align-items: center; }
      #prk .kick { background: rgba(10,10,11,.8); }
      #prv { font-weight: 900; font-size: 250px; line-height: 1; color: var(--y); text-shadow: 0 14px 0 rgba(0,0,0,.35), 0 0 90px rgba(242,200,17,.6); letter-spacing: -6px; -webkit-text-stroke: 18px #0a0a0b; paint-order: stroke fill; }
      #prs { font-weight: 900; font-size: 42px; background: #fff; color: #0a0a0b; padding: 8px 28px; border-radius: 16px; text-transform: uppercase; }
      .coin { position: absolute; left: 518px; top: 150px; opacity: 0; width: 44px; height: 44px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #fff3a8, var(--y) 55%, #b8940a); box-shadow: 0 0 20px rgba(242,200,17,.7); }

      /* ---------- full-screen b-roll ---------- */
      #chat { position: absolute; inset: 0; z-index: 5; background: radial-gradient(ellipse at 50% 0%, rgba(242,200,17,.13), rgba(0,0,0,0) 60%), var(--bg); }
      #cgrid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.035) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.035) 2px, transparent 2px); background-size: 60px 60px; }
      #win { position: absolute; left: 50px; top: 420px; width: 980px; height: 860px; border-radius: 34px; background: var(--surface); border: 2px solid var(--line); box-shadow: 0 40px 100px rgba(0,0,0,.6); overflow: hidden; }
      #wbar { height: 76px; background: var(--surface2); border-bottom: 2px solid var(--line); display: flex; align-items: center; padding: 0 28px; gap: 12px; }
      .wd { width: 18px; height: 18px; border-radius: 50%; }
      #wtitle { margin-left: 18px; font-weight: 700; font-size: 28px; color: var(--text); display: flex; align-items: center; gap: 12px; } #wtitle svg { width: 34px; height: 34px; }
      #wconn { margin-left: auto; display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 24px; color: var(--teal); }
      #wconn i { width: 14px; height: 14px; border-radius: 50%; background: var(--teal); box-shadow: 0 0 14px var(--teal); }
      #wbody { position: absolute; left: 0; top: 76px; right: 0; bottom: 0; padding: 30px 34px; }
      #ufile { display: inline-flex; align-items: center; gap: 14px; background: rgba(45,212,191,.1); border: 2px solid rgba(45,212,191,.5); border-radius: 18px; padding: 12px 20px; font-weight: 700; font-size: 28px; color: var(--teal); }
      #ufile svg { width: 34px; height: 34px; }
      #ubub { margin-top: 24px; margin-left: auto; width: 760px; background: var(--y); color: #0a0a0b; border-radius: 30px 30px 8px 30px; padding: 22px 28px; font-weight: 700; font-size: 36px; line-height: 1.25; min-height: 110px; }
      #ubub .caret { background: #0a0a0b; }
      #tools { margin-top: 22px; display: flex; flex-direction: column; gap: 10px; font-family: "JBMono"; font-weight: 500; font-size: 26px; color: var(--muted); }
      .tl b { color: var(--teal); font-weight: 700; }
      #reply { margin-top: 18px; display: flex; gap: 22px; align-items: flex-start; }
      #reply .cl { width: 56px; height: 56px; flex: none; }
      #reply .rt { font-weight: 700; font-size: 32px; color: var(--ink); line-height: 1.3; }
      #reply .rt b { color: var(--teal); }
      #dshot { position: absolute; left: 80px; top: 640px; width: 920px; border-radius: 22px; border: 3px solid rgba(242,200,17,.7); box-shadow: 0 30px 80px rgba(0,0,0,.7), 0 0 60px rgba(242,200,17,.35); }
      #pip { position: absolute; left: 770px; top: 130px; width: 250px; height: 250px; border-radius: 50%; overflow: hidden; border: 6px solid var(--y); box-shadow: 0 16px 40px rgba(0,0,0,.6); }
      #pipv { position: absolute; left: -109px; top: -136px; width: 540px; height: 960px; object-fit: cover; }
      #chead { position: absolute; left: 60px; top: 170px; width: 680px; }
      #chead .ph { font-size: 68px; }

      #mont { position: absolute; inset: 0; z-index: 5; background: radial-gradient(ellipse at 50% 45%, rgba(242,200,17,.20), rgba(0,0,0,0) 60%), var(--bg); perspective: 1600px; }
      #mgrid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.04) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.04) 2px, transparent 2px); background-size: 60px 60px; }
      .mimg { position: absolute; left: 60px; top: 640px; width: 960px; border-radius: 24px; border: 3px solid rgba(255,255,255,.18); box-shadow: 0 40px 100px rgba(0,0,0,.7); }
      #timer { position: absolute; left: 0; right: 0; top: 230px; display: flex; flex-direction: column; align-items: center; gap: 10px; }
      #tval { font-family: "JBMono"; font-weight: 700; font-size: 170px; color: #fff; letter-spacing: -4px; text-shadow: 0 0 50px rgba(242,200,17,.5); }
      #tlab { font-weight: 800; font-size: 36px; color: var(--y); letter-spacing: 6px; text-transform: uppercase; }
      #ready { position: absolute; left: 0; right: 0; top: 1110px; display: flex; justify-content: center; }
      #ready .pill { background: var(--teal); color: #06221f; font-size: 72px; padding: 18px 54px; box-shadow: 0 20px 60px rgba(45,212,191,.55); }
      #ready .pill svg { width: 78px; height: 78px; }

      /* ---------- end card ---------- */
      #end { position: absolute; inset: 0; z-index: 9; background: radial-gradient(ellipse at 50% 30%, rgba(242,200,17,.20), rgba(0,0,0,0) 60%), radial-gradient(ellipse at 50% 100%, rgba(45,212,191,.16), rgba(0,0,0,0) 55%), var(--bg); overflow: hidden; perspective: 1800px; }
      .eimg { position: absolute; width: 640px; border-radius: 18px; opacity: .32; border: 2px solid rgba(255,255,255,.15); }
      #e0 { left: -150px; top: 140px; transform: rotateY(28deg) rotate(-6deg); } #e1 { right: -170px; top: 260px; transform: rotateY(-28deg) rotate(6deg); }
      #e2 { left: -120px; top: 1450px; transform: rotateY(24deg) rotate(5deg); } #e3 { right: -150px; top: 1560px; transform: rotateY(-24deg) rotate(-5deg); }
      #ecol { position: absolute; left: 0; right: 0; top: 330px; display: flex; flex-direction: column; align-items: center; text-align: center; }
      #elogo { width: 170px; height: 170px; border-radius: 44px; background: var(--surface); border: 3px solid rgba(242,200,17,.6); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 80px rgba(242,200,17,.45); }
      #elogo svg { width: 104px; height: 104px; }
      #ename { margin-top: 34px; font-weight: 900; font-size: 88px; line-height: 1; }
      #ename b { color: var(--y); }
      #etag { margin-top: 18px; font-weight: 600; font-size: 40px; color: var(--text); }
      #ebul { margin-top: 50px; display: flex; flex-direction: column; gap: 20px; align-items: flex-start; }
      .eb { display: flex; align-items: center; gap: 18px; font-weight: 700; font-size: 40px; } .eb svg { width: 50px; height: 50px; }
      #ebtn { margin-top: 60px; display: flex; align-items: center; gap: 22px; background: var(--y); color: #0a0a0b; font-weight: 900; font-size: 64px; padding: 26px 64px; border-radius: 999px; box-shadow: 0 20px 60px rgba(242,200,17,.5); position: relative; overflow: hidden; }
      #ebtn svg { width: 60px; height: 60px; }
      #shine { position: absolute; top: -20px; left: -200px; width: 120px; height: 200px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.75), rgba(255,255,255,0)); transform: skewX(-20deg); }
      #eurl { margin-top: 34px; font-weight: 800; font-size: 46px; color: var(--ink); letter-spacing: 1px; }
      #eurl span { color: var(--y); }
      #esub { margin-top: 12px; font-weight: 600; font-size: 30px; color: var(--muted); }

      /* ---------- captions ---------- */
      #capwrap { position: absolute; left: 0; top: 0; width: 1080px; height: 0; z-index: 8; }
      .cap { position: absolute; left: 50px; right: 50px; top: 0; display: flex; justify-content: center; transform: translateY(-50%); opacity: 0; }
      .capbox { text-align: center; font-weight: 900; font-size: 66px; line-height: 1.12; text-transform: uppercase;
                -webkit-text-stroke: 10px #000; paint-order: stroke fill; text-shadow: 0 6px 0 rgba(0,0,0,.55), 0 0 30px rgba(0,0,0,.55); }
      .w { display: inline-block; margin: 0 .13em; } .hl { color: var(--y); }

      /* ---------- transitions / vfx ---------- */
      #wipe { position: absolute; left: -700px; top: -200px; width: 600px; height: 2400px; z-index: 12; background: linear-gradient(90deg, rgba(242,200,17,0), var(--y) 30%, #fff3a8 50%, var(--y) 70%, rgba(242,200,17,0)); transform: rotate(14deg); }
      #iris { position: absolute; left: 540px; top: 960px; width: 10px; height: 10px; margin: -5px 0 0 -5px; z-index: 10; border-radius: 50%; box-shadow: 0 0 0 3000px var(--bg); opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{DURATION}}" data-width="1080" data-height="1920" data-fps="30">
      <div id="spk" data-layout-allow-overflow>
        <div id="spkm"><div id="spkz">
          <video id="spkv" src="{{VIDEO}}" muted playsinline data-start="0" data-duration="{{SPK_END}}" data-track-index="0"></video>
        </div></div>
        
      </div>

      <div id="panel" class="clip" data-start="18.5" data-duration="46.9" data-track-index="2">
        <div id="pgrid"></div>
        <div class="ps" id="P1">
          <div class="phead"><div class="kick">The old way</div><div class="ph">A pro dashboard = <b>6 stages</b></div></div>
          <div id="stgrid">{{STAGES}}</div>
          <div id="slow"><span>Manual build</span><div id="slowtrack"><div id="slowbar"></div></div><span id="slowpct">3%</span></div>
        </div>
        <div class="ps" id="P2">
          <div class="phead"><div class="kick">The new way</div><div class="ph">But we <b>automated</b> it</div></div>
          <svg id="links" viewBox="0 0 1080 190"><path id="lk1" d="M260 95H430" stroke="#e07a52" stroke-width="8" stroke-dasharray="16 14" fill="none"/><path id="lk2" d="M650 95H820" stroke="#f2c811" stroke-width="8" stroke-dasharray="16 14" fill="none"/>
            <circle id="dot1" cx="260" cy="95" r="11" fill="#fff"/><circle id="dot2" cx="650" cy="95" r="11" fill="#fff"/></svg>
          <div id="nodes">
            <div class="node" id="nC"><div class="nb">{{SPARK}}</div><div class="nl">Claude AI</div></div>
            <div class="node" id="nM"><div class="nb">{{PLUG}}</div><div class="nl">MCP</div></div>
            <div class="node" id="nP"><div class="nb">{{BARS}}</div><div class="nl">Power BI</div></div>
          </div>
          <div id="auto"><div class="pill">{{CHECK}} Workflow automated</div></div>
        </div>
        <div class="ps" id="P3">
          <div class="phead"><div class="kick">Step 1 · Step 2</div><div class="ph">Give access. <b>Just ask.</b></div></div>
          <div id="acc"><div class="acc" id="ac0">{{CHECK}} Read model</div><div class="acc" id="ac1">{{CHECK}} Run DAX</div><div class="acc" id="ac2">{{CHECK}} Build pages</div></div>
          <div id="prompt"><div class="who">You</div><div id="ptxt"><span id="ptyped"></span><span class="caret" id="pcaret"></span></div><div id="psend">{{ARROW}}</div></div>
        </div>
        <div class="ps" id="P4">
          <div class="phead"><div class="kick">Everything you get</div><div class="ph">The <b>complete</b> package</div></div>
          <div id="pkgs">{{PKG}}</div>
          <div id="stats"><div class="st" id="st0"><b>14</b>tools for Claude</div><div class="st" id="st1"><b>~10 min</b>setup, once</div><div class="st" id="st2"><b>8</b>designer themes</div><div class="st" id="st3"><b>1-click</b>Windows setup</div></div>
        </div>
        <div class="ps" id="P5">
          <div class="phead"><div class="kick">Want this workflow?</div><div class="ph">Comment <b>“LINK”</b></div></div>
          <div id="cbox"><div id="cav"></div><span id="cph">Add a comment…</span><span id="ctxt"></span><span class="caret" id="ccaret"></span><span id="cpost">Post</span></div>
          <div id="cbub"><div class="av"></div><div class="bb">LINK</div></div>
          <svg id="heart" viewBox="0 0 64 64"><path d="M32 56S6 40 6 22a13 13 0 0 1 26-4 13 13 0 0 1 26 4c0 18-26 34-26 34z" fill="#ff4d5e"/></svg>
          <div id="url"><div class="pill">powerbi.growora.live</div></div>
        </div>
      </div>
      <div id="pline" class="clip" data-start="18.5" data-duration="46.9" data-track-index="3"></div>

      <div id="hook_c" class="clip lay" data-start="0" data-duration="2.6" data-track-index="4"><div id="hook">
        <svg id="hkarrow" viewBox="0 0 120 150"><path d="M20 140C40 90 70 60 100 30" stroke="#f2c811" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M70 26l34 0 0 34" stroke="#f2c811" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div id="hk0"><div class="kick">Claude AI × Power BI</div></div>
        <div id="hk1">This dashboard?</div>
        <div id="hk2">Built by AI</div>
        <div id="hk3">in <b>10–15 minutes</b></div>
      </div></div>

      <div id="roles_c" class="clip lay" data-start="6.6" data-duration="3.3" data-track-index="4"><div id="roles">
        <div class="role" id="r0"><div class="ri">{{PERSON}}</div><div class="rt">Power BI<br>developer<span class="rq">?</span></div><div class="rx">{{CROSS}}</div></div>
        <div class="role" id="r1"><div class="ri">{{PERSON}}</div><div class="rt">Data<br>analyst<span class="rq">?</span></div><div class="rx">{{CROSS}}</div></div>
      </div></div>

      <div id="chat_c" class="clip lay" data-start="11.2" data-duration="6.7" data-track-index="5"><div id="chat">
        <div id="cgrid"></div>
        <div id="chead"><div class="kick">Claude + Power BI MCP</div><div class="ph" style="margin-top:18px">Just <b>ask</b> for it</div></div>
        <div id="win">
          <div id="wbar"><div class="wd" style="background:#ff5f57"></div><div class="wd" style="background:#febc2e"></div><div class="wd" style="background:#28c840"></div>
            <div id="wtitle">{{SPARK}} Claude</div><div id="wconn"><i></i>Power BI MCP</div></div>
          <div id="wbody">
            <div id="ufile">{{BARS}} Connected: Sales.pbix</div>
            <div id="ubub"><span id="utyped"></span><span class="caret" id="ucaret"></span></div>
            <div id="tools"><div class="tl" id="t0">▸ <b>list_tables</b>  ▸ <b>list_measures</b></div><div class="tl" id="t1">▸ <b>create_or_update_measure</b></div><div class="tl" id="t2">▸ <b>build_dashboard_page</b> · 3 cards · 4 charts</div></div>
            <div id="reply"><div class="cl">{{SPARK}}</div><div class="rt">Done! Your <b>Sales overview</b> page is ready.</div></div>
          </div>
          <img id="dshot" src="assets/dash/dashboard.jpg" alt="">
        </div>
        <div id="pip"><video id="pipv" src="{{VIDEO}}" muted playsinline data-start="11.2" data-duration="6.7" data-media-start="11.2" data-track-index="1"></video></div>
      </div></div>

      <div id="deliv_c" class="clip lay" data-start="17.8" data-duration="1.17" data-track-index="4"><div id="deliv"><div class="pill">{{CHECK}} Dashboard delivered</div></div></div>

      <div id="hd_c" class="clip lay" data-start="27.6" data-duration="2.25" data-track-index="4"><div id="hd">
        <div id="hdrow"><div id="hdclock">{{CLOCK}}</div><div class="big" id="hdH">Hours</div><div id="hdarr">{{ARROW}}</div><div class="big" id="hdD">Days</div></div>
        <div id="hdsub">Building it manually</div>
      </div></div>

      <div id="mont_c" class="clip lay" data-start="39.9" data-duration="3.15" data-track-index="5"><div id="mont">
        <div id="mgrid"></div>
        <div id="timer"><div id="tlab">Claude is building</div><div id="tval">00:00</div><div id="tlab2" class="kick">10–15 min · not days</div></div>
        {{MONTAGE}}
        <div id="ready"><div class="pill">{{CHECK}} READY</div></div>
      </div></div>

      <div id="pw_c" class="clip lay" data-start="43.6" data-duration="2.8" data-track-index="4"><div id="pw">
        <div id="pwrow"><div class="big" id="pwAI">AI</div><div class="big" id="pwP">+</div><div class="big" id="pwM">MCP</div></div>
        <div id="pwsub">Power BI automation</div>
      </div></div>

      <div id="price_c" class="clip lay" data-start="55.5" data-duration="3.55" data-track-index="4"><div id="price">
        <div id="prk"><div class="kick">Complete package</div></div>
        <div id="prv">₹299</div>
        <div id="prs">One-time · Instant download</div>
        <div class="coin" id="co0"></div><div class="coin" id="co1"></div><div class="coin" id="co2"></div><div class="coin" id="co3"></div><div class="coin" id="co4"></div><div class="coin" id="co5"></div>
      </div></div>

      <div id="end_c" class="clip lay" data-start="65.33" data-duration="4.17" data-track-index="6"><div id="end">
        <img class="eimg" id="e0" src="assets/dash/02-finance.jpg" alt=""><img class="eimg" id="e1" src="assets/dash/01-sales.jpg" alt="">
        <img class="eimg" id="e2" src="assets/dash/04-marketing.jpg" alt=""><img class="eimg" id="e3" src="assets/dash/03-hr.jpg" alt="">
        <div id="ecol">
          <div id="elogo">{{BARS}}</div>
          <div id="ename">Power BI MCP<br><b>for Claude</b></div>
          <div id="etag">Talk to your Power BI report.</div>
          <div id="ebul">
            <div class="eb" id="eb0">{{CHECK}} Reads your model &amp; runs DAX</div>
            <div class="eb" id="eb1">{{CHECK}} Writes measures for you</div>
            <div class="eb" id="eb2">{{CHECK}} Builds full dashboards</div>
          </div>
          <div id="ebtn">Get it · ₹299 {{ARROW}}<div id="shine"></div></div>
          <div id="eurl"><span>powerbi.</span>growora.live</div>
          <div id="esub">One-time payment · Instant download</div>
        </div>
      </div></div>

      <div id="capwrap" class="clip" data-start="0" data-duration="{{SPK_END}}" data-track-index="7">
        {{CAPTIONS}}
      </div>
      <div id="iris" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="8"></div>
      <div id="wipe" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="8"></div>
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const D = {{DURATION}}, PH = {{PH}}, SPLIT_Y = {{SPLIT_Y}}, SPK_END = {{SPK_END}};
      const CAPS = {{CAPS_JS}}, MODES = {{MODES_JS}}, ZOOMS = {{ZOOMS_JS}}, ST = {{STAGE_T}}, T = {{T}};
      const TR = 0.45;
      const CAP_FULL = 1395, CAP_SPLIT = PH;

      // ---------- speaker layout (full <-> split) + captions position
      tl.set("#spk", { y: 0, height: 1920 }, 0);
      tl.set("#spkm", { y: 0 }, 0);
      tl.set("#capwrap", { y: CAP_FULL }, 0);
      tl.set("#panel", { y: -PH - 20 }, 0);
      tl.set("#pline", { scaleX: 0 }, 0);
      MODES.forEach(([t, m], i) => {
        if (i === 0) return;
        const split = m === "split";
        const s = t - TR / 2;
        tl.to("#spk", { y: split ? PH : 0, height: split ? 1920 - PH : 1920, duration: TR, ease: "power3.inOut" }, s);
        tl.to("#spkm", { y: split ? SPLIT_Y : 0, duration: TR, ease: "power3.inOut" }, s);
        tl.to("#panel", { y: split ? 0 : -PH - 20, duration: TR, ease: "power3.inOut" }, s);
        tl.to("#pline", { scaleX: split ? 1 : 0, duration: TR, ease: "power2.inOut" }, s + (split ? 0.1 : 0));
        tl.to("#capwrap", { y: split ? CAP_SPLIT : CAP_FULL, duration: TR, ease: "power3.inOut" }, s);
      });
      tl.to("#pgrid", { x: 60, y: 60, duration: 46.9, ease: "none" }, 18.5);

      // ---------- zoom moves
      ZOOMS.forEach(([s, e, a, b, o]) => {
        tl.set("#spkz", { transformOrigin: o }, s);
        tl.fromTo("#spkz", { scale: a }, { scale: b, duration: e - s, ease: (b > a + 0.05 || a > b + 0.05) ? "power1.inOut" : "none", immediateRender: false }, s);
      });

      // ---------- captions: word pop-in, quick exit
      CAPS.forEach(([sel, s, e]) => {
        tl.set(sel, { opacity: 1 }, s);
        tl.fromTo(sel + " .w", { autoAlpha: 0, y: 26, scale: 0.55 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.2, ease: "back.out(2.6)", stagger: 0.05, immediateRender: false }, s);
        tl.fromTo(sel + " .hl", { scale: 1 }, { scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, s + 0.25);
        tl.to(sel, { opacity: 0, duration: 0.08 }, e - 0.08);
      });

      // ---------- transition helper
      const wipe = (t) => tl.fromTo("#wipe", { x: 0 }, { x: 2100, duration: 0.42, ease: "power2.inOut", immediateRender: false }, t - 0.21);

      // ---------- HOOK 0 - 2.4
      tl.fromTo("#hk0", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "back.out(2)" }, 0.05);
      tl.fromTo("#hk1", { autoAlpha: 0, scale: 1.6, filter: "blur(16px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }, 0.0);
      tl.fromTo("#hkarrow", { autoAlpha: 0, scale: 0.4, x: -30, y: 30 }, { autoAlpha: 1, scale: 1, x: 0, y: 0, duration: 0.35, ease: "back.out(2.4)" }, 0.3);
      tl.to("#hkarrow", { y: -14, x: 10, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut" }, 0.65);
      tl.fromTo("#hk2", { autoAlpha: 0, scale: 2.6, filter: "blur(24px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.38, ease: "expo.out" }, 0.42);
      tl.fromTo("#hk3", { autoAlpha: 0, y: 40, scale: 0.6 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(2.4)" }, 1.22);
      tl.to("#hk2", { scale: 1.05, duration: 1.4, ease: "none" }, 0.8);
      tl.to("#hook", { autoAlpha: 0, y: 60, scale: 0.9, duration: 0.28, ease: "power2.in" }, 2.2);

      // ---------- roles + "Whoever it is" sweep
      tl.fromTo("#r0", { autoAlpha: 0, x: 200, rotation: 6 }, { autoAlpha: 1, x: 0, rotation: 0, duration: 0.35, ease: "back.out(2)" }, T.roleA - 0.1);
      tl.fromTo("#r1", { autoAlpha: 0, x: 200, rotation: 6 }, { autoAlpha: 1, x: 0, rotation: 0, duration: 0.35, ease: "back.out(2)" }, T.roleB - 0.1);
      tl.set(".rx", { autoAlpha: 0, scale: 0 }, 0);
      tl.to("#r0 .rx", { autoAlpha: 1, scale: 1, duration: 0.2, ease: "back.out(3)" }, 9.48);
      tl.to("#r1 .rx", { autoAlpha: 1, scale: 1, duration: 0.2, ease: "back.out(3)" }, 9.6);
      tl.to(["#r0", "#r1"], { x: 600, autoAlpha: 0, rotation: 10, duration: 0.3, ease: "power3.in", stagger: 0.06 }, 9.6);
      wipe(9.40);

      // ---------- CHAT b-roll 11.2 - 17.9
      tl.fromTo("#chat", { autoAlpha: 0, scale: 1.25, filter: "blur(20px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, 11.2);
      tl.fromTo("#win", { y: 120 }, { y: 0, duration: 0.6, ease: "power3.out" }, 11.25);
      tl.fromTo("#chead", { autoAlpha: 0, x: -60 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: "power3.out" }, 11.4);
      tl.fromTo("#pip", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }, 11.6);
      tl.fromTo("#ufile", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "back.out(2)" }, 12.2);
      tl.fromTo("#ubub", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.25 }, 13.45);
      const U = "Build this sales dashboard for me. I need it in 10 minutes!";
      const P = "Build a sales overview page: totals, monthly trend vs last year, top regions.";
      const C = "LINK";
      const typer = { u: 0, p: 0, c: 0 };
      tl.set("#utyped", { textContent: "" }, 0);
      tl.to(typer, { u: U.length, duration: 2.0, ease: "none", onUpdate: () => { document.getElementById("utyped").textContent = U.slice(0, Math.round(typer.u)); } }, 13.5);
      tl.to("#ucaret", { opacity: 0, duration: 0.01 }, 15.55);
      tl.fromTo(["#t0", "#t1", "#t2"], { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: 0.2, stagger: 0.3, ease: "power2.out" }, 15.85);
      tl.fromTo("#reply", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.25 }, 16.75);
      tl.fromTo("#dshot", { autoAlpha: 0, scale: 0.5, y: 120, rotationX: 30 }, { autoAlpha: 1, scale: 1, y: 0, rotationX: 0, duration: 0.5, ease: "back.out(1.6)" }, 16.95);
      tl.to("#dshot", { scale: 1.04, duration: 0.7, ease: "none" }, 17.45);
      tl.to("#chat", { autoAlpha: 0, scale: 1.3, filter: "blur(16px)", duration: 0.3, ease: "power2.in" }, 17.62);
      tl.fromTo("#deliv", { autoAlpha: 0, scale: 0.3, rotation: -6 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.5)" }, 17.92);
      tl.to("#deliv", { autoAlpha: 0, y: -40, duration: 0.2 }, 18.72);

      // ---------- P1 stages 18.97 - 25.43
      ["#P2", "#P3", "#P4", "#P5"].forEach(s => tl.set(s, { autoAlpha: 0 }, 0));
      tl.fromTo("#P1 .phead", { autoAlpha: 0, y: -40 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power3.out" }, 19.15);
      ST.forEach((t, i) => tl.fromTo("#stg" + i, { autoAlpha: 0, scale: 0.4, y: 40 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.3, ease: "back.out(2.4)" }, t - 0.05));
      ST.forEach((t, i) => tl.fromTo("#stg" + i, { borderColor: "#f2c811" }, { borderColor: "#2a2a30", duration: 0.6, immediateRender: false }, t + 0.25));
      tl.fromTo("#slow", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 20.2);
      tl.fromTo("#slowbar", { scaleX: 0.03 }, { scaleX: 0.14, duration: 5.0, ease: "none" }, 20.3);
      const pct = { v: 3 };
      tl.to(pct, { v: 14, duration: 5.0, ease: "none", onUpdate: () => { document.getElementById("slowpct").textContent = Math.round(pct.v) + "%"; } }, 20.3);
      tl.to("#P1", { autoAlpha: 0, duration: 0.2 }, 25.3);

      // ---------- HOURS -> DAYS 27.6 - 29.83
      tl.fromTo("#hdclock", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }, 27.62);
      tl.fromTo("#hand1", { rotation: 0, svgOrigin: "50 50" }, { rotation: 1440, svgOrigin: "50 50", duration: 2.2, ease: "power1.in" }, 27.62);
      tl.fromTo("#hand2", { rotation: 0, svgOrigin: "50 50" }, { rotation: 240, svgOrigin: "50 50", duration: 2.2, ease: "power1.in" }, 27.62);
      tl.fromTo("#hdH", { autoAlpha: 0, scale: 2, filter: "blur(14px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, T.hours);
      tl.fromTo("#hdarr", { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: 0.25 }, T.days - 0.25);
      tl.fromTo("#hdD", { autoAlpha: 0, scale: 2.4, filter: "blur(18px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, T.days);
      tl.fromTo("#hdsub", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.25, ease: "back.out(2)" }, T.days + 0.25);
      tl.to("#hd", { autoAlpha: 0, scale: 1.3, duration: 0.15 }, 29.7);

      // ---------- BUT: drop into P2 connect 29.83 - 35.95
      tl.fromTo("#P2", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01 }, 29.83);
      tl.fromTo("#P2 .phead", { autoAlpha: 0, scale: 1.5, filter: "blur(14px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, 29.95);
      tl.set(["#lk1", "#lk2", "#dot1", "#dot2", "#auto"], { autoAlpha: 0 }, 0);
      tl.fromTo("#nC", { autoAlpha: 0, scale: 0.3, y: 50 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(2.2)" }, T.claude - 0.05);
      tl.fromTo("#nP", { autoAlpha: 0, scale: 0.3, y: 50 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(2.2)" }, T.pbi - 0.05);
      tl.fromTo("#nM", { autoAlpha: 0, scale: 0.3, rotation: -90 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.2)" }, T.mcp - 0.05);
      tl.to(["#lk1", "#lk2"], { autoAlpha: 1, duration: 0.2 }, T.mcp + 0.2);
      tl.fromTo(["#lk1", "#lk2"], { strokeDashoffset: 0 }, { strokeDashoffset: -300, duration: 2.6, ease: "none", immediateRender: false }, T.mcp + 0.2);
      tl.to(["#dot1", "#dot2"], { autoAlpha: 1, duration: 0.1 }, T.mcp + 0.3);
      tl.fromTo("#dot1", { attr: { cx: 260 } }, { attr: { cx: 430 }, duration: 0.6, repeat: 3, ease: "power1.inOut", immediateRender: false }, T.mcp + 0.3);
      tl.fromTo("#dot2", { attr: { cx: 650 } }, { attr: { cx: 820 }, duration: 0.6, repeat: 3, ease: "power1.inOut", immediateRender: false }, T.mcp + 0.3);
      tl.fromTo("#nM .nb", { scale: 1 }, { scale: 1.1, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, T.mcp + 0.5);
      tl.fromTo("#auto", { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: "back.out(2.6)" }, T.automate);
      tl.to(["#dot1", "#dot2"], { autoAlpha: 0, duration: 0.1 }, T.mcp + 2.7);
      tl.to("#P2", { autoAlpha: 0, x: -200, duration: 0.3, ease: "power3.in" }, 35.75);

      // ---------- P3 access + prompt 35.95 - 39.99
      tl.fromTo("#P3", { autoAlpha: 0, x: 200 }, { autoAlpha: 1, x: 0, duration: 0.35, ease: "power3.out" }, 35.95);
      tl.fromTo(["#ac0", "#ac1", "#ac2"], { autoAlpha: 0, y: 30, scale: 0.7 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.25, stagger: 0.3, ease: "back.out(2.4)" }, 36.5);
      tl.set("#ptyped", { textContent: "" }, 0);
      tl.to(typer, { p: P.length, duration: 1.5, ease: "none", onUpdate: () => { document.getElementById("ptyped").textContent = P.slice(0, Math.round(typer.p)); } }, 37.85);
      tl.to("#pcaret", { opacity: 0, duration: 0.01 }, 39.4);
      tl.fromTo("#psend", { scale: 1 }, { scale: 0.75, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }, 39.42);
      tl.to("#prompt", { y: -40, autoAlpha: 0, duration: 0.25, ease: "power2.in" }, 39.65);

      // ---------- MONTAGE 39.9 - 43.05
      tl.fromTo("#mont", { autoAlpha: 0, scale: 1.3 }, { autoAlpha: 1, scale: 1, duration: 0.25, ease: "expo.out" }, 39.9);
      const tv = { s: 0 };
      tl.set("#tval", { textContent: "00:00" }, 0);
      tl.to(tv, { s: 600, duration: 1.95, ease: "power2.in", onUpdate: () => { const s = Math.round(tv.s); document.getElementById("tval").textContent = String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); } }, 40.1);
      tl.fromTo("#tlab2", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.25 }, 40.3);
      for (let i = 0; i < {{NDASH}}; i++) {
        const t = 40.15 + i * 0.27;
        tl.fromTo("#m" + i, { autoAlpha: 0, rotationY: i % 2 ? -70 : 70, scale: 0.7, z: -300 },
                            { autoAlpha: 1, rotationY: 0, scale: 1, z: 0, duration: 0.22, ease: "power3.out" }, t);
        if (i < {{NDASH}} - 1) tl.to("#m" + i, { autoAlpha: 0, duration: 0.05 }, t + 0.27);
      }
      tl.to("#m" + ({{NDASH}} - 1), { scale: 1.05, duration: 0.8, ease: "none" }, 42.2);
      tl.fromTo("#ready", { autoAlpha: 0, scale: 2.4 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)" }, T.ready);
      tl.fromTo("#tval", { color: "#ffffff" }, { color: "#2dd4bf", duration: 0.2, immediateRender: false }, T.ready);
      tl.to("#mont", { autoAlpha: 0, scale: 1.2, filter: "blur(14px)", duration: 0.25, ease: "power2.in" }, 42.82);

      // ---------- AI + MCP = Power BI automation 43.6 - 46.4
      tl.fromTo("#pwAI", { autoAlpha: 0, scale: 2.2, filter: "blur(14px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, T.ai);
      tl.fromTo("#pwP", { autoAlpha: 0, rotation: -180, scale: 0.3 }, { autoAlpha: 1, rotation: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }, T.plusmcp - 0.15);
      tl.fromTo("#pwM", { autoAlpha: 0, scale: 2.2, filter: "blur(14px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, T.plusmcp);
      tl.fromTo("#pwsub", { autoAlpha: 0, scale: 0.4, rotation: -4 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.6)" }, T.automation);
      tl.to("#pw", { autoAlpha: 0, y: -60, duration: 0.2 }, 46.2);

      // ---------- P4 package 46.37 - 55.47
      tl.to("#P3", { autoAlpha: 0, duration: 0.2 }, 46.1);
      tl.fromTo("#P4", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01 }, 46.3);
      tl.fromTo("#P4 .phead", { autoAlpha: 0, y: -40 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power3.out" }, 46.55);
      [49.55, T.toolkit - 0.1, T.video - 0.1].forEach((t, i) => {
        tl.fromTo("#pk" + i, { autoAlpha: 0, x: i % 2 ? -260 : 260, scale: 0.9 }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.4, ease: "back.out(1.8)" }, t);
        tl.fromTo("#pk" + i + " .pkk", { autoAlpha: 0, scale: 0 }, { autoAlpha: 1, scale: 1, duration: 0.25, ease: "back.out(3)" }, t + 0.35);
      });
      tl.fromTo(["#st0", "#st1", "#st2", "#st3"], { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.2, ease: "back.out(2)" }, 54.1);
      tl.to("#P4", { autoAlpha: 0, duration: 0.2 }, 55.35);

      // ---------- PRICE 55.5 - 59.05
      tl.fromTo("#prk", { autoAlpha: 0, y: -30 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "back.out(2)" }, T.package);
      tl.fromTo("#prv", { autoAlpha: 0, scale: 3.2, filter: "blur(26px)" }, { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }, T.price);
      tl.fromTo("#prs", { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(2.6)" }, T.price + 0.55);
      tl.to("#prv", { scale: 1.06, duration: 1.6, ease: "none" }, T.price + 0.35);
      const coins = [[-430, 120], [420, 80], [-360, 330], [380, 340], [-170, 420], [200, 440]];
      coins.forEach(([dx, dy], i) => {
        tl.fromTo("#co" + i, { autoAlpha: 0, x: 0, y: 0, scale: 0.3 },
                             { autoAlpha: 1, x: dx, y: dy - 120, scale: 1, duration: 0.45, ease: "power2.out" }, T.price + 0.02 + i * 0.02);
        tl.to("#co" + i, { y: dy + 260, autoAlpha: 0, rotation: 200, duration: 0.8, ease: "power2.in" }, T.price + 0.47 + i * 0.02);
      });
      tl.to("#price", { autoAlpha: 0, scale: 0.9, duration: 0.2 }, 58.85);

      // ---------- P5 CTA 59.03 - 65.33
      tl.fromTo("#P5", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01 }, 59.0);
      tl.fromTo("#P5 .phead", { autoAlpha: 0, y: -40 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power3.out" }, 59.25);
      tl.fromTo("#cbox", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: "back.out(2)" }, 60.0);
      tl.set(["#cbub", "#heart"], { autoAlpha: 0 }, 0);
      tl.set("#ctxt", { textContent: "" }, 0);
      tl.to("#cph", { autoAlpha: 0, duration: 0.05 }, T.link - 0.08);
      tl.to(typer, { c: C.length, duration: 0.5, ease: "none", onUpdate: () => { document.getElementById("ctxt").textContent = C.slice(0, Math.round(typer.c)); } }, T.link - 0.05);
      tl.fromTo("#cpost", { scale: 1 }, { scale: 1.3, duration: 0.1, yoyo: true, repeat: 1, immediateRender: false }, T.comment - 0.1);
      tl.to(["#ctxt", "#ccaret"], { autoAlpha: 0, duration: 0.05 }, T.comment);
      tl.fromTo("#cbub", { autoAlpha: 0, y: -60, scale: 0.6 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2.2)" }, T.comment);
      tl.fromTo("#heart", { autoAlpha: 0, scale: 0 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(3.5)" }, T.comment + 0.25);
      tl.to("#heart", { scale: 1.2, duration: 0.2, yoyo: true, repeat: 3, ease: "sine.inOut" }, T.comment + 0.6);
      tl.fromTo("#url", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: "back.out(2)" }, T.share);
      tl.fromTo("#url .pill", { scale: 1 }, { scale: 1.06, duration: 0.35, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, T.share + 0.4);

      // ---------- END CARD 65.33 - 69.5
      tl.fromTo("#iris", { opacity: 0 }, { opacity: 1, duration: 0.01 }, 64.95);
      tl.fromTo("#iris", { scale: 240 }, { scale: 0.01, duration: 0.38, ease: "power3.in", immediateRender: false }, 64.95);
      tl.to("#iris", { opacity: 0, duration: 0.01 }, 65.4);
      tl.fromTo("#end", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01 }, 65.33);
      tl.fromTo(".eimg", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 0.32, scale: 1, duration: 0.6, stagger: 0.08, ease: "power3.out" }, 65.4);
      tl.to("#e0", { y: 60, duration: 4, ease: "none" }, 65.4); tl.to("#e1", { y: -60, duration: 4, ease: "none" }, 65.4);
      tl.to("#e2", { y: -50, duration: 4, ease: "none" }, 65.4); tl.to("#e3", { y: 50, duration: 4, ease: "none" }, 65.4);
      tl.fromTo("#elogo", { autoAlpha: 0, scale: 0.2, rotation: -30 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.4)" }, 65.4);
      tl.fromTo("#ename", { autoAlpha: 0, y: 40, filter: "blur(10px)" }, { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }, 65.6);
      tl.fromTo("#etag", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.3 }, 65.8);
      tl.fromTo(["#eb0", "#eb1", "#eb2"], { autoAlpha: 0, x: -60 }, { autoAlpha: 1, x: 0, duration: 0.3, stagger: 0.35, ease: "back.out(2)" }, 65.9);
      tl.fromTo("#ebtn", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)" }, 66.95);
      tl.fromTo("#shine", { x: 0 }, { x: 900, duration: 0.7, ease: "power2.inOut", repeat: 1, repeatDelay: 0.6, immediateRender: false }, 67.3);
      tl.to("#ebtn", { scale: 1.06, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }, 67.4);
      tl.fromTo("#eurl", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.3 }, 67.2);
      tl.fromTo("#esub", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 67.4);

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
