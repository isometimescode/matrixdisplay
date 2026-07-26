"""Stinky pool: an oval pond off to one side, with looping smell lines
rising and fading above it, and text as static sign on the other side.

Run standalone:
    python -m animations.stinky_pool
"""

from pathlib import Path

from daemon.matrix import graphics

from animations.drawing import draw_stink_line, set_pixel
from animations.text import load_font, text_pixel_width

FRAME_DELAY = 0.05
# No natural end -- the smell lines loop forever, so the daemon needs a cap.
DURATION = 10

WATER_COLOR = graphics.Color(40, 90, 70)  # murky blue-green
MUCK_COLOR = graphics.Color(70, 75, 35)  # brown-green, for texture
STINK_COLOR = graphics.Color(140, 190, 60)  # sickly green
TEXT_COLOR = graphics.Color(215, 205, 165)  # parchment/sign-ish cream

# Oval pond, bottom-left, cropped to its top cap -- the lower half is
# pushed off the bottom edge (see _draw_pool). HIDDEN_HEIGHT shapes the
# curve: bigger gives a flatter arc, smaller a curve closer to the
# oval's full-width equator.
POOL_X = 1
POOL_WIDTH = 26
POOL_VISIBLE_HEIGHT = 7
POOL_HIDDEN_HEIGHT = 13

NUM_STINK_LINES = 3
# How many rows above the pool a stink line climbs before looping back to
# the water's surface to rise again.
STINK_RISE_HEIGHT = 20
FRAMES_PER_ROW = 4

TEXT_LINES = ["Stinky", "Springs", "Pop: 14"]
FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
FONT = load_font(FONT_PATH)


def _draw_pool(canvas, height):
    pool_y = height - POOL_VISIBLE_HEIGHT
    cx = POOL_X + POOL_WIDTH / 2
    rx = POOL_WIDTH / 2
    ry = (POOL_VISIBLE_HEIGHT + POOL_HIDDEN_HEIGHT) / 2
    # Push the true center below the bottom edge by POOL_HIDDEN_HEIGHT, so
    # only the oval's top cap ever falls within the rows we draw.
    cy = pool_y + ry

    for y in range(pool_y, height):
        for x in range(POOL_X, POOL_X + POOL_WIDTH):
            nx = (x + 0.5 - cx) / rx
            ny = (y + 0.5 - cy) / ry
            if nx * nx + ny * ny > 1:
                continue  # outside the oval

            # Dither between water and muck colors for a murky texture
            # instead of a flat fill.
            color = MUCK_COLOR if (x + y) % 3 == 0 else WATER_COLOR
            set_pixel(canvas, x, y, color)

    return pool_y


def _draw_text(canvas, width, height):
    text_area_x = POOL_X + POOL_WIDTH + 1
    text_area_width = width - text_area_x - 1

    line_height = FONT.height + 2
    block_height = line_height * len(TEXT_LINES)
    top = (height - block_height) // 2

    for i, line in enumerate(TEXT_LINES):
        line_width = text_pixel_width(FONT, line)
        x = text_area_x + max(0, (text_area_width - line_width) // 2)
        y = top + i * line_height + FONT.baseline
        graphics.DrawText(canvas, FONT, x, y, TEXT_COLOR, line)


def run(canvas, width, height):
    tick = 0
    line_spacing = POOL_WIDTH // (NUM_STINK_LINES + 1)
    cycle = STINK_RISE_HEIGHT * FRAMES_PER_ROW

    while True:
        canvas.Clear()
        pool_y = _draw_pool(canvas, height)

        for i in range(NUM_STINK_LINES):
            x_base = POOL_X + line_spacing * (i + 1)
            phase_offset = i * (cycle // NUM_STINK_LINES)
            draw_stink_line(
                canvas, x_base, pool_y, tick, phase_offset,
                STINK_COLOR, STINK_RISE_HEIGHT, FRAMES_PER_ROW,
            )

        _draw_text(canvas, width, height)

        canvas = yield canvas
        tick += 1


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
