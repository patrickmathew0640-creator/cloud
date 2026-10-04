"""Generate index.html (HyperFrames composition) and the SFX cue list for the MCP explainer edit.

All times are in seconds on the source video's timeline (the edit is not re-timed).
"""
import json
import re

DURATION = 57.7

# ---------------------------------------------------------------- captions
# (start, end, text). *word* = highlighted. Translated from the Tamil voice-over.
CAPTIONS = [
    (0.70, 2.60, "If I tell AI, “I have some *pending work*…”"),
    (2.60, 4.65, "“Can you *finish this task* for me?”"),
    (4.65, 5.55, "Will it *do it?*"),
    (5.60, 7.70, "Today we use *ChatGPT*, *Claude*…"),
    (7.70, 9.10, "and ask them *tons of questions*"),
    (9.10, 10.95, "*Write content*, *give ideas*, *write code*"),
    (10.95, 12.30, "And they do it, *right?*"),
    (12.30, 14.80, "But what if I say, “Open a file in *Google Drive*”"),
    (14.80, 17.60, "“Use the data in my *database*”"),
    (17.60, 20.30, "or “Do a task in an *external tool*”"),
    (20.30, 23.00, "“I’ll give you *access*” — and it *does it!*"),
    (23.10, 24.80, "That’s exactly what *MCP* is for"),
    (27.10, 29.30, "Simply put, MCP is a *bridge*"),
    (29.30, 33.40, "between AI and your *data*, *files* & *tools*"),
    (33.40, 37.10, "*AI → MCP → Tools & Data*"),
    (37.10, 41.30, "So AI goes from *just answering*…"),
    (41.30, 45.00, "…to actually *doing the tasks* you need"),
    (45.00, 47.80, "This is *AI’s next level*"),
    (47.80, 50.90, "Want to understand MCP *even more simply?*"),
    (50.90, 51.80, "*Follow* me!"),
    (51.80, 55.30, "Want an *MCP course* or *digital product*?"),
    (55.30, 57.60, "*Follow my channel* — it’s in the *next video*"),
]

# ---------------------------------------------------------------- layout modes
# full = speaker fills frame; split = graphic on top, speaker in the bottom half; card = full graphic
SCENES = [
    ("full", 0.0, 5.55),
    ("split", 5.55, 23.10),
    ("card", 23.10, 26.70),
    ("split", 26.70, 45.00),
    ("full", 45.00, DURATION),
]

# ---------------------------------------------------------------- SFX cues (file, time, volume)
SFX = [
    ("whoosh_soft", 0.00, 0.30),
    ("pop", 0.70, 0.30),
    ("whoosh", 5.40, 0.35),
    ("pop", 6.30, 0.28), ("pop", 6.96, 0.28), ("pop", 7.60, 0.22), ("click", 8.90, 0.35),
    ("click", 9.16, 0.40), ("click", 9.70, 0.40), ("click", 10.34, 0.40),
    ("whoosh_soft", 12.15, 0.30),
    ("pop", 13.00, 0.28), ("pop", 15.30, 0.28), ("pop", 18.30, 0.28),
    ("click", 20.70, 0.45), ("ding", 22.00, 0.22),
    ("riser", 21.65, 0.28),
    ("whoosh", 23.05, 0.35), ("impact", 24.30, 0.55),
    ("whoosh", 26.55, 0.35),
    ("click", 29.40, 0.40), ("click", 29.86, 0.40), ("click", 30.26, 0.40), ("ding", 32.24, 0.22),
    ("pop", 34.86, 0.28), ("pop", 35.46, 0.28), ("pop", 36.16, 0.28),
    ("whoosh_soft", 37.00, 0.30),
    ("pop", 39.70, 0.28), ("whoosh_soft", 41.30, 0.25), ("pop", 42.50, 0.28),
    ("click", 43.00, 0.40), ("click", 43.50, 0.40), ("click", 44.00, 0.40),
    ("whoosh", 44.85, 0.35), ("impact", 45.10, 0.45),
    ("whoosh_soft", 47.70, 0.25),
    ("click", 50.90, 0.45), ("pop", 50.95, 0.30),
    ("pop", 51.80, 0.30),
    ("click", 55.88, 0.45),
]


def caption_html(i, start, end, text):
    words = []
    for tok in re.split(r"(\*[^*]+\*)", text):
        if not tok:
            continue
        hl = tok.startswith("*")
        for w in tok.strip("*").split():
            cls = "w hl" if hl else "w"
            words.append(f'<span class="{cls}">{w}</span>')
    dur = round(end - start, 2)
    return (f'<div id="cap{i}" class="cap clip" data-start="{start}" data-duration="{dur}" '
            f'data-track-index="5"><div class="capbox">{" ".join(words)}</div></div>')


ICON = {
    "file": '<svg viewBox="0 0 64 64"><path d="M16 6h22l12 12v40H16z" fill="#fff" opacity=".95"/><path d="M38 6v12h12" fill="#cfd8ff"/><path d="M22 30h22M22 38h22M22 46h14" stroke="#5b6cff" stroke-width="3" stroke-linecap="round"/></svg>',
    "db": '<svg viewBox="0 0 64 64"><ellipse cx="32" cy="14" rx="20" ry="7" fill="#fff"/><path d="M12 14v36c0 4 9 7 20 7s20-3 20-7V14" fill="#fff" opacity=".9"/><path d="M12 26c0 4 9 7 20 7s20-3 20-7M12 38c0 4 9 7 20 7s20-3 20-7" stroke="#5b6cff" stroke-width="3" fill="none"/></svg>',
    "tool": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="12" fill="none" stroke="#fff" stroke-width="6"/><g stroke="#fff" stroke-width="7" stroke-linecap="round"><path d="M32 8v8M32 48v8M8 32h8M48 32h8M15 15l6 6M43 43l6 6M15 49l6-6M43 21l6-6"/></g></svg>',
    "ai": '<svg viewBox="0 0 64 64"><path d="M32 6l6 18 18 6-18 6-6 18-6-18-18-6 18-6z" fill="#fff"/><path d="M50 4l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="#ffd54a"/></svg>',
    "lock": '<svg viewBox="0 0 64 64"><rect x="14" y="28" width="36" height="28" rx="6" fill="#ff5d6c"/><path d="M22 28v-8a10 10 0 0 1 20 0v8" stroke="#ff5d6c" stroke-width="6" fill="none"/></svg>',
    "check": '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="26" fill="#2bd67b"/><path d="M20 33l8 8 16-17" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "chat": '<svg viewBox="0 0 64 64"><path d="M8 12h48v30H26l-12 10V42H8z" fill="#fff"/><circle cx="22" cy="27" r="3.5" fill="#5b6cff"/><circle cx="32" cy="27" r="3.5" fill="#5b6cff"/><circle cx="42" cy="27" r="3.5" fill="#5b6cff"/></svg>',
}


def build():
    caps = "\n      ".join(caption_html(i, *c) for i, c in enumerate(CAPTIONS))
    caps_js = json.dumps([[f"#cap{i}", s, e] for i, (s, e, _) in enumerate(CAPTIONS)])
    scenes_js = json.dumps(SCENES)
    html = TEMPLATE.replace("{{CAPTIONS}}", caps).replace("{{CAPS_JS}}", caps_js)
    html = html.replace("{{SCENES_JS}}", scenes_js).replace("{{DURATION}}", str(DURATION))
    for k, v in ICON.items():
        html = html.replace("{{ICON_%s}}" % k.upper(), v)
    open("index.html", "w").write(html)
    json.dump(SFX, open("sfx_cues.json", "w"), indent=1)


TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Poppins"; font-weight: 500; src: url("assets/fonts/poppins-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 700; src: url("assets/fonts/poppins-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 800; src: url("assets/fonts/poppins-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 900; src: url("assets/fonts/poppins-latin-900-normal.woff2") format("woff2"); }
      :root { --accent: #ffd54a; --blue: #5b6cff; --violet: #9b5bff; --green: #2bd67b; --ink: #0b0d1f; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Poppins", sans-serif; color: #fff; }

      /* ---------- speaker ---------- */
      #spk { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; z-index: 1; }
      #spkv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 45%; }
      #vig { position: absolute; inset: 0; z-index: 2; pointer-events: none;
             background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45) 100%); }

      /* ---------- graphic panel (top half in split mode / full in card mode) ---------- */
      #panel { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; z-index: 3; overflow: hidden;
               background: radial-gradient(circle at 30% 20%, #26306b 0%, #12153a 45%, #0b0d1f 100%); }
      #panel .grid { position: absolute; inset: -40px; opacity: .18;
               background-image: linear-gradient(rgba(255,255,255,.25) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.25) 1px, transparent 1px);
               background-size: 60px 60px; }
      #divider { position: absolute; left: 0; top: 957px; width: 1080px; height: 6px; z-index: 4;
                 background: linear-gradient(90deg, var(--blue), var(--violet), var(--accent)); box-shadow: 0 0 24px rgba(155,91,255,.8); transform-origin: 0 50%; }
      .scene { position: absolute; inset: 0; }
      .kicker { position: absolute; top: 70px; left: 0; right: 0; text-align: center; font-weight: 800; font-size: 34px; letter-spacing: .2em; color: var(--accent); }

      /* chat scene */
      .pills { position: absolute; top: 150px; left: 0; right: 0; display: flex; justify-content: center; gap: 28px; }
      .pill { padding: 18px 40px; border-radius: 999px; font-weight: 800; font-size: 44px; background: rgba(255,255,255,.1); border: 3px solid rgba(255,255,255,.35); }
      .bubbles { position: absolute; top: 330px; left: 110px; right: 110px; display: flex; flex-direction: column; gap: 34px; }
      .bubble { display: flex; align-items: center; gap: 26px; padding: 26px 34px; border-radius: 28px; background: #fff; color: var(--ink); font-weight: 700; font-size: 46px; box-shadow: 0 16px 40px rgba(0,0,0,.35); }
      .bubble svg { width: 64px; height: 64px; flex: none; }
      .bubble .ok { margin-left: auto; }

      .ask { position: absolute; left: 110px; right: 110px; top: 760px; height: 110px; border-radius: 999px; background: rgba(255,255,255,.12);
             border: 3px solid rgba(255,255,255,.4); display: flex; align-items: center; padding: 0 20px 0 44px; font-size: 40px; font-weight: 500; }
      .ask .send { margin-left: auto; width: 74px; height: 74px; border-radius: 50%; background: #fff; color: var(--ink); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 44px; }
      /* access scene */
      .cards { position: absolute; top: 210px; left: 60px; right: 60px; display: flex; justify-content: space-between; }
      .card { position: relative; width: 300px; height: 380px; border-radius: 34px; background: rgba(255,255,255,.08); border: 3px solid rgba(255,255,255,.25);
              display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 26px; }
      .card > svg { width: 130px; height: 130px; }
      .card .lbl { font-weight: 700; font-size: 36px; text-align: center; line-height: 1.15; }
      .card .badge { position: absolute; top: -26px; right: -18px; width: 88px; height: 88px; }
      .card .badge svg { position: absolute; inset: 0; width: 88px; height: 88px; }
      .card .badge span { position: absolute; inset: 0; display: block; transform-origin: 50% 50%; }
      .access { position: absolute; top: 680px; left: 0; right: 0; display: flex; justify-content: center; }
      .access span { padding: 22px 54px; border-radius: 999px; background: var(--green); color: #05230f; font-weight: 900; font-size: 50px; box-shadow: 0 0 40px rgba(43,214,123,.6); }

      /* MCP title card */
      #mcpcard { position: absolute; inset: 0; z-index: 6; display: flex; flex-direction: column; align-items: center; justify-content: center;
                 background: radial-gradient(circle at 50% 45%, #3b2a8f 0%, #151842 50%, #0b0d1f 100%); }
      #mcpcard .burst { position: absolute; width: 1400px; height: 1400px; border-radius: 50%;
                 background: radial-gradient(circle, rgba(255,213,74,.35) 0%, rgba(155,91,255,.15) 35%, rgba(0,0,0,0) 65%); }
      #mcpcard .big { position: relative; font-weight: 900; font-size: 330px; line-height: 1; letter-spacing: -.02em;
                 background: linear-gradient(180deg, #fff 0%, #ffe9a3 100%); -webkit-background-clip: text; background-clip: text; color: transparent;
                 filter: drop-shadow(0 12px 40px rgba(155,91,255,.7)); }
      #mcpcard .full { position: relative; display: flex; gap: 26px; margin-top: 30px; font-weight: 800; font-size: 70px; }
      #mcpcard .full span:first-letter { color: var(--accent); }

      /* diagram scene */
      .node { position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; border-radius: 40px; font-weight: 800; }
      .node svg { width: 90px; height: 90px; }
      #nAI { left: 70px; top: 330px; width: 250px; height: 250px; background: linear-gradient(160deg, #5b6cff, #3a2bb8); font-size: 52px; box-shadow: 0 0 50px rgba(91,108,255,.6); }
      #nMCP { left: 400px; top: 300px; width: 280px; height: 310px; background: linear-gradient(160deg, #ffd54a, #ff9f2e); color: var(--ink); font-size: 72px; font-weight: 900; box-shadow: 0 0 60px rgba(255,213,74,.6); }
      .rnode { left: 780px; width: 240px; height: 150px; background: rgba(255,255,255,.1); border: 3px solid rgba(255,255,255,.35); font-size: 40px; flex-direction: row; gap: 14px; border-radius: 30px; }
      .rnode svg { width: 56px; height: 56px; }
      #nData { top: 190px; } #nFiles { top: 380px; } #nTools { top: 570px; }
      #links { position: absolute; inset: 0; }
      #links path { fill: none; stroke: url(#lg); stroke-width: 8; stroke-linecap: round; }
      .packet { position: absolute; width: 26px; height: 26px; border-radius: 50%; background: #fff; box-shadow: 0 0 20px #fff, 0 0 40px var(--accent); }

      /* answers -> actions scene */
      .cmp { position: absolute; top: 180px; width: 430px; height: 600px; border-radius: 40px; padding: 40px 34px; display: flex; flex-direction: column; align-items: center; gap: 26px; }
      #cmpA { left: 60px; background: rgba(255,255,255,.07); border: 3px solid rgba(255,255,255,.25); }
      #cmpB { right: 60px; background: linear-gradient(170deg, rgba(43,214,123,.25), rgba(43,214,123,.08)); border: 3px solid var(--green); }
      .cmp h3 { font-size: 46px; font-weight: 900; text-align: center; line-height: 1.1; }
      .cmp > svg { width: 140px; height: 140px; }
      .cmp .sub { font-size: 34px; font-weight: 500; opacity: .8; text-align: center; }
      #strike { position: absolute; left: 30px; right: 30px; top: 300px; height: 10px; border-radius: 6px; background: #ff5d6c; transform-origin: 0 50%; transform: rotate(-12deg); }
      .todo { width: 100%; display: flex; flex-direction: column; gap: 18px; }
      .todo div { display: flex; align-items: center; gap: 18px; font-size: 36px; font-weight: 700; }
      .todo svg { width: 52px; height: 52px; flex: none; }
      #arrow { position: absolute; left: 505px; top: 420px; font-size: 90px; font-weight: 900; color: var(--accent); }

      /* ---------- hook / next level / CTA overlays (full mode) ---------- */
      #hook { position: absolute; top: 150px; left: 60px; right: 60px; z-index: 6; text-align: center; }
      #hook .l1, #hook .l2 { display: inline-block; font-weight: 900; font-size: 92px; line-height: 1.08; text-transform: uppercase; letter-spacing: -.01em;
                 text-shadow: 0 6px 0 rgba(0,0,0,.35), 0 0 30px rgba(0,0,0,.5); }
      #hook .l2 { color: var(--ink); background: var(--accent); padding: 4px 26px; border-radius: 18px; text-shadow: none; margin-top: 14px; }
      #flash { position: absolute; inset: 0; background: #fff; z-index: 20; opacity: 0; pointer-events: none; }
      #lvl { position: absolute; top: 170px; left: 0; right: 0; z-index: 6; display: flex; flex-direction: column; align-items: center; }
      #lvl .t { font-weight: 900; font-size: 120px; line-height: 1; text-transform: uppercase; text-shadow: 0 8px 0 rgba(0,0,0,.35), 0 0 40px rgba(155,91,255,.9); }
      #lvl .t b { color: var(--accent); }
      #lvl .bar { margin-top: 26px; width: 640px; height: 34px; border-radius: 20px; background: rgba(255,255,255,.2); overflow: hidden; border: 3px solid rgba(255,255,255,.6); }
      #lvl .fill { width: 100%; height: 100%; background: linear-gradient(90deg, var(--blue), var(--violet), var(--accent)); transform-origin: 0 50%; }
      #follow { position: absolute; top: 230px; left: 0; right: 0; z-index: 6; display: flex; justify-content: center; }
      #follow .btn { display: flex; align-items: center; gap: 22px; padding: 28px 64px; border-radius: 999px; background: linear-gradient(90deg, #ff3d6e, #ff7a3d); font-weight: 900; font-size: 72px; box-shadow: 0 18px 50px rgba(255,61,110,.55); }
      #follow .plus { width: 70px; height: 70px; border-radius: 50%; background: #fff; color: #ff3d6e; display: flex; align-items: center; justify-content: center; font-size: 66px; line-height: 1; }
      #tap { position: absolute; left: 640px; top: 330px; width: 90px; height: 90px; border-radius: 50%; border: 8px solid #fff; z-index: 7; }
      #promo { position: absolute; top: 420px; left: 90px; right: 90px; z-index: 6; padding: 34px 40px; border-radius: 34px; text-align: center;
               background: rgba(11,13,31,.82); border: 3px solid var(--accent); box-shadow: 0 20px 60px rgba(0,0,0,.5); }
      #promo .k { font-size: 34px; font-weight: 800; letter-spacing: .18em; color: var(--accent); }
      #promo .m { font-size: 58px; font-weight: 900; line-height: 1.15; margin-top: 10px; }

      /* ---------- captions ---------- */
      #capwrap { position: absolute; left: 0; top: 0; width: 1080px; z-index: 10; }
      .cap { position: absolute; left: 50px; right: 50px; top: 0; display: flex; justify-content: center; }
      .capbox { text-align: center; font-weight: 800; font-size: 62px; line-height: 1.2; text-transform: uppercase;
                -webkit-text-stroke: 3px #000; paint-order: stroke fill; text-shadow: 0 6px 0 rgba(0,0,0,.55), 0 0 26px rgba(0,0,0,.6); }
      .w { display: inline-block; }
      .hl { color: var(--accent); }

      /* progress bar */
      #prog { position: absolute; left: 0; top: 0; width: 1080px; height: 10px; z-index: 30; background: linear-gradient(90deg, var(--blue), var(--violet), var(--accent)); transform-origin: 0 50%; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{DURATION}}" data-width="1080" data-height="1920">

      <div id="spk" data-layout-allow-overflow>
        <video id="spkv" src="assets/speaker.mp4" muted playsinline data-start="0" data-duration="{{DURATION}}" data-track-index="0"></video>
      </div>
      <div id="vig" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="1"></div>

      <!-- Top graphic panel: visible in split scenes -->
      <div id="panel" class="clip" data-start="5.3" data-duration="40" data-track-index="2">
        <div class="grid"></div>

        <!-- 1: chat -->
        <div id="sChat" class="scene">
          <div class="kicker">WHAT WE DO TODAY</div>
          <div class="pills"><div class="pill" id="pGPT">ChatGPT</div><div class="pill" id="pClaude">Claude</div></div>
          <div class="bubbles">
            <div class="bubble" id="b1">{{ICON_CHAT}}<span>Write content</span><span class="ok">{{ICON_CHECK}}</span></div>
            <div class="bubble" id="b2">{{ICON_CHAT}}<span>Give me ideas</span><span class="ok">{{ICON_CHECK}}</span></div>
            <div class="bubble" id="b3">{{ICON_CHAT}}<span>Write code</span><span class="ok">{{ICON_CHECK}}</span></div>
          </div>
          <div class="ask" id="ask"><span id="askt">Ask anything…</span><span class="send">↑</span></div>
        </div>

        <!-- 2: access -->
        <div id="sAccess" class="scene">
          <div class="kicker">BUT WHAT ABOUT…</div>
          <div class="cards">
            <div class="card" id="k1">{{ICON_FILE}}<div class="lbl">Google Drive<br/>file</div><div class="badge"><span class="lk">{{ICON_LOCK}}</span><span class="ck">{{ICON_CHECK}}</span></div></div>
            <div class="card" id="k2">{{ICON_DB}}<div class="lbl">Your<br/>database</div><div class="badge"><span class="lk">{{ICON_LOCK}}</span><span class="ck">{{ICON_CHECK}}</span></div></div>
            <div class="card" id="k3">{{ICON_TOOL}}<div class="lbl">External<br/>tool</div><div class="badge"><span class="lk">{{ICON_LOCK}}</span><span class="ck">{{ICON_CHECK}}</span></div></div>
          </div>
          <div class="access" id="acc"><span>ACCESS GRANTED</span></div>
        </div>

        <!-- 3: diagram -->
        <div id="sDiag" class="scene">
          <div class="kicker">HOW MCP WORKS</div>
          <svg id="links" viewBox="0 0 1080 960">
            <defs><linearGradient id="lg" gradientUnits="userSpaceOnUse" x1="300" y1="0" x2="800" y2="0"><stop offset="0" stop-color="#5b6cff"/><stop offset="1" stop-color="#ffd54a"/></linearGradient></defs>
            <path id="l0" d="M320 455 L400 455"/>
            <path id="l1" d="M680 420 C730 420 730 265 780 265"/>
            <path id="l2" d="M680 455 L780 455"/>
            <path id="l3" d="M680 490 C730 490 730 645 780 645"/>
          </svg>
          <div class="node" id="nAI">{{ICON_AI}}<span>AI</span></div>
          <div class="node" id="nMCP"><span>MCP</span></div>
          <div class="node rnode" id="nData">{{ICON_DB}}<span>Data</span></div>
          <div class="node rnode" id="nFiles">{{ICON_FILE}}<span>Files</span></div>
          <div class="node rnode" id="nTools">{{ICON_TOOL}}<span>Tools</span></div>
          <div class="packet" id="pk1" style="left:307px;top:442px"></div>
          <div class="packet" id="pk2" style="left:667px;top:442px"></div>
        </div>

        <!-- 4: answers -> actions -->
        <div id="sCmp" class="scene">
          <div class="kicker">THE BIG SHIFT</div>
          <div class="cmp" id="cmpA">{{ICON_CHAT}}<h3>Just<br/>answers</h3><div class="sub">Text in, text out</div><div id="strike"></div></div>
          <div id="arrow">→</div>
          <div class="cmp" id="cmpB">{{ICON_AI}}<h3>Gets tasks<br/>done</h3>
            <div class="todo">
              <div id="t1">{{ICON_CHECK}}Reads files</div>
              <div id="t2">{{ICON_CHECK}}Uses data</div>
              <div id="t3">{{ICON_CHECK}}Runs tools</div>
            </div>
          </div>
        </div>
      </div>
      <div id="divider" class="clip" data-start="5.3" data-duration="40" data-track-index="3"></div>

      <!-- Full-screen MCP title card -->
      <div id="mcpcard" class="clip" data-start="23.0" data-duration="3.75" data-track-index="4">
        <div class="burst"></div>
        <div class="big">MCP</div>
        <div class="full"><span id="m1">Model</span><span id="m2">Context</span><span id="m3">Protocol</span></div>
      </div>

      <!-- Full-mode overlays -->
      <div id="hook" class="clip" data-start="0.2" data-duration="5.3" data-track-index="4">
        <div class="l1">Can AI finish</div><br/><div class="l2">your work?</div>
      </div>
      <div id="lvl" class="clip" data-start="45.0" data-duration="2.85" data-track-index="4">
        <div class="t">AI’s <b>next level</b></div>
        <div class="bar"><div class="fill"></div></div>
      </div>
      <div id="follow" class="clip" data-start="50.8" data-duration="6.9" data-track-index="4">
        <div class="btn"><span class="plus">+</span>FOLLOW</div>
      </div>
      <div id="tap" class="clip" data-start="50.8" data-duration="6.9" data-track-index="6"></div>
      <div id="promo" class="clip" data-start="51.75" data-duration="5.95" data-track-index="4">
        <div class="k">COMING IN THE NEXT VIDEO</div>
        <div class="m">MCP Course &amp; Digital Product</div>
      </div>

      <!-- Captions -->
      <div id="capwrap" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="5">
      {{CAPTIONS}}
      </div>

      <div id="prog" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="7"></div>
      <div id="flash" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="8"></div>
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const D = {{DURATION}};
      const SCENES = {{SCENES_JS}};
      const CAPS = {{CAPS_JS}};
      const T = 0.45; // layout transition length

      tl.set("#flash", { opacity: 0 }, 0);
      // ---------------- progress bar
      tl.fromTo("#prog", { scaleX: 0 }, { scaleX: 1, duration: D, ease: "none" }, 0);

      // ---------------- speaker layout per scene
      // full: wrapper fills frame. split: wrapper occupies bottom half, video shifted up so the face sits in it.
      tl.set("#spk", { y: 0, height: 1920 }, 0);
      tl.set("#spkv", { y: 0, scale: 1 }, 0);
      SCENES.forEach(([mode, start, end], i) => {
        if (i === 0) return;
        if (mode === "split") {
          tl.to("#spk", { y: 960, height: 960, duration: T, ease: "power3.inOut" }, start - 0.1);
          tl.to("#spkv", { y: -380, scale: 1, duration: T, ease: "power3.inOut" }, start - 0.1);
        } else if (mode === "full") {
          tl.to("#spk", { y: 0, height: 1920, duration: T, ease: "power3.inOut" }, start - 0.1);
          tl.to("#spkv", { y: 0, scale: 1, duration: T, ease: "power3.inOut" }, start - 0.1);
        }
      });
      // Slow push-ins / punch-ins on the full-frame speaker
      tl.fromTo("#spkv", { scale: 1.0 }, { scale: 1.07, duration: 5.0, ease: "none" }, 0.2);
      tl.to("#spkv", { scale: 1.0, duration: 0.3, ease: "power2.out" }, 5.25);
      tl.fromTo("#spkv", { scale: 1.18 }, { scale: 1.12, duration: 2.7, ease: "power2.out" }, 45.0);   // punch-in for "next level"
      tl.to("#spkv", { scale: 1.0, duration: 0.35, ease: "power2.inOut" }, 47.75);
      tl.fromTo("#spkv", { scale: 1.0 }, { scale: 1.06, duration: 9.5, ease: "none" }, 48.1);

      // ---------------- panel in/out + divider
      tl.fromTo("#panel", { y: -960 }, { y: 0, duration: T, ease: "power3.out" }, 5.45);
      tl.fromTo("#divider", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 5.55);
      tl.to("#panel", { y: -960, duration: T, ease: "power3.in" }, 44.75);
      tl.to("#divider", { scaleX: 0, duration: 0.3 }, 44.75);
      tl.to(".grid", { y: 60, duration: 40, ease: "none" }, 5.3);

      // Scene visibility inside the panel (cross-slide)
      const scn = [["#sChat", 5.3, 12.25], ["#sAccess", 12.25, 23.1], ["#sDiag", 26.6, 37.05], ["#sCmp", 37.05, 45.3]];
      tl.set(["#sAccess", "#sDiag", "#sCmp"], { autoAlpha: 0 }, 0);
      scn.forEach(([sel, s, e], i) => {
        if (i > 0) tl.fromTo(sel, { autoAlpha: 0, x: 200, filter: "blur(16px)" }, { autoAlpha: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }, s);
        if (i < scn.length - 1) tl.to(sel, { autoAlpha: 0, x: -200, filter: "blur(16px)", duration: 0.35, ease: "power3.in" }, e - 0.3);
      });

      // ---------------- chat scene
      tl.from("#sChat .kicker", { autoAlpha: 0, y: -20, duration: 0.4 }, 5.7);
      tl.from("#pGPT", { autoAlpha: 0, scale: 0.4, duration: 0.45, ease: "back.out(2.2)" }, 6.25);
      tl.from("#pClaude", { autoAlpha: 0, scale: 0.4, duration: 0.45, ease: "back.out(2.2)" }, 6.9);
      [["#b1", 9.1], ["#b2", 9.65], ["#b3", 10.3]].forEach(([s, t]) => {
        tl.from(s, { autoAlpha: 0, x: -120, duration: 0.35, ease: "power3.out" }, t);
        tl.from(s + " .ok", { scale: 0, duration: 0.35, ease: "back.out(3)" }, t + 0.35);
      });
      tl.from("#ask", { autoAlpha: 0, y: 60, duration: 0.4, ease: "back.out(1.8)" }, 7.6);
      tl.to("#ask .send", { scale: 0.8, duration: 0.1, yoyo: true, repeat: 1 }, 8.9);
      tl.to("#ask", { borderColor: "#ffd54a", duration: 0.25, yoyo: true, repeat: 3 }, 7.9);
      tl.to(".bubble", { scale: 1.03, duration: 0.25, yoyo: true, repeat: 1, stagger: 0.08 }, 11.0);

      // ---------------- access scene
      tl.from("#sAccess .kicker", { autoAlpha: 0, y: -20, duration: 0.4 }, 12.4);
      [["#k1", 12.95], ["#k2", 15.25], ["#k3", 18.25]].forEach(([s, t]) => {
        tl.from(s, { autoAlpha: 0, y: 80, scale: 0.85, duration: 0.45, ease: "back.out(1.8)" }, t);
        tl.from(s + " .lk", { scale: 0, rotation: -30, duration: 0.35, ease: "back.out(3)" }, t + 0.3);
      });
      tl.set(".ck", { scale: 0 }, 0);
      tl.to(".card", { x: "+=8", duration: 0.05, yoyo: true, repeat: 5 }, 19.9);  // "locked" shake
      tl.from("#acc", { autoAlpha: 0, scale: 0.5, duration: 0.4, ease: "back.out(2.5)" }, 20.7);
      tl.to(".lk", { scale: 0, duration: 0.2, stagger: 0.15 }, 21.6);
      tl.to(".ck", { scale: 1, duration: 0.35, ease: "back.out(3)", stagger: 0.15 }, 21.75);
      tl.to(".card", { borderColor: "#2bd67b", backgroundColor: "rgba(43,214,123,.15)", duration: 0.3, stagger: 0.15 }, 21.75);

      // ---------------- MCP card
      tl.fromTo("#mcpcard", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 23.05);
      tl.fromTo("#mcpcard .big", { scale: 2.6, autoAlpha: 0, filter: "blur(30px)" }, { scale: 1, autoAlpha: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, 24.25);
      tl.fromTo("#mcpcard .burst", { scale: 0.2, autoAlpha: 0 }, { scale: 1.1, autoAlpha: 1, duration: 0.8, ease: "expo.out" }, 24.25);
      tl.to("#mcpcard .big", { scale: 1.06, duration: 2.0, ease: "none" }, 24.7);
      [["#m1", 24.85], ["#m2", 25.3], ["#m3", 25.95]].forEach(([s, t]) =>
        tl.from(s, { autoAlpha: 0, y: 50, duration: 0.35, ease: "back.out(2)" }, t));
      tl.to("#mcpcard", { opacity: 0, scale: 1.15, duration: 0.3, ease: "power2.in" }, 26.45);
      tl.fromTo("#flash", { opacity: 0 }, { opacity: 0.85, duration: 0.06, yoyo: true, repeat: 1 }, 24.25);

      // ---------------- diagram scene
      tl.from("#sDiag .kicker", { autoAlpha: 0, y: -20, duration: 0.4 }, 26.8);
      tl.from("#nAI", { autoAlpha: 0, scale: 0.4, duration: 0.45, ease: "back.out(2)" }, 28.1);
      tl.from("#nMCP", { autoAlpha: 0, scale: 0.4, duration: 0.45, ease: "back.out(2)" }, 28.5);
      tl.set(["#l0", "#l1", "#l2", "#l3"], { strokeDasharray: 400, strokeDashoffset: 400 }, 0);
      tl.to("#l0", { strokeDashoffset: 0, duration: 0.4 }, 28.7);
      [["#nData", "#l1", 29.35], ["#nFiles", "#l2", 29.8], ["#nTools", "#l3", 30.2]].forEach(([n, l, t]) => {
        tl.from(n, { autoAlpha: 0, x: 80, duration: 0.35, ease: "power3.out" }, t);
        tl.to(l, { strokeDashoffset: 0, duration: 0.4 }, t);
      });
      tl.to("#nMCP", { scale: 1.12, duration: 0.2, yoyo: true, repeat: 1 }, 32.2);
      [["#nAI", 34.8], ["#nMCP", 35.4], ["#nData,#nFiles,#nTools", 36.1]].forEach(([n, t]) =>
        tl.to(n, { scale: 1.1, duration: 0.18, yoyo: true, repeat: 1 }, t));
      tl.set(["#pk1", "#pk2"], { opacity: 0, x: 0 }, 0);
      for (let k = 0; k < 4; k++) {
        const t0 = 30.8 + k * 1.6;
        tl.fromTo("#pk1", { opacity: 1, x: 0 }, { opacity: 1, x: 90, duration: 0.45, ease: "none" }, t0);
        tl.set("#pk1", { opacity: 0 }, t0 + 0.45);
        tl.fromTo("#pk2", { opacity: 1, x: 0 }, { opacity: 1, x: 110, duration: 0.45, ease: "none" }, t0 + 0.5);
        tl.set("#pk2", { opacity: 0 }, t0 + 0.95);
      }

      // ---------------- answers -> actions
      tl.from("#sCmp .kicker", { autoAlpha: 0, y: -20, duration: 0.4 }, 37.3);
      tl.from("#cmpA", { autoAlpha: 0, y: 80, duration: 0.45, ease: "back.out(1.6)" }, 39.6);
      tl.fromTo("#strike", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, 41.3);
      tl.to("#cmpA", { opacity: 0.45, duration: 0.3 }, 41.4);
      tl.from("#arrow", { autoAlpha: 0, x: -40, duration: 0.3 }, 41.5);
      tl.from("#cmpB", { autoAlpha: 0, y: 80, duration: 0.45, ease: "back.out(1.6)" }, 42.45);
      [["#t1", 42.95], ["#t2", 43.45], ["#t3", 43.95]].forEach(([s, t]) =>
        tl.from(s, { autoAlpha: 0, x: 40, duration: 0.3, ease: "power3.out" }, t));

      // ---------------- hook
      tl.from("#hook .l1", { autoAlpha: 0, y: -60, scale: 0.8, duration: 0.45, ease: "back.out(2)" }, 0.65);
      tl.from("#hook .l2", { autoAlpha: 0, scale: 0.3, rotation: -6, duration: 0.45, ease: "back.out(2.6)" }, 1.0);
      tl.to("#hook .l2", { scale: 1.08, duration: 0.2, yoyo: true, repeat: 1 }, 3.9);
      tl.to("#hook", { opacity: 0, y: -80, duration: 0.3, ease: "power2.in" }, 5.2);

      // ---------------- next level
      tl.fromTo("#flash", { opacity: 0 }, { opacity: 0.7, duration: 0.06, yoyo: true, repeat: 1 }, 45.05);
      tl.from("#lvl .t", { autoAlpha: 0, scale: 2.2, filter: "blur(20px)", duration: 0.4, ease: "expo.out" }, 45.05);
      tl.from("#lvl .bar", { autoAlpha: 0, y: 30, duration: 0.3 }, 45.4);
      tl.fromTo("#lvl .fill", { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: "power2.inOut" }, 45.6);
      tl.to("#lvl", { opacity: 0, y: -60, duration: 0.3 }, 47.55);

      // ---------------- CTA
      tl.from("#follow .btn", { autoAlpha: 0, scale: 0.3, duration: 0.45, ease: "back.out(2.4)" }, 50.85);
      tl.set("#tap", { opacity: 0, scale: 0.4 }, 0);
      [51.35, 55.85].forEach(t => {
        tl.fromTo("#tap", { opacity: 0.9, scale: 0.4 }, { opacity: 0, scale: 1.6, duration: 0.5, ease: "power2.out" }, t);
        tl.to("#follow .btn", { scale: 0.9, duration: 0.09, yoyo: true, repeat: 1 }, t);
      });
      tl.to("#follow .btn", { background: "linear-gradient(90deg, #2bd67b, #19b866)", duration: 0.2 }, 56.0);
      tl.from("#promo", { opacity: 0, y: 120, duration: 0.5, ease: "back.out(1.7)" }, 51.8);
      tl.to("#promo", { borderColor: "#ff7a3d", duration: 0.4, yoyo: true, repeat: 5 }, 52.4);
      tl.to(["#follow", "#promo"], { opacity: 0, duration: 0.3 }, 57.35);

      // ---------------- captions: word pop-in, slide out; position depends on layout
      const capY = t => {
        for (const [mode, s, e] of SCENES) if (t >= s && t < e) return mode === "split" ? 985 : (mode === "card" ? 1380 : 1300);
        return 1300;
      };
      tl.set("#capwrap", { y: 1300 }, 0);
      SCENES.forEach(([mode, s]) => tl.to("#capwrap", { y: capY(s), duration: T, ease: "power3.inOut" }, Math.max(0, s - 0.1)));
      CAPS.forEach(([sel, s, e]) => {
        tl.from(sel + " .w", { autoAlpha: 0, y: 30, scale: 0.6, duration: 0.22, ease: "back.out(2.5)", stagger: 0.05 }, s);
        tl.to(sel, { opacity: 0, duration: 0.12 }, e - 0.12);
      });

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
