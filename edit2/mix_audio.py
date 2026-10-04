"""Build the final soundtrack: cleaned voice + ducked background music + timed SFX, then mux onto the render."""
import json
import subprocess
import sys

DUR = 57.7
MUSIC = "audio/Inspired.mp3"   # "Inspired" by Kevin MacLeod (incompetech.com), CC BY 4.0
SR = 48000


def run(args):
    print(" ".join(args[:6]), "...", flush=True)
    subprocess.run(args, check=True)


# 1) Voice: rumble cut, light denoise, de-harsh, compression, loudness to -16 LUFS
run(["ffmpeg", "-v", "error", "-y", "-i", "source/input.mp4", "-vn",
     "-af", "highpass=f=85,afftdn=nf=-28,equalizer=f=3500:t=q:w=1.5:g=1.5,equalizer=f=250:t=q:w=1:g=-2,"
            "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2,"
            f"loudnorm=I=-16:TP=-2:LRA=8,aresample={SR}",
     "-ac", "2", "build_voice.wav"])

# 2) SFX bed: every cue delayed to its time, mixed without normalisation
cues = json.load(open("sfx_cues.json"))
inputs, chains = [], []
for i, (name, t, vol) in enumerate(cues):
    inputs += ["-i", f"audio/{name}.wav"]
    ms = int(round(t * 1000))
    chains.append(f"[{i}:a]aresample={SR},volume={vol},adelay={ms}|{ms}[s{i}]")
mix = "".join(f"[s{i}]" for i in range(len(cues)))
fc = ";".join(chains) + f";{mix}amix=inputs={len(cues)}:normalize=0:dropout_transition=0,apad,atrim=0:{DUR}[out]"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ac", "2", "build_sfx.wav"])

# 3) Music: trimmed, faded, ducked under the voice with a sidechain compressor
run(["ffmpeg", "-v", "error", "-y", "-i", MUSIC, "-i", "build_voice.wav", "-filter_complex",
     f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample={SR},volume=0.30,"
     f"afade=t=in:st=0:d=0.4,afade=t=out:st={DUR-1.8}:d=1.8[m];"
     "[1:a]anull[sc];"
     "[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[duck]",
     "-map", "[duck]", "-ac", "2", "build_music.wav"])

# 4) Final mix + limiter
run(["ffmpeg", "-v", "error", "-y", "-i", "build_voice.wav", "-i", "build_music.wav", "-i", "build_sfx.wav",
     "-filter_complex",
     "[0:a][1:a][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.89:attack=3:release=50,"
     f"atrim=0:{DUR}[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "build_mix.wav"])

# 5) Mux with the silent render
if len(sys.argv) > 1:
    run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-i", "build_mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", sys.argv[2]])
