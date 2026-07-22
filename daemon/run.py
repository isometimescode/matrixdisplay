"""The main daemon loop: cycles through SEQUENCE by default, playing
manually queued picks first when there are any.

A manual pick (eventually from the web UI) just gets appended to
manual_queue -- it plays once, then the sequence resumes on its own from
wherever it already was. No explicit "resume" action, and no way to pin
an animation indefinitely, by design -- see SETUP.md's Daemon design
section for the reasoning.

Run against the emulator:
    python -m daemon.run
"""

import signal
import sys
from collections import deque

from animations import camp_logo, rv_arrival, stinky_pool
from daemon.matrix import HEIGHT, WIDTH, build_matrix
from daemon.player import play_one


SEQUENCE = [camp_logo, rv_arrival, stinky_pool]


def main():
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
        if manual_queue:
            module = manual_queue.popleft()
        else:
            module = SEQUENCE[sequence_index % len(SEQUENCE)]
            sequence_index += 1

        canvas = play_one(matrix, canvas, module, WIDTH, HEIGHT)


if __name__ == "__main__":
    main()
