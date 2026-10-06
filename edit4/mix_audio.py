"""Build the ad soundtrack: cut + cleaned voice, ducked music, timed SFX; optionally mux onto a silent render.

usage: python3 mix_audio.py [silent_render.mp4 final.mp4]
"""
import json
import subprocess
import sys

from cuts import SEGS, CUT_TIMES
from build import DURATION as DUR

MUSIC = "audio/Inspired.mp3"   # "Inspired" by Kevin MacLeod (incompetech.com), CC BY 4.0
SR = 48000


def run(args):
    print(" ".join(args[:6]), "...", flush=True)
    subprocess.run(args, check=True)


# 1) Voice: same cuts as the picture (10 ms fades at the joins), rumble cut, light denoise, presence, compression, -15 LUFS
chains, labels = [], []
for i, (s, e) in enumerate(SEGS):
    d = round(e - s, 4)
    chains.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={d - 0.01}:d=0.01[a{i}]")
    labels.append(f"[a{i}]")
# (the laptop b-roll has no speech, only room noise, so the camera audio is muted there)
fc = ";".join(chains) + f";{''.join(labels)}concat=n={len(SEGS)}:v=0:a=1," \
    "highpass=f=85,afftdn=nf=-28,equalizer=f=3200:t=q:w=1.4:g=2,equalizer=f=250:t=q:w=1:g=-2," \
    "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2," \
    f"loudnorm=I=-15:TP=-2:LRA=8,aresample={SR}," \
    f"volume=0:enable='between(t,{CUT_TIMES[1] - 0.02},{CUT_TIMES[2] + 0.02})',apad,atrim=0:{DUR}[v]"
run(["ffmpeg", "-v", "error", "-y", "-i", "source/input.mp4", "-filter_complex", fc, "-map", "[v]", "-ac", "2", "build_voice.wav"])

# 2) SFX bed
cues = json.load(open("sfx_cues.json"))
inputs, chains = [], []
for i, (name, t, vol) in enumerate(cues):
    inputs += ["-i", f"audio/{name}.wav"]
    ms = max(0, int(round(t * 1000)))
    chains.append(f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{i}]")
mix = "".join(f"[s{i}]" for i in range(len(cues)))
fc = ";".join(chains) + f";{mix}amix=inputs={len(cues)}:normalize=0:dropout_transition=0,apad,atrim=0:{DUR}[out]"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ac", "2", "build_sfx.wav"])

# 3) Music: full energy on the hook / b-roll / end card, ducked under the voice by a sidechain
run(["ffmpeg", "-v", "error", "-y", "-i", MUSIC, "-i", "build_voice.wav", "-filter_complex",
     f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample={SR},volume=0.42,"
     f"afade=t=in:st=0:d=0.15,afade=t=out:st={DUR - 1.6}:d=1.6[m];"
     "[1:a]anull[sc];"
     "[m][sc]sidechaincompress=threshold=0.025:ratio=7:attack=15:release=400:makeup=1[duck]",
     "-map", "[duck]", "-ac", "2", "build_music.wav"])

# 4) Final mix + limiter
run(["ffmpeg", "-v", "error", "-y", "-i", "build_voice.wav", "-i", "build_music.wav", "-i", "build_sfx.wav",
     "-filter_complex", f"[0:a][1:a][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.9:attack=3:release=50,atrim=0:{DUR}[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "build_mix.wav"])

# 5) Mux with the silent render
if len(sys.argv) > 2:
    run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-i", "build_mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", sys.argv[2]])
