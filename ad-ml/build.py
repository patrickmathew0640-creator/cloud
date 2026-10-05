"""Build the Malayalam Video Studio ad reel: voice track timings -> index.html (HyperFrames) + audio mix."""
import json, subprocess, sys

SR = 48000
GAP, LEAD, TAIL = 0.35, 0.4, 1.2
lines = json.load(open("vo/lines.json"))

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

T, t = [], LEAD
for k, _ in lines:
    d = dur(f"vo/{k}.mp3"); T.append((t, t + d)); t += d + GAP
DUR = round(t - GAP + TAIL, 2)
S = [0.0] + [s - 0.25 for s, _ in T[1:]] + [DUR]          # scene boundaries
sc = lambda i: (S[i], S[i + 1] - S[i])

CAPS = [
    "എല്ലാ ദിവസവും *റീൽസ്* ഇടണം|പക്ഷേ *സമയമില്ലേ?*",
    "*ക്യാമറ* വേണ്ട, *എഡിറ്റർ* വേണ്ട|മണിക്കൂറുകളോളം *എഡിറ്റിംഗും* വേണ്ട",
    "ഇതാ *Video Studio*|ഒരു *വാചകം* ടൈപ്പ് ചെയ്താൽ മതി",
    "*വോയ്സ്, ക്യാപ്ഷൻ, മ്യൂസിക്*|എല്ലാം റെഡി — *മലയാളത്തിൽ!*",
    "*റീൽസ്, ഷോർട്ട്സ്, ആഡ്സ്*|എല്ലാം നിങ്ങളുടെ *ലാപ്ടോപ്പിൽ*",
    "ഒരു വീഡിയോയ്ക്ക് *₹0*|ഒറ്റത്തവണ — വെറും *₹499*",
    "ഇപ്പോൾ തന്നെ *വാങ്ങൂ!*",
]

def cap_html(i, txt):
    parts = txt.split("|"); s, e = T[i]; n = len(parts); out = []
    for j, p in enumerate(parts):
        a = s + (e - s) * j / n - (0.05 if j == 0 else 0); b = s + (e - s) * (j + 1) / n + (0.25 if j == n - 1 else 0)
        words = []
        for w in p.split(" "):
            hl = w.startswith("*") or w.endswith("*") or w.endswith("*,") or w.endswith("*?") or "*" in w
            words.append(f'<span class="w{" hl" if hl else ""}">{w.replace("*", "")}</span>')
        out.append((f"cap{i}_{j}", a, b, " ".join(words)))
    return out

# carry highlight state across multi-word *...* spans
def fix_hl(txt):
    res, on = [], False
    for w in txt.split(" "):
        st = w.startswith("*"); en = w.rstrip(",?!—").endswith("*")
        if st: on = True
        res.append(("*" + w.replace("*", "") + "*") if on else w.replace("*", ""))
        if en: on = False
    return " ".join(res)
CAPS = ["|".join(fix_hl(p) for p in c.split("|")) for c in CAPS]
capdivs = [c for i, t_ in enumerate(CAPS) for c in cap_html(i, t_)]

html = open("src/template.html").read()
rep = {"__DUR__": str(DUR)}
for i in range(7):
    rep[f"__S{i}__"], rep[f"__D{i}__"] = (f"{v:.2f}" for v in sc(i))
rep["__CAPS__"] = "\n".join(f'      <div id="{cid}" class="cap clip" data-start="{a:.2f}" data-duration="{b-a:.2f}" data-track-index="9"><div class="capbox">{w}</div></div>'
                            for cid, a, b, w in capdivs)
rep["__JS_CAPS__"] = json.dumps([[f"#{cid}", round(a, 2), round(b, 2)] for cid, a, b, _ in capdivs])
rep["__JS_S__"] = json.dumps([round(x, 2) for x in S])
rep["__JS_T__"] = json.dumps([[round(a, 2), round(b, 2)] for a, b in T])
for k, v in rep.items():
    html = html.replace(k, v)
open("index.html", "w").write(html)

# ---------------- audio
def run(a): subprocess.run(a, check=True)
ins, ch = [], []
for i, ((k, _), (s, _)) in enumerate(zip(lines, T)):
    ins += ["-i", f"vo/{k}.mp3"]; ms = int(s * 1000)
    ch.append(f"[{i}:a]aresample={SR},adelay={ms}|{ms}[v{i}]")
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
     ";".join(ch) + ";" + "".join(f"[v{i}]" for i in range(len(lines))) +
     f"amix=inputs={len(lines)}:normalize=0,apad,atrim=0:{DUR},loudnorm=I=-15:TP=-2,aresample={SR}[o]",
     "-map", "[o]", "-ac", "2", "build_voice.wav"])
sfx = [("whoosh", S[1] - 0.1, 0.5), ("whoosh", S[2] - 0.1, 0.5), ("riser", S[2] - 1.0, 0.35), ("impact", S[2] + 0.1, 0.45),
       ("whoosh", S[3] - 0.1, 0.5), ("whoosh", S[4] - 0.1, 0.5), ("whoosh", S[5] - 0.1, 0.5), ("ding", S[5] + 2.3, 0.5),
       ("impact", S[6] + 0.1, 0.45), ("pop", S[6] + 1.0, 0.6)]
sfx += [("pop", S[1] + 0.4 + 0.9 * j, 0.5) for j in range(3)] + [("pop", S[3] + 0.6 + 0.6 * j, 0.45) for j in range(4)]
sfx += [("click", S[2] + 1.2 + 0.08 * j, 0.25) for j in range(0, 24, 2)]
ins, ch = [], []
for i, (n, tt, v) in enumerate(sfx):
    ins += ["-i", f"assets/{n}.wav"]; ms = int(tt * 1000)
    ch.append(f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[s{i}]")
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(ch) + ";" + "".join(f"[s{i}]" for i in range(len(sfx))) +
     f"amix=inputs={len(sfx)}:normalize=0,apad,atrim=0:{DUR}[o]", "-map", "[o]", "-ac", "2", "build_sfx.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", "assets/Inspired.mp3", "-i", "build_voice.wav", "-i", "build_sfx.wav", "-filter_complex",
     f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample={SR},volume=0.32,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-1.5}:d=1.5[m];"
     "[1:a]asplit[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[d];"
     f"[v][d][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.89,atrim=0:{DUR}[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "build_mix.wav"])
print("DUR", DUR, "S", [round(x, 2) for x in S])
if len(sys.argv) > 2:
    run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-i", "build_mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", sys.argv[2]])
