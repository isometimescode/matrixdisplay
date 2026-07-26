"""Horizontal scrolling text, right to left across the panel.

Run standalone:
    python -m animations.scroll_horizontal
"""

from pathlib import Path

from daemon.matrix import graphics

from animations.text import centered_y, load_font, text_pixel_width

FRAME_DELAY = 0.06
TEXT = "Camp EKKO 2026"
TEXT_COLOR = graphics.Color(255, 140, 0)
FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
FONT = load_font(FONT_PATH)


def run(canvas, width, height):
    text_width = text_pixel_width(FONT, TEXT)
    y = centered_y(FONT, height)

    # Starts just off the right edge, ends just off the left -- DrawText
    # clips anything outside 0..width.
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
