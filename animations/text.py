"""Shared helpers for drawing BDF bitmap fonts via the `graphics` module."""

from RGBMatrixEmulator import graphics


def load_font(path):
    font = graphics.Font()
    font.LoadFont(str(path))
    return font


def text_pixel_width(font, text):
    return sum(font.CharacterWidth(ord(char)) for char in text)


def centered_y(font, height):
    """Baseline y that vertically centers one line of text within `height`
    pixels. DrawText's y argument is the baseline, not the top of the
    text, so this centers the font's box, then shifts down by baseline."""
    return (height - font.height) // 2 + font.baseline
