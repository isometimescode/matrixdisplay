"""Shared matrix setup -- the one place panel dimensions are defined, so
the daemon and every animation agree on them."""

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

WIDTH, HEIGHT = 64, 32


def build_matrix():
    options = RGBMatrixOptions()
    options.rows = HEIGHT
    options.cols = WIDTH
    options.hardware_mapping = "adafruit-hat"
    return RGBMatrix(options=options)
