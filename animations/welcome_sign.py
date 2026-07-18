"""Welcome sign: "Welcome to Stinky Springs" text, pre-rendered once at its
native size and then blitted back with nearest-neighbor scaling at a
growing fraction of that size each frame -- it reads as the sign growing
into view, staying crisp at every size since it's never re-rendered at a
different resolution. Holds briefly at full size before finishing.

Split out of rv_arrival.py, where it was originally the final phase of the
RV drive-by -- the effect didn't read the way that animation called for,
so it lives here to reconsider on its own (e.g. paired with rv_arrival in
the daemon's queue, or standalone).

Run standalone with the emulator (no hardware, no daemon needed):
    python -m animations.welcome_sign
"""

from pathlib import Path

from RGBMatrixEmulator import graphics

from animations.text import load_font, text_pixel_width

FRAME_DELAY = 0.09
# No DURATION set -- finishes on its own once the hold period ends.

# Split across three short lines rather than "Stinky Springs" on one line
# -- at this font size that line alone is wider than the panel.
TEXT_LINES = ["Welcome to", "Stinky", "Springs"]
TEXT_COLOR = graphics.Color(215, 205, 165)  # parchment/sign-ish cream
LINE_GAP = 1
FONT_PATH = Path(__file__).parent / "fonts" / "5x7.bdf"
FONT = load_font(FONT_PATH)

MIN_SCALE = 0.15
MAX_SCALE = 1.0
GROW_FRAMES = 45
HOLD_FRAMES = 25


class _PixelBuffer:
    """Minimal canvas-like object -- just enough for graphics.DrawText to
    render into -- so the sign can be pre-rendered off-screen once, instead
    of being redrawn at each frame's scale directly."""

    def __init__(self, width):
        self.width = width
        self.pixels = {}

    def SetPixel(self, x, y, r, g, b):
        self.pixels[(x, y)] = (r, g, b)


def _render_sign():
    line_height = FONT.height + LINE_GAP
    line_widths = [text_pixel_width(FONT, line) for line in TEXT_LINES]
    sign_width = max(line_widths)
    sign_height = line_height * len(TEXT_LINES) - LINE_GAP

    buffer = _PixelBuffer(sign_width)
    for i, line in enumerate(TEXT_LINES):
        x = (sign_width - line_widths[i]) // 2
        y = i * line_height + FONT.baseline
        graphics.DrawText(buffer, FONT, x, y, TEXT_COLOR, line)

    return buffer.pixels, sign_width, sign_height


def _draw_sign(canvas, pixels, sign_width, sign_height, scale, width, height):
    # Nearest-neighbor scale-up: each source pixel becomes a block whose
    # edges are rounded independently, so blocks tile the scaled image
    # exactly with no gaps or overlap at any scale.
    scaled_width = round(sign_width * scale)
    scaled_height = round(sign_height * scale)
    origin_x = (width - scaled_width) // 2
    origin_y = (height - scaled_height) // 2

    for (sx, sy), (r, g, b) in pixels.items():
        x0 = origin_x + round(sx * scale)
        x1 = origin_x + round((sx + 1) * scale)
        y0 = origin_y + round(sy * scale)
        y1 = origin_y + round((sy + 1) * scale)
        for y in range(y0, max(y0 + 1, y1)):
            for x in range(x0, max(x0 + 1, x1)):
                canvas.SetPixel(x, y, r, g, b)


def run(canvas, width, height):
    sign_pixels, sign_width, sign_height = _render_sign()
    total_frames = GROW_FRAMES + HOLD_FRAMES
    for frame in range(total_frames):
        canvas.Clear()

        progress = min(1.0, frame / GROW_FRAMES)
        scale = MIN_SCALE + (MAX_SCALE - MIN_SCALE) * progress
        _draw_sign(canvas, sign_pixels, sign_width, sign_height, scale, width, height)

        canvas = yield canvas


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
