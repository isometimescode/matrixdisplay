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

from collections import deque

from animations import camp_logo, rv_arrival, stinky_pool
from daemon.matrix import HEIGHT, WIDTH, build_matrix
from daemon.player import play_one


SEQUENCE = [camp_logo, rv_arrival, stinky_pool]


def main():
    matrix = build_matrix()
    canvas = matrix.CreateFrameCanvas()
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
