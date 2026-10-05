"""Cut, zoom, caption and mix the talking-head video in the style of the reference edit.

Usage: python3 render.py <raw.mp4> <out.mp4> [--work DIR]

Pipeline
  1. base:    crop the letterboxed 2160x992 picture out of the 2160x3840 source -> 1920x1080 @30fps
  2. cut:     keep EDIT segments (pauses/flubs removed), alternate wide / punch-in framing per segment
  3. overlay: captions + title / info card / section titles / callouts / subscribe / end card
  4. audio:   cleaned voice + soft ducked music bed
All times in edit.py are on the SOURCE timeline; they are remapped onto the cut timeline here.
"""
import argparse
import os
import subprocess

from PIL import Image

import edit
import graphics as g

S = int(os.environ.get("RENDER_SCALE", "1"))   # 1 = 1080p, 2 = 4K (3840x2160)
W, H, FPS = 1920 * S, 1080 * S, 30
CROP = "crop=1764:992:198:1424"          # 16:9 window inside the letterboxed picture
MUSIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "edit2", "audio", edit.MUSIC)


def run(args):
    print("+", " ".join(a if len(a) < 90 else a[:90] + "…" for a in args[:14]), flush=True)
    subprocess.run(args, check=True)


# ------------------------------------------------------------------ timeline mapping
def build_map():
    out, t = [], 0.0
    for s, e, z in edit.SEGMENTS:
        out.append((s, e, t, z))
        t += round((e - s) * FPS) / FPS
    return out, t


SEGMAP, _ = build_map()
CUT_DUR = sum(round((e - s) * FPS) for s, e, _, _ in SEGMAP) / FPS   # frame-exact
TOTAL = CUT_DUR + edit.END_CARD


def remap(ts):
    """Source time -> cut time (snaps into the next kept segment if ts falls in a removed gap)."""
    for s, e, o, _ in SEGMAP:
        if ts < s:
            return o
        if ts <= e:
            return o + ts - s
    return CUT_DUR


# ------------------------------------------------------------------ graphics
def autocrop(path):
    im = Image.open(path)
    box = im.getbbox() or (0, 0, 2, 2)
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0 - 4) & ~1, max(0, y0 - 4) & ~1
    x1, y1 = min(W, x1 + 4), min(H, y1 + 4)
    im.crop((x0, y0, x1, y1)).save(path)
    return x0, y0, x1 - x0, y1 - y0


def make_overlays(work):
    """Return list of overlay dicts: file, x, y, w, t0, t1, anim."""
    gdir = os.path.join(work, "gfx")
    jobs, items = [], []

    def add(name, inner, t0, t1, anim):
        jobs.append((name, inner))
        items.append({"file": os.path.join(gdir, name), "t0": t0, "t1": t1, "anim": anim})

    caps = [[remap(s), remap(e), text] for s, e, text in edit.CAPTIONS]
    for a, b in zip(caps, caps[1:]):        # hold a subtitle across short gaps, as the reference does
        if b[0] - a[1] < 1.5:
            a[1] = b[0]
    for i, (s, e, text) in enumerate(caps):
        add(f"cap{i:03d}.png", g.sub_html(text), s, e, "cut")
    tag, l1, l2, s, e = edit.TITLE
    add("title.png", g.title_html(tag, l1, l2), remap(s), remap(e), "left")
    for i, (a, b, s, e) in enumerate(edit.INFO):
        add(f"info{i}.png", g.info_html(a, b), remap(s), remap(e), "left")
    for i, (tag, name, s, e) in enumerate(edit.SECTIONS):
        add(f"sect{i}.png", g.sect_html(tag, name), remap(s), remap(e), "left")
    for i, (k, emo, text, s, e) in enumerate(edit.CALLOUTS):
        add(f"call{i}.png", g.call_html(k, emo, text), remap(s), remap(e), "right")
    for j, t in enumerate(edit.SUBSCRIBE):
        s = remap(t)
        add(f"subs{j}a.png", g.subs_html(False, False), s, s + 1.3, "pop_in")
        add(f"subs{j}b.png", g.subs_html(False, True), s + 1.3, s + 2.0, "cut")
        add(f"subs{j}c.png", g.subs_html(True, True), s + 2.0, s + 2.9, "cut")
        add(f"subs{j}d.png", g.subs_html(True, False), s + 2.9, s + 4.6, "fade_out")
    h, p = edit.END_TEXT
    add("end.png", g.end_html(h, p), CUT_DUR + 0.15, TOTAL, "fade_in")

    g.render(jobs, gdir, scale=S)
    for it in items:
        it["x"], it["y"], it["w"], it["h"] = autocrop(it["file"])
    return items


# ------------------------------------------------------------------ passes
def make_base(raw, work):
    base = os.path.join(work, "base.mp4" if S == 1 else f"base_x{S}.mp4")
    if not os.path.exists(base):
        run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-vf",
             f"{CROP},scale={W}:{H}:flags=lanczos,fps={FPS},format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-c:a", "copy", base + ".tmp.mp4"])
        os.rename(base + ".tmp.mp4", base)
    return base


def make_cut(base, work):
    """Encode each kept segment with its framing + grade, concat them, then append the blurred end card."""
    out = os.path.join(work, "cut.mp4")
    sdir = os.path.join(work, "segs")
    os.makedirs(sdir, exist_ok=True)
    lst = []
    for i, (s, e, o, z) in enumerate(SEGMAP):
        if z == 1.0:
            fr = edit.GRADE
        else:
            cw, ch = round(W / z / 2) * 2, round(H / z / 2) * 2
            cx, cy = edit.ZOOM_CENTER[0] * S, edit.ZOOM_CENTER[1] * S
            x = min(max(0, round(cx - cw / 2)), W - cw)
            y = min(max(0, round(cy - ch / 2)), H - ch)
            fr = f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,{edit.GRADE}"
        seg = os.path.join(sdir, f"s{i:03d}.mkv")
        n = round((e - s) * FPS)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", base, "-t", f"{e - s:.3f}",
             "-vf", f"{fr},setsar=1,format=yuv420p", "-frames:v", str(n),
             "-af", f"aresample=48000,afade=t=in:d=0.012,afade=t=out:st={e - s - 0.012:.3f}:d=0.012,"
                    f"apad,atrim=0:{n / FPS:.4f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-c:a", "pcm_s16le", "-ac", "2", seg])
        lst.append(f"file '{os.path.abspath(seg)}'")
    open(os.path.join(sdir, "list.txt"), "w").write("\n".join(lst) + "\n")
    joined = os.path.join(work, "joined.mkv")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(sdir, "list.txt"),
         "-c", "copy", joined])
    # end card: last frame frozen, blurred and darkened
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-filter_complex",
         f"[0:v]split[a][b];[b]trim=start={CUT_DUR - 2 / FPS:.3f},setpts=PTS-STARTPTS,"
         f"tpad=stop_mode=clone:stop_duration={edit.END_CARD + 1},trim=0:{edit.END_CARD},setpts=PTS-STARTPTS,"
         f"gblur=sigma={28 * S},eq=brightness=-0.16:saturation=0.8,fade=t=in:d=0.35[e];"
         f"[a]trim=0:{CUT_DUR:.4f},setpts=PTS-STARTPTS[a2];[a2][e]concat=n=2:v=1:a=0,format=yuv420p[v];"
         f"[0:a]apad=whole_dur={TOTAL:.4f}[au]",
         "-map", "[v]", "-map", "[au]", "-r", str(FPS), "-c:v", "libx264", "-preset", "fast", "-crf", "12",
         "-c:a", "pcm_s16le", out])
    return out


def anim_expr(it):
    """Overlay x/y expressions and per-input alpha filter for an overlay's entrance/exit."""
    t0, t1 = it["t0"], it["t1"]
    d = t1 - t0
    x, y, a = str(it["x"]), str(it["y"]), []
    A = 0.4
    if it["anim"] == "left":
        x = f"{it['x']}-{90 * S}*pow(max(0,1-(t-{t0:.3f})/{A}),3)"
        a = [f"fade=t=in:st=0:d={A}:alpha=1", f"fade=t=out:st={max(0, d - 0.35):.3f}:d=0.35:alpha=1"]
    elif it["anim"] == "right":
        x = f"{it['x']}+{160 * S}*pow(max(0,1-(t-{t0:.3f})/{A}),3)"
        a = [f"fade=t=in:st=0:d={A}:alpha=1", f"fade=t=out:st={max(0, d - 0.35):.3f}:d=0.35:alpha=1"]
    elif it["anim"] == "pop_in":
        y = f"{it['y']}-{40 * S}*pow(max(0,1-(t-{t0:.3f})/0.3),3)"
        a = ["fade=t=in:st=0:d=0.3:alpha=1"]
    elif it["anim"] == "fade_out":
        a = [f"fade=t=out:st={max(0, d - 0.4):.3f}:d=0.4:alpha=1"]
    elif it["anim"] == "fade_in":
        a = ["fade=t=in:st=0:d=0.6:alpha=1"]
    return x, y, a


def make_overlay_pass(cut, items, work):
    out = os.path.join(work, "video.mp4")
    args = ["ffmpeg", "-v", "error", "-y", "-i", cut]
    fc, last = [], "0:v"
    for i, it in enumerate(items, start=1):
        d = it["t1"] - it["t0"]
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", it["file"]]
        x, y, alpha = anim_expr(it)
        chain = ",".join(["format=rgba"] + alpha + [f"setpts=PTS-STARTPTS+{it['t0']:.3f}/TB"])
        fc.append(f"[{i}:v]{chain}[g{i}]")
        fc.append(f"[{last}][g{i}]overlay=x='{x}':y='{y}':eof_action=pass:format=auto[o{i}]")
        last = f"o{i}"
    fc.append(f"[{last}]format=yuv420p[v]")
    script = os.path.join(work, "overlay.fc")
    open(script, "w").write(";\n".join(fc))
    args += ["-filter_complex_script", script, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium",
             "-crf", "16", "-c:a", "copy", out]
    run(args)
    return out


def make_audio(cut, work):
    voice = os.path.join(work, "voice.wav")
    mix = os.path.join(work, "mix.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vn", "-af",
         "highpass=f=80,afftdn=nf=-30,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=1.5,"
         "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2,loudnorm=I=-16:TP=-2:LRA=8,aresample=48000,"
         f"apad=whole_dur={TOTAL:.4f},atrim=0:{TOTAL:.4f}",
         "-ac", "2", voice])
    run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-stream_loop", "-1", "-i", MUSIC, "-filter_complex",
         f"[1:a]atrim=0:{TOTAL:.3f},asetpts=PTS-STARTPTS,aresample=48000,volume={edit.MUSIC_VOL},"
         f"afade=t=in:d=1.0,afade=t=out:st={TOTAL - 2.5:.3f}:d=2.5[m];"
         "[0:a]asplit[v1][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=400[duck];"
         f"[v1][duck]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89,atrim=0:{TOTAL:.3f}[a]",
         "-map", "[a]", "-c:a", "pcm_s16le", mix])
    return mix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out")
    ap.add_argument("--work", default="build")
    ap.add_argument("--reuse-cut", action="store_true", help="keep an existing work/cut.mp4 (graphics-only changes)")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    print(f"cut duration {CUT_DUR:.2f}s, total {TOTAL:.2f}s", flush=True)
    base = make_base(a.raw, a.work)
    cut = os.path.join(a.work, "cut.mp4")
    if not (a.reuse_cut and os.path.exists(cut)):
        cut = make_cut(base, a.work)
    items = make_overlays(a.work)
    video = make_overlay_pass(cut, items, a.work)
    mix = make_audio(cut, a.work)
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", a.out])


if __name__ == "__main__":
    main()
