"""Edit decisions for the "Will AI take your job?" talking-head video (Malayalam VO, English subtitles).

Every time below is on the SOURCE timeline (raw clip, 149.48 s). render.py remaps them onto the cut.
"""

# ---------------------------------------------------------------- cut list
# Speech kept between pauses (silence <= -35 dB for >= 0.4 s detected, 0.12 s / 0.15 s breath left either side).
KEEP = [
    (0.00, 18.92), (19.12, 21.41), (22.32, 24.13), (24.45, 28.76), (29.21, 30.65), (31.14, 34.20),
    (34.48, 50.46), (51.38, 54.37), (55.04, 58.65), (58.94, 61.76), (61.98, 66.27), (67.48, 81.26),
    (81.53, 82.31), (82.69, 85.23), (85.40, 94.65), (95.56, 103.03), (103.21, 107.52), (107.78, 121.13),
    (121.58, 130.28), (130.87, 131.48), (131.76, 134.50), (134.75, 142.93), (143.36, 144.46),
    (144.72, 145.87), (146.06, 149.40),
]
# Sentence boundaries inside continuous takes where the framing jumps (wide <-> punch-in), as in the reference.
SPLITS = [4.98, 8.25, 13.70, 42.70, 70.65, 73.80, 78.55, 89.80, 98.05, 111.40, 115.30, 117.62, 124.10, 127.25, 138.70]
PUNCH = 1.15          # punch-in scale
MIN_HOLD = 3.0        # don't change framing more often than this


def _segments():
    pieces = []
    for s, e in KEEP:
        cuts = [s] + [x for x in SPLITS if s < x < e] + [e]
        pieces += list(zip(cuts[:-1], cuts[1:]))
    out, z, held = [], PUNCH, MIN_HOLD
    for s, e in pieces:
        if held >= MIN_HOLD:
            z, held = (1.0 if z == PUNCH else PUNCH), 0.0
        out.append((s, e, z))
        held += e - s
    return out


SEGMENTS = _segments()
ZOOM_CENTER = (1090, 470)        # punch-in centre on the 1920x1080 base frame (speaker's face, upper third)
# the raw is over-exposed and warm: pull mids/highlights down, cool it slightly, light sharpen
GRADE = ("curves=all='0/0 0.25/0.19 0.5/0.42 0.75/0.70 1/0.96',"
         "colorbalance=rm=-0.05:gm=-0.01:bm=0.04:rh=-0.03:bh=0.02,eq=saturation=1.05:contrast=1.04,unsharp=5:5:0.3")

# ---------------------------------------------------------------- subtitles (start, end, text)
CAPTIONS = [
    (0.02, 2.04, "Hello everyone, welcome back to the channel!"),
    (2.04, 4.95, "Will people who don't know AI lose out on jobs in the future?"),
    (5.08, 7.86, "Many people are asking this question right now."),
    (8.34, 10.70, "But the truth is, not knowing AI"),
    (10.70, 13.10, "won't cost you your job right away."),
    (13.82, 17.00, "But someone who knows how to use AI"),
    (17.00, 20.50, "can do that same job faster and much smarter."),
    (21.66, 23.70, "Let me give you a simple example."),
    (24.08, 27.26, "Say one person takes 2 hours to prepare a report."),
    (28.52, 30.50, "Another person does the same job,"),
    (31.26, 34.05, "but they know how to use AI tools."),
    (34.60, 38.00, "They automate the data, make a summary,"),
    (38.00, 42.04, "get ideas using AI, and finish it in just 30–40 minutes."),
    (43.20, 45.50, "Here, AI isn't taking their job –"),
    (45.50, 49.10, "knowing how to use AI is making them more productive."),
    (50.98, 53.18, "So what's really changing here?"),
    (54.36, 58.50, "In the future, the question isn't just"),
    (59.06, 60.66, "“Will AI replace me?”"),
    (61.50, 66.10, "It's “Will someone using AI do a better job than me?”"),
    (67.06, 70.60, "Whether it's content creation, marketing,"),
    (70.60, 73.62, "coding, data analysis or customer support,"),
    (73.92, 77.38, "AI tools are making people far more productive."),
    (78.68, 80.84, "You can see it in your own day-to-day life."),
    (80.84, 82.20, "So what should we learn?"),
    (82.80, 86.24, "One important thing."),
    (86.72, 92.50, "Learning AI doesn't mean memorising the names of 100 AI tools."),
    (92.52, 94.08, "First, think about your own job."),
    (94.96, 98.06, "Think about the repetitive tasks you do every day."),
    (98.06, 99.70, "Look at what they are –"),
    (99.78, 102.14, "writing emails, doing research,"),
    (102.76, 107.10, "analysing data, creating presentations,"),
    (107.24, 111.30, "or creating content."),
    (111.50, 115.06, "First, learn where you can use AI in those tasks."),
    (115.38, 117.62, "But sometimes we hear news about AI"),
    (117.62, 120.90, "and about employees being laid off because of it."),
    (121.22, 124.04, "Actually, some companies are doing that."),
    (124.18, 127.20, "But they can't rely on AI all the time –"),
    (127.20, 130.10, "even now, human effort still has to go into it."),
    (130.96, 134.30, "So whatever it is, learning AI"),
    (134.30, 137.50, "and AI tools has become really important."),
    (138.80, 141.90, "For more videos on technology, careers and skills,"),
    (141.90, 144.16, "please subscribe to my channel."),
    (145.62, 147.70, "If you liked this video, please like and comment."),
    (147.70, 149.32, "Thank you!"),
]

# ---------------------------------------------------------------- graphics
TITLE = ("AI & CAREERS", "Will AI Take", "Your Job?", 0.30, 4.90)
INFO = [("2 Hours vs 30 Minutes", "Same report – with and without AI", 24.40, 28.70)]
SECTIONS = [
    ("PART 1", "The Truth", 8.34, 11.40),
    ("PART 2", "A Simple Example", 21.60, 24.10),
    ("PART 3", "The Real Question", 50.98, 53.90),
    ("PART 4", "What To Learn", 80.84, 84.40),
    ("PART 5", "AI & Layoffs", 115.38, 118.40),
]
CALLOUTS = [   # (kicker, emoji, text, start, end) – top-right card
    ("WITH AI", "⚡", "Automate data → Summary → Ideas", 34.60, 41.80),
    ("KEY POINT", "🤝", "AI doesn't take your job – it boosts you", 43.20, 49.10),
    ("ASK YOURSELF", "🤔", "Will someone using AI beat me?", 61.50, 66.10),
    ("EXAMPLE", "💼", "Content • Marketing • Coding • Data • Support", 67.10, 73.60),
    ("MYTH", "🚫", "Learning AI ≠ memorising 100 tool names", 86.72, 92.50),
    ("STEP 1", "🔁", "List your daily repetitive tasks", 94.96, 98.90),
    ("YOUR TASKS", "📋", "Emails • Research • Data • Slides • Content", 99.78, 111.20),
    ("STEP 2", "🎯", "Find where AI fits into those tasks", 111.50, 115.10),
    ("REALITY", "🧠", "AI still needs human effort", 124.18, 130.10),
    ("BOTTOM LINE", "🚀", "Learning AI tools is now essential", 130.96, 137.50),
]
SUBSCRIBE = [14.00, 141.40]      # like / subscribe / bell + cursor click animation (4.6 s each)
END_TEXT = ("Thanks for watching!", "Subscribe for more tech, career & skill videos")
END_CARD = 4.0                   # seconds of blurred freeze-frame end card

# ---------------------------------------------------------------- audio
MUSIC = "Wallpaper.mp3"          # "Wallpaper" by Kevin MacLeod (incompetech.com), CC BY 4.0
MUSIC_VOL = 0.11                 # soft bed under the voice, as in the reference

# ---------------------------------------------------------------- Shorts (EDIT=edit python3 shorts.py ...)
VCROP = "crop=558:992:921:1424"       # 9:16 window on the speaker inside the 2160x992 picture band
VZOOM_CENTER = (540, 720)
SHORTS = [   # name, source windows, hook (tag, line 1, line 2)
    ("ml-short1-will-ai-take-your-job", [(2.04, 20.50)], ("AI & JOBS", "Will AI Take", "Your Job?")),
    ("ml-short2-2hours-vs-30min", [(21.66, 49.10)], ("AI AT WORK", "Same Job:", "2 Hours vs 30 Min")),
    ("ml-short3-the-real-question", [(50.98, 80.84)], ("THE REAL QUESTION", "Will AI", "Replace You?")),
    ("ml-short4-what-to-learn", [(80.84, 115.06)], ("HOW TO START", "Don't Memorise", "100 AI Tools!")),
]
