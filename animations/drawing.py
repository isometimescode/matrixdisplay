"""Shared low-level pixel helpers used across animations."""

import math

from daemon.matrix import graphics


def set_pixel(canvas, x, y, color):
    canvas.SetPixel(x, y, color.red, color.green, color.blue)


def fill_rect(canvas, x, y, width, height, color):
    for row in range(height):
        for col in range(width):
            set_pixel(canvas, x + col, y + row, color)


def draw_rect_outline(canvas, x, y, width, height, color):
    for col in range(width):
        set_pixel(canvas, x + col, y, color)
        set_pixel(canvas, x + col, y + height - 1, color)
    for row in range(height):
        set_pixel(canvas, x, y + row, color)
        set_pixel(canvas, x + width - 1, y + row, color)


def dim(color, brightness):
    return graphics.Color(
        round(color.red * brightness),
        round(color.green * brightness),
        round(color.blue * brightness),
    )


def draw_stink_line(
    canvas, x_base, top_y, tick, phase_offset, color, rise_height, frames_per_row,
    brightness=1.0,
):
    """A wavy line rising and fading out above (x_base, top_y), looping
    every `rise_height * frames_per_row` ticks -- reads as dissipating
    smell/smoke rather than a static squiggle."""
    cycle = rise_height * frames_per_row
    progress = (tick + phase_offset) % cycle
    rise = progress / frames_per_row

    for row in range(int(rise) + 1):
        y = top_y - row
        if y < 0:
            break

        wave = math.sin(row * 0.6 + tick * 0.15) * 1.5
        x = round(x_base + wave)
        fade = max(0.0, 1.0 - row / rise_height) * brightness
        set_pixel(canvas, x, y, dim(color, fade))
