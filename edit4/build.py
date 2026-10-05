"""Generate index.html (HyperFrames composition) + sfx_cues.json for the Power BI MCP for Claude ad.

All times below are OUTPUT seconds. The speaker track (assets/speaker.mp4) is the source cut by cuts.SEGS;
src2out() converts word timings from the Tamil transcript (source/words_large.json) to output time.
"""
import json
import re

from cuts import CUT_TIMES, SPK_DUR, src2out as o

END = 4.3                      # end card length
DURATION = round(SPK_DUR + END, 3)
C1, C2, C3, C4 = CUT_TIMES[:4]  # 9.767 ipad-back | 16.933 laptop | 22.6 mug | 25.8 sofa
C5 = o(42.70)                   # in-source cut to the selfie shot (38.45)

# English captions translated from the Tamil voice-over. *word* = highlight.
CAPTIONS = [
    (o(6.66), o(8.78), "I want a *dashboard like this*"),
    (o(8.78), o(10.80), "Will a *Power BI developer* build it…"),
    (o(10.84), o(12.60), "…or a *data analyst?*"),
    (C1 + 0.02, o(14.52), "You need *neither!*"),
    (o(14.52), o(17.36), "Just give your *data + access* to *AI*"),
    (o(17.36), o(20.30), "and say: “I want a *dashboard like this*”"),
    (o(26.66), o(29.60), "While it *builds itself*… we do *our work*"),
    (o(30.30), o(33.10), "Normally, a *Power BI developer*…"),
    (o(33.10), o(35.30), "takes *hours*… or even *days*"),
    (o(35.46), o(37.62), "But with *Claude + MCP*"),
    (o(37.62), o(40.00), "the *Power BI connector*"),
    (o(40.00), o(42.70), "this dashboard took *10–15 minutes*"),
    (o(42.70), o(44.62), "A *professional dashboard* needs…"),
    (o(48.42), o(49.86), "*so many stages!*"),
    (o(49.86), o(52.30), "So a proper dashboard takes"),
    (o(52.30), o(54.42), "*hours… even days*"),
    (o(54.42), o(57.32), "But we *automated* this same workflow"),
    (o(57.32), o(61.46), "with *Claude AI + Power BI MCP*"),
    (o(61.46), o(64.98), "Gave it *access*, told it *what dashboard* we want"),
    (o(64.98), o(68.04), "*10–15 minutes*… dashboard *READY!*"),
    (o(68.04), o(70.88), "From *installation* to *dashboard creation*"),
    (o(70.88), o(73.38), "a complete *A–Z PDF guide*"),
    (o(73.38), o(75.12), "Get the complete guide"),
    (o(75.12), o(77.46), "for just *₹299*"),
    (o(77.46), o(79.86), "Want to learn this *AI + Power BI MCP* workflow?"),
    (o(79.86), o(83.00), "*Comment “LINK”* below"),
    (o(83.06), o(84.40), "we’ll *share the link!*"),
]

T = {  # named beats (output seconds)
    "hi": o(5.12), "like_this": o(7.68), "dev": o(8.78), "analyst": o(11.38),
    "neither": o(13.98), "data": o(14.52), "access": o(15.52), "ai": o(16.54), "ask": o(17.70), "send": o(19.60),
    "ready_talk": o(26.66),
    "hours": o(33.10), "days": o(34.36), "but": o(35.46), "claude": o(36.08), "mcp": o(36.88), "pbi": o(37.62),
    "min": o(40.48),
    "stages": [o(44.70), o(45.30), o(45.78), o(46.40), o(47.00), o(47.38), o(47.84)], "many": o(48.88),
    "h2": o(52.30), "d2": o(53.40), "but2": o(54.42), "claude2": o(57.32), "automate": o(60.20),
    "access2": o(62.06), "what": o(62.90), "just": o(64.98), "ready": o(66.86),
    "install": o(68.04), "creation": o(69.32), "atoz": o(70.88), "pdf": o(71.88), "guide_end": o(73.38),
    "price": o(75.36), "download": o(76.66), "learn": o(77.46), "link": o(81.34), "comment": o(82.44), "share": o(83.06),
}

STAGES = [("📋", "Requirements"), ("🗄️", "Data"), ("🧹", "Preparation"), ("🧩", "Modeling"),
          ("🧮", "DAX"), ("📊", "Visuals"), ("🧪", "Testing")]
SAMPLES = ["01-sales", "02-finance", "03-hr", "04-marketing", "05-ecommerce",
           "06-supply", "07-hospital", "08-support", "09-education", "10-projects"]
TOOLS = ["list_tables", "list_measures", "create_or_update_measure", "build_dashboard_page"]
PROMPT1 = "Build a sales dashboard: revenue, orders, margin %, sales by month, by channel and top products."
PROMPT2 = "Here’s my sales report. Build me a dashboard like this one."

# ---------------- sound design ----------------
# Standard, restrained ad sound design: whooshes on scene changes / big reveals, a few soft risers + impacts
# on the key beats. No pops, dings, clicks or typing.
SFX = [
    ("impact", 0.02, 0.32), ("whoosh", 0.00, 0.22),                       # open
    ("whoosh_soft", 3.35, 0.16),                                           # hook out
    ("whoosh", C1 - 0.18, 0.22),                                           # cut to iPad back
    ("impact", T["neither"], 0.22),                                        # "neither"
    ("whoosh_soft", T["ai"] - 0.15, 0.14),
    ("riser", C2 - 1.0, 0.10), ("whoosh", C2 - 0.15, 0.24),                # into laptop b-roll
    ("whoosh", C3 - 0.15, 0.20),                                           # cut to mug shot
    ("whoosh", C4 - 0.12, 0.20),                                           # cut to sofa shot
    ("whoosh_soft", T["but"] - 0.1, 0.16),                                 # old way -> new way
    ("riser", T["min"] - 1.45, 0.14), ("impact", T["min"], 0.30),          # 10-15 MIN
    ("whoosh", C5 - 0.15, 0.22),                                           # cut to selfie
    ("whoosh_soft", T["but2"] - 0.12, 0.18), ("impact", T["but2"] + 0.35, 0.22),   # AUTOMATED
    ("riser", T["just"] - 1.3, 0.12), ("whoosh", T["just"] - 0.12, 0.24), ("impact", T["just"] + 0.02, 0.26),  # ready showcase
    ("whoosh", T["install"] - 0.1, 0.20),                                  # guide
    ("riser", T["price"] - 1.45, 0.14), ("impact", T["price"], 0.32),      # price
    ("whoosh_soft", T["learn"] - 0.1, 0.16),                               # CTA
    ("riser", SPK_DUR - 1.4, 0.14), ("whoosh", SPK_DUR - 0.1, 0.26), ("impact", SPK_DUR + 0.05, 0.34),  # end card
]
# keyboard typing under the typed prompts (deterministic jitter)
for start, n in [(C2 + 0.35, 22), (T["what"] + 0.05, 16), (T["link"] - 0.35, 4)]:
    for i in range(n):
        SFX.append(("click", round(start + i * 0.062 + (i * 7 % 5) * 0.004, 3), round(0.16 + (i * 3 % 4) * 0.03, 3)))
SFX = [(n, round(t, 3), v) for n, t, v in SFX]


def caption_html(i, start, end, text):
    words = []
    for tok in re.split(r"(\*[^*]+\*)", text):
        if not tok:
            continue
        hl = tok.startswith("*")
        for w in tok.strip("*").split():
            words.append(f'<span class="{"w hl" if hl else "w"}">{w}</span>')
    return (f'<div id="cap{i}" class="cap clip" data-start="{round(start, 3)}" data-duration="{round(end - start, 3)}" '
            f'data-track-index="20"><div class="capbox">{" ".join(words)}</div></div>')


CLAUDE_SVG = ('<svg viewBox="0 0 100 100"><g fill="#fff">' +
              "".join(f'<rect x="46" y="8" width="8" height="38" rx="4" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 45)) +
              '</g></svg>')
PBI_SVG = ('<svg viewBox="0 0 100 100"><rect x="18" y="52" width="16" height="34" rx="4" fill="#1a1400"/>'
           '<rect x="42" y="34" width="16" height="52" rx="4" fill="#1a1400"/><rect x="66" y="14" width="16" height="72" rx="4" fill="#1a1400"/></svg>')
CHECK = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="#22c55e"/><path d="M19 33l8 8 18-18" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="#ef4444"/><path d="M22 22l20 20M42 22l-20 20" stroke="#fff" stroke-width="8" stroke-linecap="round"/></svg>'


def lockup(prefix):
    return (f'<div class="lock" id="{prefix}">'
            f'<div class="tile cl" id="{prefix}a"><i>{CLAUDE_SVG}</i><span>Claude</span></div><b class="plus" id="{prefix}p1">+</b>'
            f'<div class="tile mc" id="{prefix}b"><i class="mcpi">MCP</i><span>Connector</span></div><b class="plus" id="{prefix}p2">+</b>'
            f'<div class="tile pb" id="{prefix}c"><i>{PBI_SVG}</i><span>Power BI</span></div></div>')


def build():
    caps = "\n      ".join(caption_html(i, *c) for i, c in enumerate(CAPTIONS))
    stages = "".join(f'<div class="stg" id="stg{i}"><em>{e}</em>{n}</div>' for i, (e, n) in enumerate(STAGES))
    tools = "".join(f'<div class="tool" id="tool{i}"><span class="spin"></span><span class="tick">{CHECK}</span>▸ {t}</div>' for i, t in enumerate(TOOLS))
    reel = "".join(f'<div class="rc" id="rc{i}"><img src="assets/{s}.webp" /></div>' for i, s in enumerate(SAMPLES))
    wall = "".join(f'<img src="assets/{SAMPLES[(i * 3) % 10]}.webp" />' for i in range(18))
    beats = {k: (round(v, 3) if not isinstance(v, list) else [round(x, 3) for x in v]) for k, v in T.items()}
    rep = {
        "{{CAPTIONS}}": caps, "{{STAGE_PILLS}}": stages, "{{TOOLS}}": tools, "{{REEL}}": reel, "{{WALL}}": wall,
        "{{LOCK1}}": lockup("lk1"), "{{LOCK2}}": lockup("lk2"), "{{CLAUDE}}": CLAUDE_SVG, "{{PBI}}": PBI_SVG,
        "{{CHECK}}": CHECK, "{{CROSS}}": CROSS, "{{PROMPT1}}": PROMPT1, "{{PROMPT2}}": PROMPT2,
        "{{CAPS_JS}}": json.dumps([[f"#cap{i}", round(s, 3), round(e, 3)] for i, (s, e, _) in enumerate(CAPTIONS)]),
        "{{T_JS}}": json.dumps(beats), "{{CUTS_JS}}": json.dumps([C1, C2, C3, C4, C5]),
        "{{DURATION}}": str(DURATION), "{{SPK}}": str(SPK_DUR),
    }
    # clip windows (start, duration) for each overlay group
    win = {
        "HOOK": (0, 3.9), "FOCUS": (T["like_this"] - 0.2, C1 - T["like_this"] + 0.2),
        "CHIPS": (T["dev"] - 0.1, T["neither"] + 0.9 - T["dev"] + 0.1),
        "FLOW": (T["data"] - 0.1, C2 - T["data"] + 0.1),
        "LAPTOP": (C2 - 0.05, C3 - C2 + 0.05), "BUILDING": (C3, C4 - C3),
        "OLDWAY": (o(30.30), T["but"] + 0.3 - o(30.30)), "NEWWAY": (T["but"] - 0.1, C5 - T["but"] + 0.1),
        "STAGES": (C5 + 0.3, T["just"] - C5 - 0.3), "SHOW": (T["just"] - 0.05, T["install"] - T["just"] + 0.05),
        "GUIDE": (T["install"], T["guide_end"] - T["install"]), "PRICE": (T["guide_end"], T["learn"] - T["guide_end"]),
        "CTA": (T["learn"], SPK_DUR - T["learn"]), "END": (SPK_DUR - 0.05, END + 0.05),
        "BRAND": (3.6, SPK_DUR - 3.6),
    }
    html = TEMPLATE
    for k, (s, d) in win.items():
        html = html.replace("{{%s}}" % k, f'data-start="{round(s, 3)}" data-duration="{round(d, 3)}"')
    for k, v in rep.items():
        html = html.replace(k, v)
    assert "{{" not in html, re.findall(r"\{\{\w+\}\}", html)
    open("index.html", "w").write(html)
    json.dump(sorted(SFX, key=lambda c: c[1]), open("sfx_cues.json", "w"), indent=1)
    print("duration", DURATION, "cuts", CUT_TIMES, "C5", C5)


TEMPLATE = (open("composition.tpl").read())

if __name__ == "__main__":
    build()
