"""Build the final soundtrack (voice cut on the same edit points + ducked original music + timed SFX) and mux it.

    python3 mix_audio.py [silent_render.mp4 final.mp4]
"""
import json
import subprocess
import sys

DUR = 69.5
SR = 48000
CUTS = [(2.40, 11.80), (12.70, 22.2667), (22.80, 69.1667)]  # source seconds kept, in order


def run(args):
    print(" ".join(args[:6]), "...", flush=True)
    subprocess.run(args, check=True)


# 1) Voice: same cuts as the picture, 12 ms fades at each join, gentle cleanup and compression
parts = []
for i, (a, b) in enumerate(CUTS):
    parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample={SR},afade=t=in:d=0.012,afade=t=out:st={b - a - 0.012:.3f}:d=0.012[v{i}]")
fc = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(CUTS))) + f"concat=n={len(CUTS)}:v=0:a=1,"
fc += ("highpass=f=80,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=4000:t=q:w=1.4:g=1.5,"
       "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
       f"loudnorm=I=-16:TP=-2:LRA=8,aresample={SR},apad,atrim=0:{DUR}[out]")
run(["ffmpeg", "-v", "error", "-y", "-i", "source/input.mp4", "-filter_complex", fc, "-map", "[out]", "-ac", "2", "build_voice.wav"])

# 2) SFX bed
cues = json.load(open("sfx_cues.json"))
inputs, chains = [], []
for i, (name, t, vol) in enumerate(cues):
    inputs += ["-i", f"audio/{name}.wav"]
    ms = max(0, int(round(t * 1000)))
    chains.append(f"[{i}:a]aresample={SR},volume={vol},adelay={ms}|{ms}[s{i}]")
fc = ";".join(chains) + ";" + "".join(f"[s{i}]" for i in range(len(cues))) + \
    f"amix=inputs={len(cues)}:normalize=0:dropout_transition=0,volume=0.8,apad,atrim=0:{DUR}[out]"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ac", "2", "build_sfx.wav"])

# 3) Music ducked under the voice (sidechain), full level on the end card where there is no voice
run(["ffmpeg", "-v", "error", "-y", "-i", "audio/music.wav", "-i", "build_voice.wav", "-filter_complex",
     f"[0:a]atrim=0:{DUR},aresample={SR},volume=0.62[m];[1:a]anull[sc];"
     "[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=320:makeup=1[duck]",
     "-map", "[duck]", "-ac", "2", "build_music.wav"])

# 4) Final mix, limiter, social loudness (-14 LUFS)
run(["ffmpeg", "-v", "error", "-y", "-i", "build_voice.wav", "-i", "build_music.wav", "-i", "build_sfx.wav",
     "-filter_complex",
     "[0:a][1:a][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.89:attack=3:release=60,"
     f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample={SR},atrim=0:{DUR}[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "build_mix.wav"])

if len(sys.argv) > 2:
    run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-i", "build_mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", sys.argv[2]])
