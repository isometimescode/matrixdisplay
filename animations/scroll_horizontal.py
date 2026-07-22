"""Horizontal scrolling text, right to left across the panel.

Text is drawn with a BDF bitmap font via the `graphics` module rather than
PIL -- see animations/text.py for why (short version: no anti-aliasing
blur at these tiny sizes). DrawText clips automatically, so scrolling is
just "draw the text starting further left each frame."

Run standalone with the emulator (no hardware, no daemon needed):
    python -m animations.scroll_horizontal
"""

from pathlib import Path

from daemon.matrix import graphics

from animations.text import centered_y, load_font, text_pixel_width

FRAME_DELAY = 0.06
TEXT = "Camp EKKO 2026"
TEXT_COLOR = graphics.Color(255, 140, 0)
FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
# Loaded once at import time, not per-play -- parsing the BDF file on every
# single cycle through the sequence would be wasted work repeated forever.
FONT = load_font(FONT_PATH)


def run(canvas, width, height):
    text_width = text_pixel_width(FONT, TEXT)
    y = centered_y(FONT, height)

    # Start with the text just off the right edge, end with it just off
    # the left edge -- DrawText clips whatever's outside 0..width for us.
    x = width
    while x > -text_width:
        canvas.Clear()
        graphics.DrawText(canvas, FONT, x, y, TEXT_COLOR, TEXT)
        canvas = yield canvas

        x -= 1


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
