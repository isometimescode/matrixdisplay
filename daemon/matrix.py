"""Shared matrix setup -- the one place panel dimensions are defined, so
the daemon and every animation agree on them."""

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

WIDTH, HEIGHT = 64, 32


def build_matrix():
    options = RGBMatrixOptions()
    options.rows = HEIGHT
    options.cols = WIDTH
    return RGBMatrix(options=options)
