"""Plays one animation at a time, owning the frame loop, timing, and
canvas so animations only have to decide what to draw.

Each animation module exposes `run(canvas, width, height)`: a generator
that does setup, then repeatedly does `canvas = yield canvas`. That
round-trip matters on real hardware -- the matrix double-buffers, so
`SwapOnVSync` can hand back a different canvas object each time, and
`send()` is what feeds it back into the generator.

`play_one` just keeps pulling frames until the generator stops on its
own or a DURATION cap is hit, whichever comes first. The cap only
matters for animations with no natural end; a module can override the
default below with its own DURATION.
"""

import time

DEFAULT_DURATION = 15
DEFAULT_FRAME_DELAY = 0.03


def play_one(matrix, canvas, module, width, height):
    duration = getattr(module, "DURATION", DEFAULT_DURATION)
    frame_delay = getattr(module, "FRAME_DELAY", DEFAULT_FRAME_DELAY)
    deadline = time.monotonic() + duration

    frames = module.run(canvas, width, height)
    canvas = next(frames)  # runs setup and draws the first frame

    while True:
        canvas = matrix.SwapOnVSync(canvas)
        time.sleep(frame_delay)
        if time.monotonic() >= deadline:
            frames.close()
            break
        try:
            canvas = frames.send(canvas)
        except StopIteration:
            break

    return canvas
