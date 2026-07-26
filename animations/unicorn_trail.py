"""A unicorn trots left to right leaving a trail of rainbow poop nuggets,
holds on the finished trail, fades to black, then a title card
scrolls by with text.

The unicorn is a literal bitmap (UNICORN_BITMAP below), transcribed cell
for cell. The legs are a fixed pose as a consequence.

The title text is drawn one character at a time so each can carry its own
color.

Run standalone:
    python -m animations.unicorn_trail
"""

from pathlib import Path

from daemon.matrix import graphics

from animations.drawing import dim, draw_stink_line, set_pixel
from animations.text import centered_y, load_font, text_pixel_width

FRAME_DELAY = 0.05
# Every phase below has a natural end, but the full sequence runs longer
# than the daemon's default DURATION cap -- set explicitly so it isn't
# cut short before reaching that natural end.
DURATION = 25

FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
FONT = load_font(FONT_PATH)

# --- title scroll ---------------------------------------------

TEXT_SCROLL_STEP = 1

OTHER_COLOR = graphics.Color(200, 200, 200)  # plain, easy-to-read gray

RED = graphics.Color(220, 30, 30)
ORANGE = graphics.Color(230, 120, 20)
YELLOW = graphics.Color(220, 200, 20)
GREEN = graphics.Color(40, 170, 60)
BLUE = graphics.Color(40, 90, 220)
PURPLE = graphics.Color(150, 50, 200)
# Shared with the poop trail below -- same sequence, same word "rainbow".
RAINBOW_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

BROWN = graphics.Color(120, 80, 40)
SICK_GREEN = graphics.Color(90, 120, 45)
MUSTARD = graphics.Color(170, 150, 30)
OLIVE = graphics.Color(110, 110, 30)
STINKY_COLORS = [BROWN, SICK_GREEN, MUSTARD, OLIVE]

# (word, palette) -- a word cycles its palette one color per letter; a
# plain string is just OTHER_COLOR throughout.
PHRASE_WORDS = [
    "Follow",
    "the",
    RAINBOW_COLORS,
    "to",
    STINKY_COLORS,
    STINKY_COLORS,
]
# The two special words' own text, since a palette alone doesn't carry it.
_RAINBOW_TEXT = "Rainbow"
_STINKY_TEXT = ["Stinky", "Springs"]


def _build_phrase():
    """Precompute (char, color) pairs for the whole title once, so `run`
    doesn't redo word-splitting and palette-cycling every frame."""
    chars = []
    stinky_word_index = 0
    for word in PHRASE_WORDS:
        if word is RAINBOW_COLORS:
            text, palette = _RAINBOW_TEXT, RAINBOW_COLORS
        elif word is STINKY_COLORS:
            text, palette = _STINKY_TEXT[stinky_word_index], STINKY_COLORS
            stinky_word_index += 1
        else:
            text, palette = word, None

        for i, ch in enumerate(text):
            chars.append((ch, palette[i % len(palette)] if palette else OTHER_COLOR))
        chars.append((" ", OTHER_COLOR))

    chars.pop()  # drop the trailing space after the last word
    return chars


PHRASE_CHARS = _build_phrase()
PHRASE_WIDTH = text_pixel_width(FONT, "".join(ch for ch, _ in PHRASE_CHARS))


def _draw_phrase(canvas, x, y):
    cx = x
    for ch, color in PHRASE_CHARS:
        cx += graphics.DrawText(canvas, FONT, cx, y, color, ch)


# --- unicorn + poop trail ---------------------------------------

WALK_STEP = 1

UNICORN_WIDTH = 22
UNICORN_HEIGHT = 22

# One row per bitmap row, one character per column. "." is transparent;
# every other character keys into UNICORN_COLORS.
UNICORN_BITMAP = [
    "....................._",
    "...................._.",
    "...............BAA.__.",
    ".............FEEDG__..",
    "............BEHHHHHHG.",
    "...........BEHHHHHHHHG",
    "...........BEHHHHGGGHG",
    "...........BIHHHHG.GG.",
    "..........BBBHHHHG....",
    "..FB..GGGGBBAHHHHG....",
    ".FIIBGHHHHEHHHHHHG....",
    "BEB.GHHHHHHHHHHHHG....",
    "BFB.GHHHHHHHHHHHHG....",
    "BFB.GHHHHHHHHHHHHG....",
    "BAJ.GHHHHHHHHHHHG.....",
    "DAJ..GHHGGGGGGHHG.....",
    "AAE..GHG......GHG.....",
    "BA...GHG......GHG.....",
    "B....GHG......GHG.....",
    ".....GHG......GHG.....",
    "....._K_......_K_.....",
    ".....___......___.....",
]
UNICORN_COLORS = {
    "_": graphics.Color(255, 166, 77),  # #FFA64D Light Orange
    "A": graphics.Color(191, 64, 166),  # #BF40A6 Muted Magenta
    "B": graphics.Color(210, 121, 189),  # #D279BD Light Muted Rose
    "D": graphics.Color(166, 64, 191),  # #A640BF Muted Magenta
    "E": graphics.Color(230, 179, 196),  # #E6B3C4 Very Light Muted Red
    "F": graphics.Color(210, 121, 165),  # #D279A5 Light Muted Rose
    "G": graphics.Color(64, 107, 191),  # #406BBF Muted Blue
    "H": graphics.Color(238, 238, 238),  # #EEEEEE Off White
    "I": graphics.Color(255, 153, 202),  # #FF99CA Very Light Rose
    "J": graphics.Color(210, 121, 202),  # #D279CA Light Muted Magenta
    "K": graphics.Color(255, 204, 153),  # #FFCC99 Very Light Orange
}
# Nuggets drop from about here -- roughly where the tail is -- so they
# appear to come from behind the unicorn as it walks.
TAIL_LOCAL_X = 2

# Narrow point tapering to a wide base, bottom corners rounded off so it
# doesn't read as a bare triangle.
NUGGET_WIDTH, NUGGET_HEIGHT = 7, 8
NUGGET_SHAPE = [
    "...#...",
    "..###..",
    "..###..",
    ".#####.",
    ".#####.",
    "#######",
    "#######",
    ".#####.",
]
# A few pixels apart -- close enough to read as a continuous trail, wide
# enough that individual nuggets stay distinct.
DEPOSIT_INTERVAL = 9

STINK_COLOR = graphics.Color(140, 190, 60)  # sickly green
STINK_RISE_HEIGHT = 6
FRAMES_PER_ROW = 4


def _draw_unicorn(canvas, x, ground_y):
    top = ground_y - UNICORN_HEIGHT
    for row, line in enumerate(UNICORN_BITMAP):
        for col, ch in enumerate(line):
            if ch != ".":
                set_pixel(canvas, x + col, top + row, UNICORN_COLORS[ch])


def _draw_nugget(canvas, x, ground_y, color):
    top = ground_y - NUGGET_HEIGHT
    for row, line in enumerate(NUGGET_SHAPE):
        for col, ch in enumerate(line):
            if ch == "#":
                set_pixel(canvas, x + col, top + row, color)


# --- hold animation, then fade ----------------------------------------

HOLD_FRAMES = 30
FADE_FRAMES = 20


def _draw_trail(canvas, trail, ground_y, tick, brightness=1.0):
    stink_top = ground_y - NUGGET_HEIGHT
    for i, (nugget_x, color) in enumerate(trail):
        _draw_nugget(canvas, nugget_x, ground_y, dim(color, brightness))
        draw_stink_line(
            canvas, nugget_x + NUGGET_WIDTH // 2, stink_top, tick, i * 3,
            STINK_COLOR, STINK_RISE_HEIGHT, FRAMES_PER_ROW, brightness,
        )


def run(canvas, width, height):
    # Phase 1: unicorn walks left to right, dropping a rainbow trail.
    ground_y = height
    trail = []
    color_index = 0
    last_deposit_x = None
    tick = 0

    x = -UNICORN_WIDTH
    while x < width:
        canvas.Clear()
        _draw_trail(canvas, trail, ground_y, tick)
        _draw_unicorn(canvas, x, ground_y)
        canvas = yield canvas
        tick += 1

        x += WALK_STEP
        tail_x = x + TAIL_LOCAL_X
        in_bounds = 0 <= tail_x <= width - NUGGET_WIDTH
        due = last_deposit_x is None or tail_x - last_deposit_x >= DEPOSIT_INTERVAL
        if in_bounds and due:
            trail.append((tail_x, RAINBOW_COLORS[color_index % len(RAINBOW_COLORS)]))
            color_index += 1
            last_deposit_x = tail_x

    # Phase 2: hold on the finished trail.
    for _ in range(HOLD_FRAMES):
        canvas.Clear()
        _draw_trail(canvas, trail, ground_y, tick)
        canvas = yield canvas
        tick += 1

    # Phase 3: fade the trail (and its stink) to black.
    for frame in range(FADE_FRAMES + 1):
        brightness = 1.0 - frame / FADE_FRAMES
        canvas.Clear()
        _draw_trail(canvas, trail, ground_y, tick, brightness)
        canvas = yield canvas
        tick += 1

    # Phase 4: title card scrolls right to left across the whole panel.
    y = centered_y(FONT, height)
    x = width
    while x > -PHRASE_WIDTH:
        canvas.Clear()
        _draw_phrase(canvas, x, y)
        canvas = yield canvas
        x -= TEXT_SCROLL_STEP


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
