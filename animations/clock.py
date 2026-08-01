"""Current time -- day of week and 24-hour clock -- with a set of corner
brackets that grow along the edges of a frame around it until they meet
in the middle of each side, sealing the box shut; the animation ends
there. The time is read once at the start and held fixed for the whole
animation, so there's never a digit changing mid-transition.

Run standalone:
    python -m animations.clock
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daemon.matrix import graphics
from daemon.settings import get_timezone

from animations.drawing import dim, set_pixel
from animations.text import centered_y, load_font, text_pixel_width

FRAME_DELAY = 0.05
TEXT_COLOR = graphics.Color(20, 130, 140)
FONT_PATH = Path(__file__).parent / "fonts" / "6x9.bdf"
FONT = load_font(FONT_PATH)

TEXT_FADE_FRAMES = 20  # how long the text takes to fade in at the start
GROWTH_FRAMES = 200  # total animation length -- how long the brackets take to seal

FRAME_PADDING = 4  # gap between the text's bounding box and the brackets
FRAME_DIM = 0.6  # brackets read as a secondary accent, dimmer than the text


def _text_scale_for(frame):
    return min(1.0, frame / TEXT_FADE_FRAMES)


def _draw_corner_brackets(canvas, x0, y0, x1, y1, arm_h, arm_v, color):
    for i in range(arm_h):
        set_pixel(canvas, x0 + i, y0, color)  # top edge, growing rightward
        set_pixel(canvas, x1 - i, y0, color)  # top edge, growing leftward
        set_pixel(canvas, x0 + i, y1, color)  # bottom edge, growing rightward
        set_pixel(canvas, x1 - i, y1, color)  # bottom edge, growing leftward
    for i in range(arm_v):
        set_pixel(canvas, x0, y0 + i, color)  # left edge, growing downward
        set_pixel(canvas, x0, y1 - i, color)  # left edge, growing upward
        set_pixel(canvas, x1, y0 + i, color)  # right edge, growing downward
        set_pixel(canvas, x1, y1 - i, color)  # right edge, growing upward


def run(canvas, width, height):
    text = datetime.now(ZoneInfo(get_timezone())).strftime("%a %H:%M")
    text_width = text_pixel_width(FONT, text)
    x = (width - text_width) // 2
    y = centered_y(FONT, height)

    top_y = (height - FONT.height) // 2
    frame_x0 = x - FRAME_PADDING
    frame_y0 = top_y - FRAME_PADDING
    frame_x1 = x + text_width - 1 + FRAME_PADDING
    frame_y1 = top_y + FONT.height - 1 + FRAME_PADDING

    # Each side's two arms meet in the middle once they've each grown to
    # half that side's length -- rounded up so odd lengths still close.
    half_w = (frame_x1 - frame_x0 + 2) // 2
    half_h = (frame_y1 - frame_y0 + 2) // 2
    max_half = max(half_w, half_h)

    bracket_color = dim(TEXT_COLOR, FRAME_DIM)

    for frame in range(GROWTH_FRAMES):
        progress = frame / (GROWTH_FRAMES - 1)
        arm = round(max_half * progress)
        arm_h = min(arm, half_w)
        arm_v = min(arm, half_h)

        canvas.Clear()
        _draw_corner_brackets(
            canvas, frame_x0, frame_y0, frame_x1, frame_y1, arm_h, arm_v, bracket_color
        )
        text_color = dim(TEXT_COLOR, _text_scale_for(frame))
        graphics.DrawText(canvas, FONT, x, y, text_color, text)
        canvas = yield canvas


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
