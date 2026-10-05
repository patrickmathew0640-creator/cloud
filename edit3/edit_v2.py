"""Edit decisions for video 2: "Don't fear AI – use it" talking head (Tamil VO, English subtitles).

Render with: EDIT=edit_v2 python3 render.py raw2.mp4 out.mp4 --work build2
Every time below is on the SOURCE timeline (raw clip, 143.23 s).
"""
from edit import END_CARD, END_TEXT, GRADE, MUSIC, MUSIC_VOL, PUNCH, MIN_HOLD  # noqa: F401  same look as video 1

CROP = "crop=2126:1196:17:1322"     # 16:9 window inside this clip's 2160x1200 letterboxed picture

# ---------------------------------------------------------------- cut list
KEEP = [
    (0.76, 22.40), (23.16, 35.28), (36.01, 38.75), (38.91, 46.04), (46.73, 79.18), (79.34, 83.97),
    (84.19, 100.82), (101.13, 108.33), (108.50, 111.19), (111.51, 115.38), (115.53, 118.03),
    (118.40, 126.88), (127.10, 136.15), (136.55, 142.41), (142.63, 143.15),
]
SPLITS = [7.48, 16.10, 25.70, 29.50, 42.98, 52.05, 57.75, 62.10, 65.70, 70.35, 75.50, 92.00, 96.85,
          104.10, 113.76, 122.58, 131.10]


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
ZOOM_CENTER = (1040, 500)

# ---------------------------------------------------------------- subtitles (start, end, text)
CAPTIONS = [
    (0.56, 2.32, "Hello everyone, welcome back to the channel!"),
    (2.32, 4.90, "Many of you might be wondering –"),
    (4.90, 7.48, "if you don't know AI, will you get a job in the future?"),
    (7.48, 11.00, "Someone who knows how to use AI"),
    (11.00, 16.00, "can finish their work very quickly and smartly."),
    (16.14, 17.66, "Let's look at a simple example."),
    (18.50, 21.54, "Imagine someone takes 2 hours to prepare a report."),
    (22.60, 25.70, "But another person knows how to use AI tools."),
    (25.70, 29.50, "They organise the data, create a summary,"),
    (29.50, 35.00, "get ideas with AI, and finish the task in 30 to 40 minutes."),
    (35.64, 37.72, "Here, AI didn't take their job."),
    (38.50, 42.98, "Because they knew how to use AI, they became more productive."),
    (42.98, 46.08, "That's what has really changed."),
    (46.24, 49.92, "So the question we should ask in the future isn't"),
    (50.10, 51.52, "“Will AI replace me?”"),
    (52.12, 56.74, "but “Can someone using AI do this job better than me?”"),
    (57.80, 62.06, "Content creation, marketing, coding, data analysis, customer support –"),
    (62.16, 65.16, "we see AI tools in so many fields."),
    (65.16, 67.16, "We're seeing it with our own eyes."),
    (67.16, 70.30, "Don't you see how productive they're making people?"),
    (70.38, 74.74, "But I'm not telling you to learn 100 AI tools"),
    (75.54, 79.00, "or to memorise them all."),
    (79.62, 82.86, "First, look at your own work."),
    (83.46, 86.16, "What repetitive tasks do you do every day?"),
    (86.30, 88.18, "Do you write emails? Do research?"),
    (88.54, 90.36, "Analyse data? Make presentations?"),
    (91.10, 92.00, "Or create content?"),
    (92.00, 96.86, "In that work, learn where you can use AI."),
    (96.86, 100.60, "That's the main thing you need to learn."),
    (100.70, 103.80, "So don't be afraid of AI."),
    (104.16, 105.96, "Don't see it as your competitor –"),
    (107.82, 109.84, "see it as your assistant."),
    (110.86, 113.76, "Your existing skills + AI skills –"),
    (113.76, 117.82, "this combination will make you even more powerful in the future."),
    (117.82, 122.50, "Some companies say they don't need as many employees because they use AI –"),
    (122.60, 124.60, "we hear a lot of news like that."),
    (124.78, 128.92, "But on the other side, human effort is still needed."),
    (131.16, 135.68, "So whatever happens, learning AI is very important for us."),
    (137.06, 139.40, "For more career, technology and skill videos,"),
    (139.40, 141.08, "subscribe to the channel!"),
    (142.28, 143.04, "Thank you!"),
]

# ---------------------------------------------------------------- graphics
TITLE = ("AI & CAREERS", "Don't Fear AI,", "Use It!", 0.60, 5.00)
INFO = [("2 Hours vs 30 Minutes", "Same report – with and without AI", 18.50, 22.40)]
SECTIONS = [
    ("PART 1", "The Truth", 7.48, 10.50),
    ("PART 2", "A Simple Example", 16.14, 18.40),
    ("PART 3", "The Real Question", 46.24, 49.50),
    ("PART 4", "What To Learn", 79.62, 82.80),
    ("PART 5", "AI = Your Assistant", 100.70, 103.70),
    ("PART 6", "The Reality", 117.82, 120.90),
]
CALLOUTS = [   # (kicker, emoji, text, start, end) – top-right card
    ("WITH AI", "⚡", "Organise data → Summary → Ideas", 25.70, 34.90),
    ("KEY POINT", "🤝", "AI didn't take the job – it boosted it", 35.64, 42.90),
    ("ASK YOURSELF", "🤔", "Can someone using AI do it better?", 52.12, 56.74),
    ("EXAMPLE", "💼", "Content • Marketing • Coding • Data • Support", 57.80, 65.00),
    ("MYTH", "🚫", "No need to memorise 100 AI tools", 70.38, 79.00),
    ("STEP 1", "🔁", "Spot your daily repetitive tasks", 83.46, 86.20),
    ("YOUR TASKS", "📋", "Emails • Research • Data • Slides • Content", 86.30, 92.00),
    ("STEP 2", "🎯", "Learn where AI fits into that work", 92.00, 96.80),
    ("MINDSET", "🤖", "AI = your assistant, not a competitor", 104.16, 110.00),
    ("FORMULA", "➕", "Your skills + AI skills = Power", 110.86, 117.60),
    ("REALITY", "🧠", "Human effort is still needed", 124.78, 129.00),
    ("BOTTOM LINE", "🚀", "Learning AI is very important", 131.16, 135.70),
]
SUBSCRIBE = [11.50, 138.80]
