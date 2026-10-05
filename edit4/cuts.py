# (src_start, src_end) kept from source/input.mp4, in order. Output time is the running sum.
SEGS = [(3.0, 12.7667), (13.3, 20.4667), (20.55, 26.2167), (26.45, 29.65), (30.05, 84.5167)]  # ends snapped to the encoded 30fps segment lengths
def src2out(t):
    o = 0.0
    for s, e in SEGS:
        if s <= t <= e + 0.05:
            return round(o + t - s, 3)
        o += e - s
    raise ValueError(t)
CUT_TIMES = []
_o = 0.0
for s, e in SEGS:
    _o += e - s; CUT_TIMES.append(round(_o, 3))
SPK_DUR = CUT_TIMES[-1]
