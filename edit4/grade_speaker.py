"""Cut + tone-map (HLG -> SDR BT.709, no extra grading) the 4K source into assets/speaker.mp4 (2160x3840, 30fps)."""
import subprocess
from cuts import SEGS

TM = ("zscale=t=linear:npl=400,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
L = []
for i, (s, e) in enumerate(SEGS):
    out = f"build/seg{i}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-i", "source/input.mp4", "-t", str(round(e - s, 4)), "-an",
                    "-vf", f"{TM},fps=30", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", "15",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", out], check=True)
    L.append(f"file 'seg{i}.mp4'")
open("build/list.txt", "w").write("\n".join(L))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/list.txt", "-c", "copy",
                "-movflags", "+faststart", "assets/speaker.mp4"], check=True)
