"""Render every on-screen graphic as a transparent 1920x1080 PNG with headless Chromium.

Styling copies the reference edit: Segoe-style bold type (Selawik, metric-compatible with Segoe UI),
yellow #FFC20E tags, white callout cards with a yellow edge bar, dark translucent subtitle box.
"""
import html
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE / "fonts").as_uri()
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

BASE_CSS = f"""
@font-face {{ font-family: S; font-weight: 400; src: url('{FONTS}/selawk.ttf'); }}
@font-face {{ font-family: S; font-weight: 600; src: url('{FONTS}/selawksb.ttf'); }}
@font-face {{ font-family: S; font-weight: 700; src: url('{FONTS}/selawkb.ttf'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; background: transparent; overflow: hidden;
             font-family: S, sans-serif; }}
.emo {{ font-family: 'Noto Color Emoji'; font-weight: 400; }}
.ar {{ font-family: 'DejaVu Sans'; font-weight: 700; font-size: .8em; padding: 0 .08em; }}
.tag {{ display: inline-block; background: #FFC20E; color: #111; font-weight: 700; border-radius: 9px; }}
.shadow {{ text-shadow: 0 3px 10px rgba(0,0,0,.55), 0 1px 2px rgba(0,0,0,.6); }}

/* subtitle */
.sub {{ position: absolute; left: 50%; bottom: 52px; transform: translateX(-50%); max-width: 1300px; width: max-content;
        background: rgba(20,14,14,.62); color: #fff; font-weight: 600; font-size: 47px; line-height: 62px;
        padding: 4px 16px 6px; text-align: center; }}

/* opening title */
.title {{ position: absolute; left: 110px; top: 350px; }}
.title .tag {{ font-size: 34px; padding: 4px 26px 6px; }}
.title h1 {{ color: #fff; font-weight: 700; font-size: 80px; line-height: 98px; margin-top: 30px; }}

/* lower-left info card */
.info {{ position: absolute; left: 90px; top: 610px; border-left: 10px solid #FFC20E; }}
.info .a {{ background: #fff; color: #111; font-weight: 700; font-size: 48px; line-height: 90px; padding: 0 36px 0 26px; display: table; }}
.info .b {{ background: #111; color: #fff; font-weight: 600; font-size: 30px; line-height: 60px; padding: 0 36px 0 26px; display: table; }}

/* section title */
.sect {{ position: absolute; left: 110px; top: 380px; }}
.sect .tag {{ font-size: 36px; line-height: 65px; padding: 0 24px; border-radius: 12px; }}
.sect h2 {{ color: #fff; font-weight: 700; font-size: 88px; line-height: 100px; margin-top: 10px; }}

/* top-right callout */
.call {{ position: absolute; right: 70px; top: 116px; }}
.call .k {{ position: absolute; left: 14px; top: -20px; background: #111; color: #FFC20E; font-weight: 700; font-size: 25px;
            padding: 2px 16px 4px; border-radius: 999px; letter-spacing: .02em; z-index: 2; }}
.call .box {{ display: flex; align-items: center; gap: 18px; background: #fff; border-radius: 18px; border-left: 10px solid #FFC20E;
              height: 114px; padding: 0 32px 0 30px; box-shadow: 0 6px 18px rgba(0,0,0,.28); }}
.call .box .emo {{ font-size: 46px; margin-top: -14px; }}
.call .box .t {{ font-weight: 700; font-size: 52px; color: #111; white-space: nowrap; }}

/* subscribe */
.subs {{ position: absolute; right: 90px; top: 76px; display: flex; align-items: center; gap: 18px; }}
.subs .like {{ width: 132px; height: 88px; border-radius: 999px; background: #fff; display: flex; justify-content: center;
               align-items: flex-start; padding-top: 6px; font-size: 40px; box-shadow: 0 6px 16px rgba(0,0,0,.3); }}
.subs .btn {{ height: 88px; padding: 0 42px; border-radius: 999px; background: #E8120C; color: #fff; font-weight: 700; font-size: 38px;
              display: flex; align-items: center; box-shadow: 0 6px 16px rgba(0,0,0,.3); }}
.subs .btn.done {{ background: #5a5a5a; }}
.subs .bell {{ font-size: 42px; margin-left: 12px; margin-top: -40px; }}
.cursor {{ position: absolute; right: 18px; top: 190px; font-size: 56px; transform: rotate(-20deg); }}

/* end card text */
.end {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.end h1 {{ color: #fff; font-weight: 700; font-size: 92px; }}
.end p {{ color: #FFC20E; font-weight: 600; font-size: 40px; margin-top: 10px; }}
"""


def esc(s):
    return html.escape(s)


def sub_html(text):
    return f'<div class="sub">{esc(text)}</div>'


def title_html(tag, l1, l2):
    return f'<div class="title"><span class="tag">{esc(tag)}</span><h1 class="shadow">{esc(l1)}<br>{esc(l2)}</h1></div>'


def info_html(a, b):
    return f'<div class="info"><div class="a">{esc(a)}</div><div class="b">{esc(b)}</div></div>'


def sect_html(tag, name):
    return f'<div class="sect"><span class="tag">{esc(tag)}</span><h2 class="shadow">{esc(name)}</h2></div>'


def call_html(kicker, emoji, text):
    return (f'<div class="call"><div class="k">{esc(kicker)}</div><div class="box"><span class="emo">{emoji}</span>'
            f'<span class="t">{esc(text).replace("→", "<span class=ar>→</span>")}</span></div></div>')


def subs_html(done, cursor):
    btn = '<div class="btn done">SUBSCRIBED</div>' if done else '<div class="btn">SUBSCRIBE</div>'
    cur = '<div class="cursor emo">👆</div>' if cursor else ''
    return f'<div class="subs"><div class="like emo">👍</div>{btn}<div class="bell emo">🔔</div></div>{cur}'


def end_html(h, p):
    return f'<div class="end"><h1 class="shadow">{esc(h)}</h1><p class="shadow">{esc(p)}</p></div>'


def render(jobs, outdir, scale=1):
    """jobs: list of (filename, inner_html)."""
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
        for name, inner in jobs:
            tmp = HERE / "_render.html"
            tmp.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head>"
                           f"<body>{inner}</body></html>")
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=os.path.join(outdir, name), omit_background=True)
        b.close()
    (HERE / "_render.html").unlink(missing_ok=True)
