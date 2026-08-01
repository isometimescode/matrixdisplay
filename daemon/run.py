"""The main daemon loop: cycles through SEQUENCE by default, playing
manually queued picks first when there are any -- a manual pick plays
once, then the sequence resumes where it left off.

Run against the emulator:
    python -m daemon.run
"""

import functools
import signal
import sys
from collections import deque
from types import SimpleNamespace

from animations import (
    camp_logo,
    clock,
    rv_arrival,
    scroll_horizontal,
    stinky_pool,
    unicorn_trail,
)
from daemon.inbox import drain_picks, ensure_inbox_dir
from daemon.matrix import HEIGHT, WIDTH, build_matrix
from daemon.player import play_one


SEQUENCE = [camp_logo, unicorn_trail, rv_arrival, stinky_pool, clock]
MODULES_BY_NAME = {module.__name__.rsplit(".", 1)[-1]: module for module in SEQUENCE}


def _text_pick(text):
    """A module-like object that plays scroll_horizontal with custom
    text, so play_one can treat it the same as any other animation."""
    return SimpleNamespace(
        run=functools.partial(scroll_horizontal.run, text=text),
        FRAME_DELAY=scroll_horizontal.FRAME_DELAY,
    )


def main():
    # Must happen before build_matrix(): RGBMatrix drops root privileges
    # once the hardware is initialized, and the dropped-to user can't
    # create this directory itself.
    ensure_inbox_dir()

    matrix = build_matrix()
    canvas = matrix.CreateFrameCanvas()

    def clear_and_exit(signum, frame):
        # Without this, killing the process mid-frame leaves the panel's
        # refresh thread dead and the LEDs frozen on a half-drawn frame.
        canvas.Clear()
        matrix.SwapOnVSync(canvas)
        sys.exit(0)

    signal.signal(signal.SIGTERM, clear_and_exit)
    signal.signal(signal.SIGINT, clear_and_exit)

    manual_queue = deque()
    sequence_index = 0

    while True:
        for kind, value in drain_picks(MODULES_BY_NAME.keys()):
            if kind == "name":
                manual_queue.append(MODULES_BY_NAME[value])
            else:
                manual_queue.append(_text_pick(value))

        if manual_queue:
            module = manual_queue.popleft()
        else:
            module = SEQUENCE[sequence_index % len(SEQUENCE)]
            sequence_index += 1

        canvas = play_one(matrix, canvas, module, WIDTH, HEIGHT)


if __name__ == "__main__":
    main()
