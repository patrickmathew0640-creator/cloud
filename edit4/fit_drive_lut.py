"""Fit a 3D LUT that maps the source's decoded frames to Google Drive's own SDR rendition (source/drive_ref.mp4),
so the speaker looks exactly like the reference the client watches on Drive."""
import subprocess
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import uniform_filter


def frame(src, t, extra=""):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf",
                          "scale=270:480:flags=area,format=rgb24" + extra, "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(480, 270, 3).astype(float)


train, test = np.arange(1.0, 84.0, 1.4), np.arange(1.7, 84.0, 7.0)
X, Y = [], []
for t in train:
    a, b = uniform_filter(frame("source/input.mp4", t), (5, 5, 1)), uniform_filter(frame("source/drive_ref.mp4", t), (5, 5, 1))
    X.append(a.reshape(-1, 3)); Y.append(b.reshape(-1, 3))
X, Y = np.concatenate(X) / 255, np.concatenate(Y) / 255
N = 33
idx = np.clip(np.rint(X * (N - 1)).astype(int), 0, N - 1)
flat = idx[:, 0] * N * N + idx[:, 1] * N + idx[:, 2]
cnt = np.bincount(flat, minlength=N ** 3)
sums = np.stack([np.bincount(flat, weights=Y[:, c], minlength=N ** 3) for c in range(3)], 1)
g = np.stack(np.meshgrid(*[np.linspace(0, 1, N)] * 3, indexing="ij"), -1).reshape(-1, 3)
lut = g.copy()
have = cnt >= 8
lut[have] = sums[have] / cnt[have, None]
d, j = cKDTree(g[have]).query(g[~have])          # empty cells borrow the nearest fitted offset
lut[~have] = g[~have] + (lut[have][j] - g[have][j])
res = (lut - g).reshape(N, N, N, 3)
for c in range(3):
    res[..., c] = uniform_filter(res[..., c], 3)
lut = np.clip(g.reshape(N, N, N, 3) + res, 0, 1)
with open("drive_match.cube", "w") as f:
    f.write(f"# Matches Google Drive's SDR rendition of the source (fitted by fit_drive_lut.py)\nLUT_3D_SIZE {N}\n")
    for b in range(N):
        for gg in range(N):
            for r in range(N):
                v = lut[r, gg, b]
                f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
print("populated cells", int(have.sum()))
e = [np.abs(frame("source/input.mp4", t, ",lut3d=drive_match.cube") - frame("source/drive_ref.mp4", t)).mean() for t in test]
m = np.mean([frame("source/input.mp4", t, ",lut3d=drive_match.cube").mean((0, 1)) for t in test], 0)
r = np.mean([frame("source/drive_ref.mp4", t).mean((0, 1)) for t in test], 0)
print("held-out MAE", round(float(np.mean(e)), 2), "mean RGB lut", m.round(1), "drive", r.round(1))
