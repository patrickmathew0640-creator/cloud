"""Cut + tone-map (HLG -> SDR BT.709) + grade the source into assets/speaker.mp4 (1080x1920, 30fps)."""
import subprocess
from cuts import SEGS

TM = ("zscale=w=1080:h=1920:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
GRADE = {0: "eq=contrast=1.10:saturation=1.12:gamma=0.94",   # bright window glare on the iPad shot
         1: "eq=contrast=1.08:saturation=1.12:gamma=0.97"}
L = []
for i, (s, e) in enumerate(SEGS):
    g = GRADE.get(i, "eq=contrast=1.06:saturation=1.15")
    out = f"build/seg{i}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-i", "source/input.mp4", "-t", str(round(e - s, 4)), "-an",
                    "-vf", f"{TM},{g},unsharp=5:5:0.4,fps=30", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "15",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", out], check=True)
    L.append(f"file 'seg{i}.mp4'")
open("build/list.txt", "w").write("\n".join(L))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/list.txt", "-c", "copy",
                "-movflags", "+faststart", "assets/speaker.mp4"], check=True)
