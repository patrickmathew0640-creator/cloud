"""Generate index.html (HyperFrames composition) and SFX cues for the "3D website from one prompt" edit.

Times are seconds on the source timeline (25.6s, Tamil voice-over). Cards live in the empty wall area
above the speaker's head (y 64-536); her face sits at roughly y 660-1200 and is never covered.
Cards are either screen captures of threeui.com ("hook", "video"; made with capture.mjs) or animated
UI mock-ups ("paste", "comment").

The source is iPhone HLG HDR, so assets/speaker.mp4 is tone-mapped to SDR bt709 first and the render
uses --sdr (see ../edit4/build.py for the exact ffmpeg prep command):
  npx hyperframes@0.8.121 render --sdr -q delivery -f 30 -o renders/silent.mp4
  python3 mix_audio.py renders/silent.mp4 out.mp4   (then re-encode to H.264 for delivery)
"""
import json
import re

DURATION = 25.6

# English subtitles translated from the Tamil voice-over. *word* = highlight.
CAPTIONS = [
    (0.05, 1.42, "With just *one prompt*…"),
    (1.44, 3.56, "want a *super 3D website*?"),
    (3.58, 5.92, "then this website is *heaven* for you"),
    (5.94, 8.24, "it has lots of *free templates*"),
    (8.26, 10.22, "*pick* the design you like"),
    (10.24, 12.44, "and *copy* its prompt"),
    (12.46, 14.52, "Next, go to *Claude AI*"),
    (14.54, 16.02, "and *paste* that prompt"),
    (16.04, 16.92, "*That's it!*"),
    (16.94, 18.40, "build your very own"),
    (18.42, 21.70, "*stunning 3D website*"),
    (21.72, 23.38, "Want the *link* to this website?"),
    (23.40, 25.50, "comment *“3D”* below"),
]

# (id, kind, clip, start, end, kicker, title)
CARDS = [
    ("c0", "hook", "s_hook", 0.20, 3.40, "", ""),
    ("c1", "video", "s_browse", 3.75, 7.95, "THREEUI.COM", "Free 3D website templates"),
    ("c2", "video", "s_pick", 8.20, 10.15, "STEP 1", "Pick a design you like"),
    ("c3", "video", "s_copy", 10.25, 12.40, "STEP 2", "Copy the prompt"),
    ("c4", "paste", "", 12.50, 16.00, "STEP 3", "Paste it into Claude AI"),
    ("c5", "video", "s_result", 16.85, 21.40, "THE RESULT", "Your own stunning 3D website"),
    ("c6", "comment", "", 21.70, DURATION, "WANT THE LINK?", "Comment “3D” below"),
]
COPY_CLICK = 11.70  # the cursor clicks "Copy Prompt" 1.45s into the s_copy capture

# speaker punch-ins on each new beat
BEATS = [3.58, 8.26, 10.24, 12.46, 16.04, 21.72]

SFX = [("whoosh_soft", round(c[3] - 0.05, 2), 0.16) for c in CARDS]
SFX += [("click", COPY_CLICK, 0.35), ("pop", COPY_CLICK + 0.08, 0.08), ("click", 14.95, 0.35), ("click", 15.45, 0.35),
        ("ding", 16.10, 0.10), ("click", 23.95, 0.3), ("click", 24.15, 0.3), ("click", 24.80, 0.35), ("pop", 24.86, 0.08)]

# opening lines of the real prompt threeui.com copies for the Kage template
PROMPT = "# Integrate &lt;KageLandingPage /&gt; from ThreeUI using its exact source. You are working in an existing application. Implement this component…"
CURSOR = '<svg viewBox="0 0 24 24"><path d="M4 2l16 10-7 1.6L9.6 21z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>'
SEND = '<svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def caption_html(i, start, end, text):
    words = []
    for tok in re.split(r"(\*[^*]+\*)", text):
        if not tok:
            continue
        hl = tok.startswith("*")
        for w in tok.strip("*").split():
            words.append(f'<span class="{"w hl" if hl else "w"}">{w}</span>')
    return (f'<div id="cap{i}" class="cap clip" data-start="{start}" data-duration="{round(end - start, 2)}" '
            f'data-track-index="5"><div class="capbox">{" ".join(words)}</div></div>')


def head(kicker, title):
    tw = " ".join(f'<span class="tw">{w}</span>' for w in title.split())
    return f'<div class="kick">{kicker}</div><div class="title">{tw}</div>'


def card_html(cid, kind, clip, start, end, kicker, title):
    dur = round(end - start, 2)
    if kind in ("hook", "video"):
        vid = (f'<div class="frame" data-layout-allow-overflow><video id="{cid}v" class="bv" src="assets/broll/{clip}.mp4" muted playsinline '
               f'data-start="{start}" data-duration="{dur}" data-track-index="3"></video></div><div class="shade"></div>')
        if kind == "hook":
            text = ('<div class="txt hook"><div class="kick">JUST ONE PROMPT</div>'
                    '<div class="big"><span class="acc">3D</span> WEBSITE</div>'
                    '<div class="sub">built for you in minutes</div></div>')
        else:
            text = f'<div class="txt">{head(kicker, title)}</div>'
            if cid == "c3":
                text += '<div class="toast">✓ Prompt copied</div>'
        body = vid + text
    elif kind == "paste":
        body = f'''<div class="ui"><div class="uihead">{head(kicker, title)}</div>
          <div class="chat"><div class="chatname">Claude AI</div>
            <div class="inbox"><div class="ph">How can I help you today?</div><div class="typed">{PROMPT}</div>
              <div class="send">{SEND}</div></div></div>
          <div class="cursor" id="{cid}cur">{CURSOR}</div></div>'''
    else:  # comment
        body = f'''<div class="ui"><div class="uihead">{head(kicker, title)}</div>
          <div class="cmt"><div class="av"></div><div class="cbox"><span class="ph">Add a comment…</span><span class="ctext">3D</span><span class="caret"></span></div>
            <div class="post">Post</div></div>
          <div class="done"><div class="av"></div><div><b>you</b><span>3D</span></div></div>
          <div class="cursor" id="{cid}cur">{CURSOR}</div></div>'''
    return f'''<div id="{cid}" class="card {kind}"><div class="sheen" data-layout-allow-overflow></div>
        {body}
      </div>'''


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
      :root { --accent: #ffd54a; --ink: #101218; --ui: #1a1c26; --ui2: #262938; --line: rgba(255,255,255,.12); --mute: rgba(255,255,255,.55); --clay: #d97757; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Poppins", sans-serif; color: #fff; }

      #spk { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
      #spkv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 48%; }
      #vig { position: absolute; inset: 0; z-index: 2;
             background: radial-gradient(ellipse 80% 62% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.28) 100%),
                         linear-gradient(180deg, rgba(0,0,0,0) 70%, rgba(0,0,0,.22) 100%); }

      /* ---------- cards (top band, clear of the face) ---------- */
      .card { position: absolute; left: 120px; top: 64px; width: 840px; height: 472px; z-index: 3; border-radius: 30px; overflow: hidden;
              box-shadow: 0 22px 60px rgba(0,0,0,.35), 0 0 0 3px rgba(255,255,255,.85); background: var(--ui); }
      .frame { position: absolute; inset: 0; overflow: hidden; border-radius: 30px; }
      .bv { position: absolute; left: 0; top: 0; width: 840px; height: 472px; object-fit: cover; }
      .shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 38%, rgba(0,0,0,.74) 100%); }
      .hook .shade { background: linear-gradient(180deg, rgba(10,10,16,.35), rgba(10,10,16,.68)); }
      .sheen { position: absolute; top: -40px; left: -300px; width: 180px; height: 560px; transform: rotate(18deg); z-index: 4;
               background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.22), rgba(255,255,255,0)); }
      .txt { position: absolute; left: 44px; right: 44px; bottom: 34px; }
      .kick { font-size: 26px; font-weight: 800; letter-spacing: .2em; color: var(--accent); text-shadow: 0 2px 10px rgba(0,0,0,.4); }
      .title { margin-top: 4px; font-size: 54px; line-height: 1.1; font-weight: 800; text-shadow: 0 3px 16px rgba(0,0,0,.45); }
      .tw { display: inline-block; }
      #c5 .title { line-height: 1.18; }
      .txt.hook { bottom: auto; top: 0; height: 472px; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
      .txt.hook .big { font-size: 120px; font-weight: 900; line-height: 1; letter-spacing: .02em; text-shadow: 0 6px 30px rgba(0,0,0,.5); }
      .acc { color: var(--accent); display: inline-block; }
      .txt.hook .sub { margin-top: 14px; font-size: 38px; font-weight: 600; opacity: .95; }

      .toast { position: absolute; right: 40px; top: 96px; padding: 12px 22px; border-radius: 16px; background: #2bd67b; color: #0b2a18;
               font-size: 26px; font-weight: 800; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
      .video .bv { filter: saturate(1.05); }

      /* ---------- UI mock-up cards ---------- */
      .ui { position: absolute; inset: 0; padding: 34px 44px; background: radial-gradient(circle at 85% 0%, #2b2f4a 0%, var(--ui) 60%); }
      .uihead .title { font-size: 46px; text-shadow: none; }
      .cursor { position: absolute; left: 0; top: 0; width: 46px; height: 46px; z-index: 5; filter: drop-shadow(0 4px 8px rgba(0,0,0,.5)); }
      .cursor svg { width: 100%; height: 100%; }
      /* paste */
      .chat { position: absolute; left: 44px; right: 44px; top: 170px; height: 260px; border-radius: 22px; background: #f5f2ec; padding: 20px 24px; color: #2b2a27; }
      .chatname { font-size: 24px; font-weight: 800; color: var(--clay); }
      .inbox { position: absolute; left: 22px; right: 22px; bottom: 20px; height: 150px; border-radius: 18px; background: #fff; border: 2px solid #e4ded3; padding: 16px 90px 16px 20px; }
      .inbox .ph { position: absolute; left: 20px; top: 16px; font-size: 24px; color: #9a958c; }
      .typed { font-size: 22px; line-height: 1.45; color: #2b2a27; clip-path: inset(0 100% 0 0); }
      .send { position: absolute; right: 16px; bottom: 16px; width: 56px; height: 56px; border-radius: 16px; background: var(--clay); display: flex; align-items: center; justify-content: center; }
      .send svg { width: 30px; height: 30px; }
      /* comment */
      .cmt { position: absolute; left: 44px; right: 44px; top: 200px; height: 96px; display: flex; align-items: center; gap: 18px; }
      .av { width: 64px; height: 64px; flex: none; border-radius: 50%; background: linear-gradient(135deg, #ffd54a, #ff7a59); }
      .cbox { flex: 1; height: 72px; border-radius: 36px; background: var(--ui2); border: 2px solid var(--line); display: flex; align-items: center; padding: 0 26px; position: relative; font-size: 30px; }
      .cbox .ph { position: absolute; left: 26px; color: var(--mute); }
      .cbox .ctext { font-weight: 800; opacity: 0; }
      .caret { width: 3px; height: 34px; background: var(--accent); margin-left: 4px; }
      .post { height: 64px; padding: 0 26px; border-radius: 32px; background: var(--accent); color: var(--ink); font-size: 26px; font-weight: 800; display: flex; align-items: center; }
      .done { position: absolute; left: 44px; top: 320px; display: flex; align-items: center; gap: 18px; padding: 14px 26px 14px 14px; border-radius: 22px; background: rgba(255,255,255,.08); }
      .done .av { width: 54px; height: 54px; }
      .done b { display: block; font-size: 20px; color: var(--mute); font-weight: 700; }
      .done span { font-size: 32px; font-weight: 800; }

      /* ---------- subtitles (chest area, below the chin) ---------- */
      .cap { position: absolute; left: 70px; right: 70px; top: 1450px; z-index: 5; display: flex; justify-content: center; }
      .capbox { max-width: 900px; padding: 14px 30px 16px; border-radius: 22px; background: rgba(10,10,14,.58); text-align: center;
                font-size: 46px; line-height: 1.25; font-weight: 800; }
      .w { display: inline-block; }
      .w.hl { color: var(--accent); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{D}}" data-width="1080" data-height="1920">
      <div id="spk" data-layout-allow-overflow>
        <video id="spkv" src="assets/speaker.mp4" muted playsinline data-start="0" data-duration="{{D}}" data-track-index="0"></video>
      </div>
      <div id="vig" class="clip" data-start="0" data-duration="{{D}}" data-track-index="1"></div>

      {{CARDS}}

      {{CAPTIONS}}
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const D = {{D}};
      const CAPS = {{CAPS_JS}}, CARDS = {{CARDS_JS}}, BEATS = {{BEATS_JS}};

      // ---------- speaker: slow drift with a gentle punch-in on every beat
      tl.set("#spkv", { scale: 1 }, 0);
      tl.to("#spkv", { scale: 1.04, duration: BEATS[0], ease: "none" }, 0);
      BEATS.forEach((b, i) => {
        const e = i < BEATS.length - 1 ? BEATS[i + 1] : D;
        const hi = i % 2 ? 1.07 : 1.09, lo = i % 2 ? 1.03 : 1.05;
        tl.to("#spkv", { scale: hi, duration: 0.5, ease: "power2.out" }, b);
        tl.to("#spkv", { scale: lo, duration: e - b - 0.5, ease: "none" }, b + 0.5);
      });

      // ---------- cards (wrappers are untimed; only the videos carry data-start)
      tl.set(".card", { autoAlpha: 0 }, 0);
      CARDS.forEach(([id, s, e, kind]) => {
        const c = "#" + id;
        tl.fromTo(c, { autoAlpha: 0, y: -26, scale: 0.94, filter: "blur(10px)" },
                     { autoAlpha: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }, s);
        if (kind === "video" || kind === "hook") tl.fromTo(c + "v", { scale: kind === "hook" ? 1.12 : 1.05 }, { scale: 1.0, duration: e - s, ease: "none" }, s);
        tl.fromTo(c + " .sheen", { x: 0 }, { x: 1400, duration: 0.9, ease: "power2.inOut" }, s + 0.35);
        if (e < D) tl.to(c, { autoAlpha: 0, y: -18, scale: 0.97, filter: "blur(6px)", duration: 0.35, ease: "power2.in" }, e - 0.35);
        else tl.to(c, { autoAlpha: 0, duration: 0.3, ease: "power2.in" }, D - 0.3);
        if (kind !== "hook") {
          tl.from(c + " .kick", { autoAlpha: 0, x: -24, duration: 0.4, ease: "power3.out" }, s + 0.3);
          tl.from(c + " .tw", { autoAlpha: 0, y: 26, duration: 0.42, ease: "power3.out", stagger: 0.06 }, s + 0.4);
        }
      });
      // hook
      tl.from("#c0 .big", { autoAlpha: 0, scale: 0.86, duration: 0.55, ease: "power3.out" }, 0.45);
      tl.from("#c0 .sub", { autoAlpha: 0, y: 18, duration: 0.45, ease: "power3.out" }, 0.95);
      tl.fromTo("#c0 .acc", { scale: 1 }, { scale: 1.18, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out" }, 1.98);

      // copy step: toast pops when the captured cursor clicks "Copy Prompt"
      tl.fromTo("#c3 .toast", { autoAlpha: 0, y: -12, scale: 0.9 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }, {{COPY_CLICK}} + 0.05);

      // paste mock: chat box appears, prompt pastes in, cursor hits send
      tl.from("#c4 .chat", { autoAlpha: 0, y: 30, duration: 0.45, ease: "power3.out" }, 12.8);
      tl.to("#c4 .ph", { opacity: 0, duration: 0.1 }, 14.95);
      tl.fromTo("#c4 .typed", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.35, ease: "power2.out" }, 14.97);
      tl.fromTo("#c4cur", { x: 380, y: 470, autoAlpha: 0 }, { x: 742, y: 378, autoAlpha: 1, duration: 0.6, ease: "power2.inOut" }, 14.7);
      tl.to("#c4cur", { scale: 0.82, duration: 0.08, yoyo: true, repeat: 1 }, 15.45);
      tl.to("#c4 .send", { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1 }, 15.45);

      // comment mock: "3D" typed, posted
      tl.from("#c6 .cmt", { autoAlpha: 0, y: 30, duration: 0.45, ease: "power3.out" }, 22.0);
      tl.fromTo("#c6 .caret", { opacity: 1 }, { opacity: 0, duration: 0.3, repeat: 5, yoyo: true, ease: "none" }, 22.3);
      tl.to("#c6 .cbox .ph", { opacity: 0, duration: 0.1 }, 23.9);
      tl.to("#c6 .ctext", { opacity: 1, duration: 0.05 }, 23.95);
      tl.fromTo("#c6cur", { x: 500, y: 470, autoAlpha: 0 }, { x: 735, y: 262, autoAlpha: 1, duration: 0.6, ease: "power2.inOut" }, 24.1);
      tl.to("#c6cur", { scale: 0.82, duration: 0.08, yoyo: true, repeat: 1 }, 24.8);
      tl.to("#c6 .post", { scale: 0.9, duration: 0.08, yoyo: true, repeat: 1 }, 24.8);
      tl.to("#c6 .cbox .ctext", { opacity: 0, duration: 0.1 }, 24.9);
      tl.fromTo("#c6 .done", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: "back.out(1.8)" }, 24.9);

      // ---------- subtitles: words rise in softly
      CAPS.forEach(([sel, s, e]) => {
        tl.from(sel + " .capbox", { autoAlpha: 0, y: 14, duration: 0.18, ease: "power2.out" }, s);
        tl.from(sel + " .w", { autoAlpha: 0, y: 12, duration: 0.22, ease: "power2.out", stagger: 0.04 }, s);
        tl.to(sel, { opacity: 0, duration: 0.1 }, e - 0.1);
      });

      tl.set({}, {}, D);
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def build():
    caps = "\n      ".join(caption_html(i, *c) for i, c in enumerate(CAPTIONS))
    cards = "\n      ".join(card_html(*c) for c in CARDS)
    html = (TEMPLATE.replace("{{CAPTIONS}}", caps).replace("{{CARDS}}", cards)
            .replace("{{CAPS_JS}}", json.dumps([[f"#cap{i}", s, e] for i, (s, e, _) in enumerate(CAPTIONS)]))
            .replace("{{CARDS_JS}}", json.dumps([[c[0], c[3], c[4], c[1]] for c in CARDS]))
            .replace("{{BEATS_JS}}", json.dumps(BEATS))
            .replace("{{COPY_CLICK}}", str(COPY_CLICK)).replace("{{D}}", str(DURATION)))
    open("index.html", "w").write(html)
    json.dump(sorted(SFX, key=lambda c: c[1]), open("sfx_cues.json", "w"), indent=1)
    print(f"index.html: {len(CAPTIONS)} captions, {len(CARDS)} cards; {len(SFX)} sfx cues")


if __name__ == "__main__":
    build()
