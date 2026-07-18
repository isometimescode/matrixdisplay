"""Runs a single animation standalone against the emulator, for the
`python -m animations.<name>` dev workflow -- no daemon, no sequencing,
just that one animation looping forever (ignoring DURATION) until you
Ctrl+C, restarting from the top each time a finite one completes a pass.
"""

import time

from daemon.matrix import HEIGHT, WIDTH, build_matrix


def run_standalone(module):
    matrix = build_matrix()
    canvas = matrix.CreateFrameCanvas()
    frame_delay = getattr(module, "FRAME_DELAY", 0.03)

    while True:
        frames = module.run(canvas, WIDTH, HEIGHT)
        canvas = next(frames)
        while True:
            canvas = matrix.SwapOnVSync(canvas)
            time.sleep(frame_delay)
            try:
                canvas = frames.send(canvas)
            except StopIteration:
                break
