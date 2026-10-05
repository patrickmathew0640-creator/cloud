"""Cut vertical Shorts (1080x1920) out of video 2, reusing its subtitles, callouts, grade and music.

Usage: python3 shorts.py <raw2.mp4> <outdir> [--work DIR] [--only N]

Each short: 9:16 window around the speaker taken straight from the 4K source, pauses removed,
wide / punch-in framing alternating, hook title for the first seconds, top callouts, big captions,
like/subscribe click at the end, cleaned voice + soft ducked music.
"""
import argparse
import os
import subprocess

from PIL import Image

import edit_v2 as ed
import graphics as g

W, H, FPS = 1080, 1920, 30
VCROP = "crop=675:1200:800:1320"      # 9:16 window centred on the speaker inside the 2160x1200 picture band
PUNCH = 1.12
ZOOM_CENTER = (540, 860)              # speaker's face on the 1080x1920 frame
MIN_HOLD = 2.5
HOOK_DUR = 3.6
SUBS_DUR = 4.6
MUSIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "edit2", "audio", ed.MUSIC)

SHORTS = [   # name, source windows, hook (tag, line 1, line 2)
    ("short1-2hours-vs-30min", [(16.14, 46.08)], ("AI AT WORK", "Same Job:", "2 Hours vs 30 Min")),
    ("short2-will-ai-replace-you", [(46.24, 70.30)], ("THE REAL QUESTION", "Will AI", "Replace You?")),
    ("short3-dont-learn-100-tools", [(70.38, 100.60)], ("HOW TO START", "Don't Learn", "100 AI Tools!")),
    ("short4-ai-is-your-assistant", [(100.70, 118.03), (131.16, 135.80)], ("MINDSET", "Don't Fear AI,", "Use It!")),
]


def run(args):
    print("+", " ".join(a if len(a) < 80 else a[:80] + "…" for a in args[:12]), flush=True)
    subprocess.run(args, check=True)


def pieces_for(windows):
    out = []
    for w0, w1 in windows:
        for s, e in ed.KEEP:
            s, e = max(s, w0 - 0.10), min(e, w1 + 0.25)
            if e - s < 0.2:
                continue
            cuts = [s] + [x for x in ed.SPLITS if s < x < e] + [e]
            out += list(zip(cuts[:-1], cuts[1:]))
    segs, z, held = [], PUNCH, MIN_HOLD
    for s, e in out:
        if held >= MIN_HOLD:
            z, held = (1.0 if z == PUNCH else PUNCH), 0.0
        segs.append((s, e, z))
        held += e - s
    return segs


def build_map(segs):
    m, t = [], 0.0
    for s, e, z in segs:
        m.append((s, e, t, z))
        t += round((e - s) * FPS) / FPS
    return m, t


def remapper(m, total):
    def remap(ts):
        for s, e, o, _ in m:
            if ts < s:
                return o
            if ts <= e:
                return o + ts - s
        return total
    return remap


def autocrop(path):
    im = Image.open(path)
    x0, y0, x1, y1 = im.getbbox() or (0, 0, 2, 2)
    x0, y0 = max(0, x0 - 4) & ~1, max(0, y0 - 4) & ~1
    x1, y1 = min(W, x1 + 4), min(H, y1 + 4)
    im.crop((x0, y0, x1, y1)).save(path)
    return x0, y0


def anim(it):
    t0, d = it["t0"], it["t1"] - it["t0"]
    x, y, a = str(it["x"]), str(it["y"]), []
    if it["anim"] == "drop":       # hook / callout: slide down + fade, fade out
        y = f"{it['y']}-60*pow(max(0,1-(t-{t0:.3f})/0.4),3)"
        a = ["fade=t=in:st=0:d=0.4:alpha=1", f"fade=t=out:st={max(0, d - 0.35):.3f}:d=0.35:alpha=1"]
    elif it["anim"] == "pop_in":
        y = f"{it['y']}-40*pow(max(0,1-(t-{t0:.3f})/0.3),3)"
        a = ["fade=t=in:st=0:d=0.3:alpha=1"]
    elif it["anim"] == "fade_out":
        a = [f"fade=t=out:st={max(0, d - 0.4):.3f}:d=0.4:alpha=1"]
    return x, y, a


def make_short(raw, name, windows, hook, outdir, work):
    wdir = os.path.join(work, name)
    os.makedirs(wdir, exist_ok=True)
    segs = pieces_for(windows)
    m, total = build_map(segs)
    remap = remapper(m, total)
    print(f"== {name}: {len(segs)} pieces, {total:.2f}s", flush=True)

    # 1) segments straight from the 4K source
    lst = []
    for i, (s, e, o, z) in enumerate(m):
        fr = f"{VCROP},scale={W}:{H}:flags=lanczos"
        if z != 1.0:
            cw, ch = round(W / z / 2) * 2, round(H / z / 2) * 2
            x = min(max(0, round(ZOOM_CENTER[0] - cw / 2)), W - cw)
            y = min(max(0, round(ZOOM_CENTER[1] - ch / 2)), H - ch)
            fr += f",crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos"
        n = round((e - s) * FPS)
        seg = os.path.join(wdir, f"s{i:03d}.mkv")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", raw, "-t", f"{e - s:.3f}",
             "-vf", f"{fr},fps={FPS},{ed.GRADE},setsar=1,format=yuv420p", "-frames:v", str(n),
             "-af", f"aresample=48000,afade=t=in:d=0.012,afade=t=out:st={e - s - 0.012:.3f}:d=0.012,"
                    f"apad,atrim=0:{n / FPS:.4f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-c:a", "pcm_s16le", "-ac", "2", seg])
        lst.append(f"file '{os.path.abspath(seg)}'")
    open(os.path.join(wdir, "list.txt"), "w").write("\n".join(lst) + "\n")
    cut = os.path.join(wdir, "cut.mkv")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(wdir, "list.txt"),
         "-c", "copy", cut])

    # 2) graphics
    jobs, items = [], []

    def add(fname, inner, t0, t1, a):
        jobs.append((fname, inner))
        items.append({"file": os.path.join(wdir, fname), "t0": t0, "t1": t1, "anim": a})

    w0, w1 = windows[0][0], windows[-1][1]
    caps = [[remap(s), remap(e), t] for s, e, t in ed.CAPTIONS
            if any(a - 0.1 <= s and e <= b + 0.6 for a, b in windows)]
    for a, b in zip(caps, caps[1:]):
        if b[0] - a[1] < 1.5:
            a[1] = b[0]
    caps[-1][1] = total
    for i, (s, e, t) in enumerate(caps):
        add(f"cap{i:02d}.png", g.vsub_html(t), s, e, "cut")
    add("hook.png", g.vhook_html(*hook), 0.0, HOOK_DUR, "fade_out")   # visible from frame 1 (thumbnail)
    subs0 = total - SUBS_DUR
    for i, (k, emo, text, s, e) in enumerate(ed.CALLOUTS):
        if not any(a - 0.1 <= s < b for a, b in windows):
            continue
        s, e = max(remap(s), HOOK_DUR + 0.2), min(remap(e), subs0 - 0.2)
        if e - s >= 1.5:
            add(f"call{i:02d}.png", g.vcall_html(k, emo, text), s, e, "drop")
    add("subsA.png", g.vsubs_html(False, False), subs0, subs0 + 1.3, "pop_in")
    add("subsB.png", g.vsubs_html(False, True), subs0 + 1.3, subs0 + 2.0, "cut")
    add("subsC.png", g.vsubs_html(True, True), subs0 + 2.0, subs0 + 2.9, "cut")
    add("subsD.png", g.vsubs_html(True, False), subs0 + 2.9, total, "fade_out")
    g.render(jobs, wdir, size=(W, H), extra_css=g.VERT_CSS)
    for it in items:
        it["x"], it["y"] = autocrop(it["file"])

    # 3) overlays
    video = os.path.join(wdir, "video.mp4")
    args, fc, last = ["ffmpeg", "-v", "error", "-y", "-i", cut], [], "0:v"
    for i, it in enumerate(items, start=1):
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{it['t1'] - it['t0']:.3f}", "-i", it["file"]]
        x, y, alpha = anim(it)
        fc.append(f"[{i}:v]" + ",".join(["format=rgba"] + alpha + [f"setpts=PTS-STARTPTS+{it['t0']:.3f}/TB"]) + f"[g{i}]")
        fc.append(f"[{last}][g{i}]overlay=x='{x}':y='{y}':eof_action=pass:format=auto[o{i}]")
        last = f"o{i}"
    fc.append(f"[{last}]format=yuv420p[v]")
    script = os.path.join(wdir, "overlay.fc")
    open(script, "w").write(";\n".join(fc))
    run(args + ["-filter_complex_script", script, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium",
                "-crf", "18", video])

    # 4) audio: cleaned voice + ducked music
    mix = os.path.join(wdir, "mix.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-stream_loop", "-1", "-i", MUSIC, "-filter_complex",
         "[0:a]highpass=f=80,afftdn=nf=-30,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=1.5,"
         "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=8,"
         f"aresample=48000,apad=whole_dur={total:.4f},atrim=0:{total:.4f},asplit[v1][sc];"
         f"[1:a]atrim=0:{total:.4f},asetpts=PTS-STARTPTS,aresample=48000,volume={ed.MUSIC_VOL},"
         f"afade=t=in:d=0.5,afade=t=out:st={total - 1.2:.3f}:d=1.2[m];"
         "[m][sc]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=400[duck];"
         f"[v1][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]",
         "-map", "[a]", "-ac", "2", "-c:a", "pcm_s16le", mix])
    out = os.path.join(outdir, f"{name}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("outdir")
    ap.add_argument("--work", default="build_shorts")
    ap.add_argument("--only", type=int)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for i, (name, windows, hook) in enumerate(SHORTS, start=1):
        if a.only and a.only != i:
            continue
        make_short(a.raw, name, windows, hook, a.outdir, a.work)


if __name__ == "__main__":
    main()
