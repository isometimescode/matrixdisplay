"""Plays one animation at a time, owning the frame loop, timing, and
canvas so animations only have to decide what to draw.

Each animation module exposes `run(canvas, width, height)`: a generator
that does one-time setup, then repeatedly draws a frame and does
`canvas = yield canvas`. That round-trip matters on real hardware: the
matrix library double-buffers, so `SwapOnVSync` can hand back a *different*
canvas object each time. Without feeding that back in, the animation would
keep drawing onto a buffer that's no longer the offscreen one. `send()` is
what delivers the fresh canvas back into the generator.

Infinite animations (nothing ever stops the loop) and finite ones (a
scroll that completes one pass and returns) look identical to `play_one`:
it just keeps pulling frames until the generator stops on its own, or a
DURATION cap is hit, whichever comes first. The cap only matters for
animations with no natural end -- a module can set its own DURATION to
override the default below.
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
