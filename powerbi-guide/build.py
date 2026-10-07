"""Build the Power BI MCP guide video project.

1. Voices every narration line in script.py with edge-tts (cached in vo/).
2. Lays the lines out on one timeline: each scene starts with LEAD, lines are GAP apart, scenes end with TAIL.
3. Writes vo.wav (the whole voice track), timing.json, and index.html from src/template.html.

Needs: pip install edge-tts, plus ffmpeg/ffprobe on PATH.
"""
import asyncio
import hashlib
import html
import json
import os
import re
import subprocess

import edge_tts

from script import SCENES

VOICE = "en-IN-NeerjaNeural"
RATE = "-3%"
LEAD, GAP, TAIL = 0.55, 0.42, 0.85
SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))


def run(args):
    subprocess.run(args, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


async def tts(text, path):
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)
            return
        except Exception:
            if attempt == 3:
                raise
            await asyncio.sleep(2 ** attempt)


async def voice_all():
    os.makedirs(os.path.join(HERE, "vo"), exist_ok=True)
    clips = {}
    for _, _, lines in SCENES:
        for line in lines:
            beat, caption = line[0], line[1]
            spoken = line[2] if len(line) > 2 else caption
            key = hashlib.sha1(f"{VOICE}|{RATE}|{spoken}".encode()).hexdigest()[:12]
            wav = os.path.join(HERE, "vo", f"{beat}_{key}.wav")
            if not os.path.exists(wav):
                mp3 = wav[:-4] + ".mp3"
                await tts(spoken, mp3)
                # Trim the silence edge-tts leaves at both ends so GAP is the real pause.
                run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af",
                     "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                     "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                     "-ar", str(SR), "-ac", "1", wav])
                os.remove(mp3)
            clips[beat] = wav
    return clips


def split_caption(text, limit=64):
    """Split a caption into on-screen chunks of at most ~limit characters, at sentence or comma breaks."""
    parts = re.split(r"(?<=[.!?:])\s+(?=\S)", text)
    chunks = []
    for p in parts:
        while len(p) > limit:
            cut = max((m.end() for m in re.finditer(r"[,;]\s|\s(?:and|or|then|with|so|because)\s", p[:limit + 8])),
                      default=0)
            if cut < limit * 0.35:
                cut = p.rfind(" ", 0, limit) + 1
            chunks.append(p[:cut].strip())
            p = p[cut:].strip()
        chunks.append(p)
    merged = []
    for c in chunks:
        if merged and len(merged[-1]) + len(c) + 1 <= limit * 0.75:
            merged[-1] += " " + c
        else:
            merged.append(c)
    return merged


def main():
    clips = asyncio.run(voice_all())

    t = 0.0
    scenes, beats, caps = {}, {}, []
    for sid, title, lines in SCENES:
        start = t
        t += LEAD
        for line in lines:
            beat, caption = line[0], line[1]
            d = duration(clips[beat])
            beats[beat] = round(t, 3)
            beats[beat + "_end"] = round(t + d, 3)
            chunks = split_caption(caption)
            total = sum(len(c) for c in chunks)
            ct = t
            for c in chunks:
                cd = d * len(c) / total
                caps.append((round(ct, 3), round(cd + (GAP * 0.8 if c is chunks[-1] else 0), 3), c))
                ct += cd
            t += d + GAP
        t += TAIL - GAP
        scenes[sid] = {"start": round(start, 3), "dur": round(t - start, 3), "title": title}
    total = round(t + 0.6, 3)  # short hold on the last frame
    scenes["outro"]["dur"] = round(total - scenes["outro"]["start"], 3)

    # Voice track
    order = [line[0] for _, _, lines in SCENES for line in lines]
    inputs, chains = [], []
    for i, b in enumerate(order):
        inputs += ["-i", clips[b]]
        ms = int(round(beats[b] * 1000))
        chains.append(f"[{i}:a]adelay={ms}[a{i}]")
    fc = ";".join(chains) + ";" + "".join(f"[a{i}]" for i in range(len(order))) + \
        f"amix=inputs={len(order)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[out]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", str(SR),
         os.path.join(HERE, "vo.wav")])

    json.dump({"total": total, "scenes": scenes, "beats": beats}, open(os.path.join(HERE, "timing.json"), "w"),
              indent=1)

    # index.html
    src = open(os.path.join(HERE, "src", "template.html")).read()
    src = src.replace("{{TOTAL}}", str(total))
    src = re.sub(r"\{\{(\w+)\.(start|dur)\}\}", lambda m: str(scenes[m.group(1)][m.group(2)]), src)
    src = src.replace("/*__TIMING__*/", "const T = " + json.dumps(beats) + ";\n      const S = " +
                      json.dumps({k: [v["start"], v["dur"]] for k, v in scenes.items()}) + ";")
    cap_html = "\n".join(
        f'      <div id="cap{i}" class="cap clip" data-start="{s}" data-duration="{d}" data-track-index="9">'
        f'<span>{html.escape(c)}</span></div>' for i, (s, d, c) in enumerate(caps))
    src = src.replace("<!--__CAPTIONS__-->", cap_html)
    open(os.path.join(HERE, "index.html"), "w").write(src)

    print(f"total {total:.1f}s, {len(order)} lines, {len(caps)} captions")
    for sid, v in scenes.items():
        print(f"  {sid:8s} {v['start']:7.2f} +{v['dur']:.2f}")


if __name__ == "__main__":
    main()
