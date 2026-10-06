"""Synthesize the original music bed and extra SFX for the Power BI MCP ad (no third-party audio, no licence strings).

Music is arranged section by section on the edit's own timeline (seconds on the output timeline):
  0.00 hook groove -> 9.40 full groove -> 18.97 tension ("hours to days") with build -> 29.83 drop ("But we automated it")
  -> 55.47 price stab -> 59.03 CTA groove -> 65.33 outro chord.
"""
import numpy as np
from scipy.signal import butter, sosfilt
import wave

SR = 48000
DUR = 69.5
BPM = 124
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def write(path, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f / (SR / 2), "high", output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def t_(d):
    return np.arange(int(d * SR)) / SR


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def saw(f, t, phase=0.0):
    return 2 * ((f * t + phase) % 1) - 1


# ---------------------------------------------------------------- instruments
def kick(level=1.0):
    t = t_(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 300) * 0.25
    return np.tanh((body + click) * 1.6) * level


def clap(level=1.0):
    t = t_(0.35)
    n = bp(rng.standard_normal(len(t)), 900, 5000)
    env = np.zeros(len(t))
    for d in (0.0, 0.011, 0.022):
        i = int(d * SR)
        env[i:] += np.exp(-(t[: len(t) - i]) * 70)
    env += np.exp(-t * 14) * 0.35
    return n * env * 0.5 * level


def hat(open_=False, level=1.0):
    t = t_(0.25 if open_ else 0.06)
    n = hp(rng.standard_normal(len(t)), 7000, 4)
    return n * np.exp(-t * (14 if open_ else 90)) * 0.28 * level


def tick(level=1.0):
    t = t_(0.03)
    return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 220) * 0.35 * level + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 300) * 0.12 * level


def pluck(note, dur=0.32, level=1.0, bright=4500):
    t = t_(dur)
    f = mtof(note)
    x = saw(f, t) * 0.6 + saw(f * 1.004, t, 0.3) * 0.4
    x = lp(x * np.exp(-t * 9), bright)
    return x * np.minimum(1, t * 400) * level * 0.32


def pad(notes, dur, level=1.0, cutoff=2400):
    t = t_(dur)
    x = np.zeros((len(t), 2))
    for n in notes:
        f = mtof(n)
        for k, det in enumerate((-0.12, -0.06, 0, 0.05, 0.11)):
            v = saw(f * 2 ** (det / 12), t, (k * 0.37) % 1)
            pan = 0.5 + (k - 2) * 0.18
            x[:, 0] += v * (1 - pan)
            x[:, 1] += v * pan
    x = np.stack([lp(x[:, 0], cutoff), lp(x[:, 1], cutoff)], 1)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
    return x * env[:, None] * level * 0.045 / max(1, len(notes) / 3)


def bass(note, dur, level=1.0):
    t = t_(dur)
    f = mtof(note)
    x = saw(f, t) + 0.6 * np.sin(2 * np.pi * f * t)
    x = lp(x, 380, 4) * np.minimum(1, t * 300) * np.minimum(1, (dur - t) * 60)
    return np.tanh(x * 1.4) * 0.30 * level


def noise_riser(dur, level=1.0):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = int(0.05 * SR)
    for i in range(0, len(t), seg):  # sweeping band
        c = 400 * (18000 / 400) ** (i / len(t))
        out[i:i + seg] = bp(n[i:i + seg + 2000], c * 0.6, min(c * 1.4, 22000))[:len(out[i:i + seg])]
    tone = saw(110 * 2 ** (3 * t / dur), t) * 0.15
    return (out * 0.35 + lp(tone, 3000)) * (t / dur) ** 2 * level


# ---------------------------------------------------------------- arranger
music = np.zeros((int(DUR * SR) + SR, 2))
duck = np.ones(len(music))  # kick sidechain pump for pads/bass


def place(x, at, gain=1.0, pan=0.5):
    i = int(round(at * SR))
    if i >= len(music):
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos(pan * np.pi / 2), x * np.sin(pan * np.pi / 2)], 1) * 2 ** 0.5
    n = min(len(x), len(music) - i)
    music[i:i + n] += x[:n] * gain


pumped = np.zeros_like(music)


def place_pumped(x, at, gain=1.0):
    i = int(round(at * SR))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    n = min(len(x), len(pumped) - i)
    pumped[i:i + n] += x[:n] * gain


def mark_kick(at):
    i = int(round(at * SR))
    t = t_(BEAT)
    env = 1 - 0.75 * np.exp(-t * 9)
    n = min(len(env), len(duck) - i)
    duck[i:i + n] = np.minimum(duck[i:i + n], env[:n])


# chord progressions (MIDI). Bright: Am F C G (vi IV I V in C). Dark: Am F Dm E
BRIGHT = [(57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (55, [55, 59, 62, 67])]
DARK = [(45, [57, 60, 64]), (41, [57, 60, 65]), (50, [57, 62, 65]), (52, [56, 59, 64])]


def groove(start, end, prog, kick_on=True, clap_on=True, hats=True, arp=True, pad_on=True, bass_on=True, open_hat=True, lvl=1.0):
    bar = 4 * BEAT
    nbars = int(np.ceil((end - start) / bar))
    for b in range(nbars):
        t0 = start + b * bar
        root, chord = prog[b % len(prog)]
        if pad_on:
            place_pumped(pad([n + 12 for n in chord], min(bar, end - t0) + 0.05, cutoff=2600), t0, 0.9 * lvl)
        for s in range(16):  # 16th grid
            ts = t0 + s * BEAT / 4
            if ts >= end - 0.01:
                break
            if kick_on and s % 4 == 0:
                place(kick(), ts, 0.85 * lvl)
                mark_kick(ts)
            if clap_on and s in (4, 12):
                place(clap(), ts, 0.7 * lvl)
            if hats and s % 2 == 0:
                place(hat(level=0.9 if s % 4 == 2 else 0.5), ts, lvl)
            if open_hat and s % 4 == 2:
                place(hat(True, 0.6), ts, lvl)
            if bass_on and s % 2 == 0:
                place_pumped(bass(root - 12 + (12 if s % 4 == 2 else 0), BEAT / 2 * 0.9), ts, lvl)
            if arp:
                seq = [chord[i % len(chord)] + 12 * (i // len(chord) % 2) for i in (0, 1, 2, 3, 2, 1, 3, 4, 0, 2, 1, 3, 2, 4, 3, 1)]
                place(pluck(seq[s] + 12, level=0.75), ts, 0.8 * lvl, pan=0.3 if s % 2 else 0.7)


# S1 hook groove (lighter: no clap until the 2nd bar), S2 full groove
groove(0.0, 9.40, BRIGHT, clap_on=False, open_hat=False, lvl=0.95)
groove(9.40, 18.97, BRIGHT)
# S3 tension: clock ticks, dark pad, bass drone; build from 26.4
s3, s3e = 18.97, 29.83
bar = 4 * BEAT
for b in range(int(np.ceil((s3e - s3) / bar))):
    t0 = s3 + b * bar
    root, chord = DARK[b % 4]
    place(pad(chord, min(bar, s3e - t0) + 0.05, level=1.2, cutoff=1300), t0, 1.0)
    place(bass(root - 12, min(bar, s3e - t0) * 0.98, 0.8), t0, 1.0)
k = 0
t = s3
while t < s3e - 0.05:  # ticking clock: 8ths, accent on beats
    place(tick(1.0 if k % 2 == 0 else 0.55), t, 1.0)
    t += BEAT / 2
    k += 1
t = s3 + 4 * bar  # half-time heartbeat kick from bar 5
while t < 26.4:
    place(kick(0.8), t, 0.7)
    t += 2 * BEAT
# snare-roll build into the drop
t, step = 26.4, BEAT / 2
while t < s3e - 0.05:
    place(clap(0.35 + 0.65 * (t - 26.4) / (s3e - 26.4)), t, 0.6)
    t += step
    if t > 27.9:
        step = BEAT / 4
    if t > 29.0:
        step = BEAT / 8
place(noise_riser(3.4), s3e - 3.4, 0.9)
# S4 drop: full groove (with a clean break on the dashboard montage landing)
groove(29.83, 55.47, BRIGHT)
# S5 price: tight stab, then groove back without pad for punch
groove(55.72, 59.03, BRIGHT, pad_on=False, arp=True)
# S6 CTA
groove(59.03, 65.33, BRIGHT)
# S7 outro: sustained bright chord + one kick hit
place(kick(), 65.33, 1.0)
place(pad([69, 72, 76, 81], 4.1, level=1.6, cutoff=3200), 65.33, 1.0)
place(bass(45 - 12 + 12, 3.6, 0.9), 65.33, 1.0)
for i, n in enumerate([81, 84, 88, 93]):
    place(pluck(n, 0.9, 0.7, 6000), 65.33 + i * BEAT / 2, 0.8)

music += pumped * duck[:, None]
# simple stereo delay on everything for width
d = int(BEAT * 0.75 * SR)
wet = np.zeros_like(music)
wet[d:, 0] = music[:-d, 1] * 0.18
wet[d:, 1] = music[:-d, 0] * 0.18
music += wet
music = music[: int(DUR * SR)]
fade = np.ones(len(music))
fo = int(2.2 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
music *= fade[:, None]
music /= np.max(np.abs(music)) + 1e-9
write("audio/music.wav", music * 0.89)

# ---------------------------------------------------------------- extra SFX
# ka-ching: metallic bell partials + coin rattle
t = t_(1.3)
bell = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) * a for f, dcy, a in
           ((2093, 3.2, 0.5), (2637, 3.8, 0.35), (3136, 4.5, 0.3), (4186, 6, 0.2), (5274, 7, 0.12)))
bell[: int(0.09 * SR)] *= 0.0  # bell lands after the drawer clunk
bell = np.roll(bell, int(0.0 * SR))
clunk = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 40) * 0.6
coins = np.zeros(len(t))
for i in range(14):
    at = 0.1 + rng.random() * 0.45
    tt = t_(0.05)
    c = np.sin(2 * np.pi * (5000 + rng.random() * 3000) * tt) * np.exp(-tt * 120) * 0.25
    j = int(at * SR)
    coins[j:j + len(c)] += c
write("audio/kaching.wav", (bell + clunk + coins) * 0.8)

# typing: a burst of soft key clicks (2.4 s, irregular)
t = t_(2.4)
typing = np.zeros(len(t))
at = 0.0
while at < 2.3:
    tt = t_(0.035)
    k_ = bp(rng.standard_normal(len(tt)), 1500, 6000) * np.exp(-tt * 180) * (0.5 + 0.5 * rng.random())
    j = int(at * SR)
    typing[j:j + len(k_)] += k_
    at += 0.06 + rng.random() * 0.07
write("audio/typing.wav", typing * 0.7)

# bass drop / sub boom for the big reveal
t = t_(1.6)
f = 30 + 70 * np.exp(-t * 4)
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
write("audio/boom.wav", np.tanh(boom * 1.8) * 0.9)

# notification / send blip (two-tone)
t = t_(0.32)
blip = np.concatenate([np.sin(2 * np.pi * 1318 * t[: len(t) // 2]), np.sin(2 * np.pi * 1760 * t[len(t) // 2:])]) * np.exp(-((t % 0.16) * 18))
write("audio/blip.wav", blip * 0.5)

# reverse swell into the end card
t = t_(1.2)
sw = lp(rng.standard_normal(len(t)), 6000) * (t / 1.2) ** 3
write("audio/swell.wav", sw * 0.6)

# camera shutter-ish snap for the dashboard flash cuts
t = t_(0.12)
snap = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 60) * 0.6
snap[int(0.05 * SR):] += hp(rng.standard_normal(len(t) - int(0.05 * SR)), 3000) * np.exp(-t[: len(t) - int(0.05 * SR)] * 90) * 0.5
write("audio/snap.wav", snap)
print("ok")
