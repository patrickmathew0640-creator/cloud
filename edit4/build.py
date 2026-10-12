"""Generate index.html (HyperFrames composition) and SFX cues for the "6 communication books" edit.

Times are seconds on the source timeline (39.83s, Tamil voice-over). B-roll cards live in the empty
wall area above the speaker's head (y 64-536); her face sits at roughly y 675-1230 and is never covered.
"""
import json
import re

DURATION = 39.8

# English subtitles translated from the Tamil voice-over. *word* = highlight.
CAPTIONS = [
    (0.05, 1.50, "To build your *communication skills*"),
    (1.50, 3.40, "here are *6 books* to read"),
    (3.42, 5.26, "First — *Talk Like TED*"),
    (5.28, 7.20, "learn to speak with *confidence*"),
    (7.22, 10.04, "Second — *Never Split the Difference*"),
    (10.06, 12.52, "sharpen your *negotiation skills*"),
    (12.54, 15.04, "Third — *Just Listen*"),
    (15.06, 17.02, "truly *understand* other people"),
    (17.04, 20.22, "Fourth — *The Charisma Myth*"),
    (20.24, 22.26, "*polish* your personality"),
    (22.28, 25.22, "Fifth — *How to Win Friends* & Influence People"),
    (25.24, 28.28, "build *great relationships* with people"),
    (28.30, 30.66, "Sixth — *How to Talk to Anyone*"),
    (30.68, 32.62, "speak to anyone *fearlessly*"),
    (32.64, 35.52, "*Save* these 6 books"),
    (35.54, 38.90, "and take your communication to the *next level*"),
]

# (id, clip, start, end, kicker, title) - card on screen from start to end
CARDS = [
    ("c0", "b0_books", 0.20, 3.30, "", ""),
    ("c1", "b1_ted", 3.55, 7.10, "BOOK 01", "Talk Like TED"),
    ("c2", "b2_handshake", 7.80, 12.40, "BOOK 02", "Never Split the Difference"),
    ("c3", "b3_listen", 13.30, 16.90, "BOOK 03", "Just Listen"),
    ("c4", "b4_charisma", 18.20, 22.00, "BOOK 04", "The Charisma Myth"),
    ("c5", "b5_friends", 22.70, 28.10, "BOOK 05", "How to Win Friends &amp; Influence People"),
    ("c6", "b6_talk", 28.75, 32.50, "BOOK 06", "How to Talk to Anyone"),
    ("c7", "b7_read", 32.80, 36.30, "", ""),
]
RECAP = (36.45, DURATION)
BOOKS = [c[5] for c in CARDS[1:7]]

# speaker punch-ins on each "first / second / ..." beat
BEATS = [3.42, 7.22, 12.54, 17.04, 22.28, 28.30, 32.64]

SFX = [("whoosh_soft", round(s - 0.05, 2), 0.16) for _, _, s, *_ in CARDS[1:]]
SFX += [("whoosh_soft", 0.15, 0.14), ("ding", 33.45, 0.10), ("whoosh_soft", RECAP[0] - 0.05, 0.16)]
SFX += [("pop", round(RECAP[0] + 0.35 + i * 0.12, 2), 0.06) for i in range(6)]


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


BOOKMARK = '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.5L6 21z" fill="#ffd54a"/></svg>'


def card_html(cid, clip, start, end, kicker, title):
    dur = round(end - start, 2)
    if cid == "c0":
        text = ('<div class="txt hook"><div class="kick">COMMUNICATION SKILLS</div>'
                '<div class="big"><span class="six">6</span> BOOKS</div>'
                '<div class="sub">that will change how you speak</div></div>')
    elif cid == "c7":
        text = f'<div class="txt save"><div class="savepill">{BOOKMARK}<span>SAVE THIS LIST</span></div></div>'
    else:
        tw = " ".join(f'<span class="tw">{w}</span>' for w in title.split())
        text = f'<div class="txt"><div class="kick">{kicker} <em>/ 06</em></div><div class="title">{tw}</div></div>'
    return f'''<div id="{cid}" class="card">
        <div class="frame" data-layout-allow-overflow><video id="{cid}v" class="bv" src="assets/broll/{clip}.mp4" muted playsinline data-start="{start}" data-duration="{dur}" data-track-index="3"></video></div>
        <div class="shade"></div><div class="sheen" data-layout-allow-overflow></div>
        {text}
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
      :root { --accent: #ffd54a; --ink: #101218; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Poppins", sans-serif; color: #fff; }

      #spk { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
      #spkv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 49%; }
      #vig { position: absolute; inset: 0; z-index: 2;
             background: radial-gradient(ellipse 80% 62% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.28) 100%),
                         linear-gradient(180deg, rgba(0,0,0,0) 70%, rgba(0,0,0,.22) 100%); }

      /* ---------- b-roll cards (top band, clear of the face) ---------- */
      .card { position: absolute; left: 120px; top: 64px; width: 840px; height: 472px; z-index: 3; border-radius: 30px;
              box-shadow: 0 22px 60px rgba(0,0,0,.35), 0 0 0 3px rgba(255,255,255,.85); overflow: hidden; }
      .frame { position: absolute; inset: 0; overflow: hidden; border-radius: 30px; }
      .bv { position: absolute; left: 0; top: 0; width: 840px; height: 472px; object-fit: cover; }
      .shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 38%, rgba(0,0,0,.72) 100%); }
      #c0 .shade { background: linear-gradient(180deg, rgba(10,10,16,.30), rgba(10,10,16,.70)); }
      #c7 .shade { background: linear-gradient(180deg, rgba(0,0,0,0) 50%, rgba(0,0,0,.55) 100%); }
      .sheen { position: absolute; top: -40px; left: -300px; width: 180px; height: 560px; transform: rotate(18deg);
               background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.28), rgba(255,255,255,0)); }
      .txt { position: absolute; left: 44px; right: 44px; bottom: 34px; }
      .kick { font-size: 26px; font-weight: 800; letter-spacing: .2em; color: var(--accent); text-shadow: 0 2px 10px rgba(0,0,0,.4); }
      .kick em { font-style: normal; color: rgba(255,255,255,.7); }
      .title { margin-top: 4px; font-size: 56px; line-height: 1.08; font-weight: 800; text-shadow: 0 3px 16px rgba(0,0,0,.45); }
      .tw { display: inline-block; }
      #c5 .title { font-size: 48px; line-height: 1.18; }
      .hook { bottom: auto; top: 0; height: 472px; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
      .hook .big { font-size: 128px; font-weight: 900; line-height: 1; letter-spacing: .02em; text-shadow: 0 6px 30px rgba(0,0,0,.45); }
      .hook .six { color: var(--accent); display: inline-block; }
      .hook .sub { margin-top: 14px; font-size: 38px; font-weight: 600; opacity: .95; }
      .save { display: flex; justify-content: center; }
      .savepill { display: flex; align-items: center; gap: 14px; padding: 16px 34px; border-radius: 60px; background: rgba(16,18,24,.78);
                  font-size: 36px; font-weight: 800; letter-spacing: .08em; }
      .savepill svg { width: 40px; height: 40px; }

      /* ---------- recap list ---------- */
      #recap { position: absolute; left: 120px; top: 64px; width: 840px; height: 472px; z-index: 3; border-radius: 30px; padding: 34px 48px;
               background: linear-gradient(160deg, rgba(22,24,34,.94), rgba(14,15,22,.94)); box-shadow: 0 22px 60px rgba(0,0,0,.35), 0 0 0 3px rgba(255,255,255,.85); }
      #recap .rk { font-size: 24px; font-weight: 800; letter-spacing: .2em; color: var(--accent); margin-bottom: 10px; }
      .ri { display: flex; align-items: center; gap: 20px; height: 62px; font-size: 32px; font-weight: 700; white-space: nowrap; }
      .ri b { width: 46px; height: 46px; flex: none; border-radius: 14px; display: flex; align-items: center; justify-content: center;
              background: var(--accent); color: var(--ink); font-size: 24px; font-weight: 900; }

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

      <div id="recap">
        <div class="rk">YOUR READING LIST</div>
        {{RECAP}}
      </div>

      {{CAPTIONS}}
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const D = {{D}};
      const CAPS = {{CAPS_JS}}, CARDS = {{CARDS_JS}}, BEATS = {{BEATS_JS}}, RS = {{RS}};

      // ---------- speaker: slow drift with a gentle punch-in on every new book
      tl.set("#spkv", { scale: 1 }, 0);
      tl.to("#spkv", { scale: 1.04, duration: BEATS[0], ease: "none" }, 0);
      BEATS.forEach((b, i) => {
        const e = i < BEATS.length - 1 ? BEATS[i + 1] : D;
        const hi = i % 2 ? 1.07 : 1.09, lo = i % 2 ? 1.03 : 1.04;
        tl.to("#spkv", { scale: hi, duration: 0.5, ease: "power2.out" }, b);
        tl.to("#spkv", { scale: lo, duration: e - b - 0.5, ease: "none" }, b + 0.5);
      });

      // ---------- b-roll cards (wrappers are untimed; only the videos carry data-start)
      tl.set([".card", "#recap"], { autoAlpha: 0 }, 0);
      CARDS.forEach(([id, s, e]) => {
        const c = "#" + id;
        tl.fromTo(c, { autoAlpha: 0, y: -26, scale: 0.94, filter: "blur(10px)" },
                     { autoAlpha: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }, s);
        tl.fromTo(c + "v", { scale: 1.12 }, { scale: 1.0, duration: e - s, ease: "none" }, s);
        tl.fromTo(c + " .sheen", { x: 0 }, { x: 1400, duration: 0.9, ease: "power2.inOut" }, s + 0.35);
        tl.to(c, { autoAlpha: 0, y: -18, scale: 0.97, filter: "blur(6px)", duration: 0.35, ease: "power2.in" }, e - 0.35);
        tl.from(c + " .kick", { autoAlpha: 0, x: -24, duration: 0.4, ease: "power3.out" }, s + 0.3);
        tl.from(c + " .tw", { autoAlpha: 0, y: 26, duration: 0.42, ease: "power3.out", stagger: 0.06 }, s + 0.4);
      });
      // hook card details
      tl.from("#c0 .big", { autoAlpha: 0, scale: 0.86, duration: 0.55, ease: "power3.out" }, 0.45);
      tl.from("#c0 .sub", { autoAlpha: 0, y: 18, duration: 0.45, ease: "power3.out" }, 0.9);
      tl.fromTo("#c0 .six", { scale: 1 }, { scale: 1.18, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out" }, 2.28);
      // save card
      tl.from("#c7 .savepill", { autoAlpha: 0, y: 24, scale: 0.9, duration: 0.45, ease: "back.out(1.8)" }, 33.35);

      // ---------- recap list
      tl.fromTo("#recap", { autoAlpha: 0, y: -26, scale: 0.94, filter: "blur(10px)" },
                          { autoAlpha: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }, RS);
      tl.from("#recap .rk", { autoAlpha: 0, x: -20, duration: 0.35, ease: "power3.out" }, RS + 0.2);
      tl.from("#recap .ri", { autoAlpha: 0, x: -30, duration: 0.4, ease: "power3.out", stagger: 0.12 }, RS + 0.35);
      tl.to("#recap", { autoAlpha: 0, duration: 0.4, ease: "power2.in" }, D - 0.45);

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
    recap = "\n        ".join(f'<div class="ri"><b>{i + 1}</b><span>{t}</span></div>' for i, t in enumerate(BOOKS))
    html = (TEMPLATE.replace("{{CAPTIONS}}", caps).replace("{{CARDS}}", cards).replace("{{RECAP}}", recap)
            .replace("{{CAPS_JS}}", json.dumps([[f"#cap{i}", s, e] for i, (s, e, _) in enumerate(CAPTIONS)]))
            .replace("{{CARDS_JS}}", json.dumps([[c[0], c[2], c[3]] for c in CARDS]))
            .replace("{{BEATS_JS}}", json.dumps(BEATS))
            .replace("{{RS}}", str(RECAP[0]))
            .replace("{{D}}", str(DURATION)))
    open("index.html", "w").write(html)
    json.dump(sorted(SFX, key=lambda c: c[1]), open("sfx_cues.json", "w"), indent=1)
    print(f"index.html: {len(CAPTIONS)} captions, {len(CARDS)} cards; {len(SFX)} sfx cues")


if __name__ == "__main__":
    build()
