"""A simplified pixel-art version of the Camp EKKO logo: the three stripe
colors, plus "CAMP EKKO" and "2026" in blocky text. No mountain silhouette
or script text -- neither holds up at this resolution.

The text stays put -- both lines fit the panel's width on their own, so
there's no need to scroll them. The stripes get a shimmer instead: a
brightness wave sweeps across the color band so the badge still feels
alive without the text ever going half off-screen.

Run standalone with the emulator (no hardware, no daemon needed):
    python -m animations.camp_logo
"""

import math
from pathlib import Path

from RGBMatrixEmulator import graphics

from animations.text import load_font, text_pixel_width

FRAME_DELAY = 0.05
# No natural end -- the shimmer loops forever, so the daemon needs a cap.
DURATION = 10

TITLE_TEXT = "CAMP EKKO"
YEAR_TEXT = "2026"
# The logo's black text only works on its white background -- inverted to
# off-white here so it reads against the panel's black background instead.
TITLE_COLOR = graphics.Color(230, 225, 215)

RUST = graphics.Color(180, 75, 50)
TEAL = graphics.Color(20, 130, 140)
GOLD = graphics.Color(240, 165, 25)
STRIPE_COLORS = [RUST, TEAL, GOLD]
STRIPE_HEIGHT = 2
STRIPE_WIDTH = 48

# A brightness wave sweeps sideways across the stripes, column by column,
# rather than the stripes themselves moving -- text stays put and readable
# while the color band still feels alive.
SHIMMER_WAVELENGTH = 14  # pixels per light/dark cycle
SHIMMER_SPEED = 0.5  # pixels the wave travels per frame
SHIMMER_MIN_BRIGHTNESS = 0.35  # never dims all the way to black

FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
FONT = load_font(FONT_PATH)


def _draw_stripes(canvas, stripe_x, stripes_top, tick):
    for i, color in enumerate(STRIPE_COLORS):
        for row in range(STRIPE_HEIGHT):
            y = stripes_top + i * STRIPE_HEIGHT + row
            for col in range(STRIPE_WIDTH):
                phase = (col + tick * SHIMMER_SPEED) * (
                    2 * math.pi / SHIMMER_WAVELENGTH
                )
                brightness = SHIMMER_MIN_BRIGHTNESS + (
                    1 - SHIMMER_MIN_BRIGHTNESS
                ) * (0.5 * (1 + math.sin(phase)))
                canvas.SetPixel(
                    stripe_x + col,
                    y,
                    round(color.red * brightness),
                    round(color.green * brightness),
                    round(color.blue * brightness),
                )


def run(canvas, width, height):
    title_width = text_pixel_width(FONT, TITLE_TEXT)
    year_width = text_pixel_width(FONT, YEAR_TEXT)
    stripes_height = STRIPE_HEIGHT * len(STRIPE_COLORS)

    title_x = (width - title_width) // 2
    year_x = (width - year_width) // 2
    stripe_x = (width - STRIPE_WIDTH) // 2

    # Three rows stacked top to bottom -- title, stripes, year -- centered
    # as one block, with a 1px gap on either side of the stripe band.
    block_height = FONT.height + 1 + stripes_height + 1 + FONT.height
    top = (height - block_height) // 2

    title_y = top + FONT.baseline
    stripes_top = top + FONT.height + 1
    year_top = stripes_top + stripes_height + 1
    year_y = year_top + FONT.baseline

    tick = 0
    while True:
        canvas.Clear()
        graphics.DrawText(canvas, FONT, title_x, title_y, TITLE_COLOR, TITLE_TEXT)
        _draw_stripes(canvas, stripe_x, stripes_top, tick)
        graphics.DrawText(canvas, FONT, year_x, year_y, TITLE_COLOR, YEAR_TEXT)

        canvas = yield canvas
        tick += 1


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
