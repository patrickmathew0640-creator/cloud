# AI & jobs talking-head edit

Edits the raw Malayalam talking-head clip (2160x3840 HEVC, the picture letterboxed as a 2160x992 band) in the
style of the reference video "5 Skills You Must Learn in 2026":

- 1920x1080 landscape @ 30 fps, cropped from the letterboxed band
- pauses tightened (silences ≥ 0.4 s cut, short breath kept), framing alternating wide / 1.15× punch-in
- light grade (the raw is over-exposed and warm)
- English subtitles: Segoe-style semibold white on a translucent dark box, bottom centre
- opening title (yellow tag + two-line bold title), "PART n" section titles, lower-left info card,
  top-right callout cards with a kicker tag + emoji, like/subscribe/bell click animation (×2),
  blurred freeze-frame "Thanks for watching!" end card
- cleaned voice (-16 LUFS) over a soft ducked music bed

Font: [Selawik](https://github.com/microsoft/Selawik) (SIL OFL 1.1), metric-compatible with Segoe UI, which the
reference uses. Music: "Wallpaper" by Kevin MacLeod (incompetech.com), CC BY 4.0, from `../edit2/audio/`.

## Files

- `edit.py`: every edit decision: kept ranges, framing splits, subtitles, graphics, timings (source timeline)
- `graphics.py`: renders each graphic as a transparent PNG with headless Chromium (Playwright)
- `render.py`: crop → per-segment cut/zoom/grade → overlays → audio mix → mux

## Render

```sh
pip install playwright pillow
python3 render.py raw.mp4 out.mp4 --work build          # full render
python3 render.py raw.mp4 out.mp4 --work build --reuse-cut   # graphics/subtitle changes only
RENDER_SCALE=2 python3 render.py raw.mp4 out_4k.mp4 --work build4k   # 3840x2160 (graphics drawn at 4K)
```

Outputs: `../deliverables/ai-jobs-edit-1080p.mp4`, `../deliverables/ai-jobs-edit-4k.mp4`.
The 4K video is scaled up from the source's 2160x992 picture band, so the footage is softer than the text.

## Video 2 (Tamil)

`edit_v2.py` holds the decisions for the second clip (Tamil voice-over, 2160x1200 letterboxed picture):

```sh
EDIT=edit_v2 python3 render.py raw2.mp4 out2.mp4 --work build2
```

Output: `../deliverables/ai-skills-tamil-edit-1080p.mp4`.
