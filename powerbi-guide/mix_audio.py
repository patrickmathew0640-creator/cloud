"""Build the soundtrack for the guide: the voice track from build.py over quiet, ducked background music.

Usage: python mix_audio.py renders/powerbi-guide-silent.mp4 ../deliverables/powerbi-mcp-guide-1080p.mp4
"""
import json
import subprocess
import sys

DUR = json.load(open("timing.json"))["total"]
SR = 48000
# All by Kevin MacLeod (incompetech.com), CC BY 4.0. Played back to back with 3s crossfades.
MUSIC = ["audio/Inspired.mp3", "audio/Wallpaper.mp3", "audio/Carefree.mp3"]


def run(args):
    print(" ".join(args[:6]), "...", flush=True)
    subprocess.run(args, check=True)


# 1) Voice: light clean-up and loudness to -16 LUFS
run(["ffmpeg", "-v", "error", "-y", "-i", "vo.wav",
     "-af", f"highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120:makeup=1.5,"
            f"loudnorm=I=-16:TP=-2:LRA=9,aresample={SR},apad,atrim=0:{DUR}",
     "-ac", "2", "build_voice.wav"])

# 2) Music bed: crossfaded playlist, quiet, ducked under the voice, faded at both ends
inputs = sum((["-i", m] for m in MUSIC), [])
n = len(MUSIC)
chain = "[0:a]aresample=48000[m0];" + "".join(f"[{i}:a]aresample=48000[r{i}];" for i in range(1, n))
prev = "m0"
for i in range(1, n):
    chain += f"[{prev}][r{i}]acrossfade=d=3:c1=tri:c2=tri[m{i}];"
    prev = f"m{i}"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", "build_voice.wav", "-filter_complex",
     chain + f"[{prev}]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume=0.2,"
     f"afade=t=in:st=0:d=1.5,afade=t=out:st={DUR - 4}:d=4[m];"
     f"[{n}:a]anull[sc];[m][sc]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=500[duck]",
     "-map", "[duck]", "-ac", "2", "build_music.wav"])

# 3) Final mix + limiter
run(["ffmpeg", "-v", "error", "-y", "-i", "build_voice.wav", "-i", "build_music.wav", "-filter_complex",
     f"[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:attack=3:release=50,atrim=0:{DUR}[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "build_mix.wav"])

# 4) Mux with the silent render
if len(sys.argv) > 2:
    run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-i", "build_mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", sys.argv[2]])
