"""RV arrival, step 1: a boxy RV drives left-to-right across the panel.

This is just the shape and movement -- no wheel rotation, tree reveals, or
growing sign yet (see SETUP.md's Content plan; those are separate
sub-steps layered on top of this one).

Run standalone with the emulator (no hardware, no daemon needed):
    python -m animations.rv_arrival
"""

from RGBMatrixEmulator import graphics

FRAME_DELAY = 0.08
# No DURATION set -- the drive-by finishes on its own once the RV clears
# the right edge, same as the horizontal text scroll.

BODY_COLOR = graphics.Color(225, 220, 205)  # cream/white
GLASS_COLOR = graphics.Color(140, 175, 195)  # pale blue-gray glass
DOOR_OUTLINE_COLOR = graphics.Color(15, 15, 20)
ACCENT_COLOR = graphics.Color(180, 45, 35)  # red side storage box
HEADLIGHT_COLOR = graphics.Color(230, 185, 60)
HUB_COLOR = graphics.Color(130, 130, 130)
# Lighter than a "real" tire black -- true near-black tends to vanish into
# the gaps between LEDs when viewed at night, so this trades accuracy for
# actually being visible. Only the real panel will confirm either way.
WHEEL_COLOR = graphics.Color(75, 75, 75)

# The RV is two stacked rectangles, not one flat box: a taller rear "box"
# (the camper body) and a shorter front "cab" (the van chassis), sitting on
# a shared ground line -- the difference in height is what reads as the
# step/bump between them, like a real cab-chassis camper.
BOX_WIDTH = 18
BOX_HEIGHT = 10
CAB_WIDTH = 4
CAB_HEIGHT = 6
RV_WIDTH = BOX_WIDTH + CAB_WIDTH
WHEEL_SIZE = 4
RV_HEIGHT = BOX_HEIGHT + WHEEL_SIZE

# The box-to-cab height difference is stepped down in two 1-pixel-wide
# stages rather than one abrupt drop or a diagonal ramp (a true slope
# doesn't read cleanly at this resolution).
BOX_CAB_STEP = (BOX_HEIGHT - CAB_HEIGHT) // 2

# All positions below are local to the RV's own top-left corner (0, 0);
# _draw_rv offsets everything by the RV's current x and the ground line.
# Window and vent sit near the roofline, not mid-body.
WINDOW_TOP_FROM_BOX_TOP = 1
WINDOW_HEIGHT = 3
BOX_WINDOW_LEFT = 3
BOX_WINDOW_WIDTH = 7
VENT_LEFT = 15
# One column wider than it looks like it should be -- the extra column
# lands on the box's stepped-down corner, so the glass reads as spilling
# into that little slope instead of stopping short of it.
VENT_WIDTH = 3

# Small tail light, rear edge of the box, same row as the headlight so
# they line up across the whole vehicle.
ACCENT_LEFT = 0
ACCENT_WIDTH = 1
ACCENT_HEIGHT = 2

# The door is just an outline (same fill as the body), not a solid block,
# same as it's drawn on the real EKKO -- otherwise it'd read as a random
# blob rather than a door. Runs the full height of the box, roof to floor.
DOOR_LEFT = 11
DOOR_WIDTH = 3
DOOR_TOP = 1
DOOR_HEIGHT = BOX_HEIGHT - DOOR_TOP

HEADLIGHT_TOP = 2
HEADLIGHT_HEIGHT = 2

WHEEL_BACK_X = 4
WHEEL_FRONT_X = BOX_WIDTH + (CAB_WIDTH - WHEEL_SIZE) // 2


def _fill_rect(canvas, x, y, width, height, color):
    for row in range(height):
        for col in range(width):
            canvas.SetPixel(x + col, y + row, color.red, color.green, color.blue)


def _draw_rect_outline(canvas, x, y, width, height, color):
    for col in range(width):
        canvas.SetPixel(x + col, y, color.red, color.green, color.blue)
        canvas.SetPixel(x + col, y + height - 1, color.red, color.green, color.blue)
    for row in range(height):
        canvas.SetPixel(x, y + row, color.red, color.green, color.blue)
        canvas.SetPixel(x + width - 1, y + row, color.red, color.green, color.blue)


def _draw_wheel(canvas, x, y):
    # A lighter cross-shaped hub in the middle of the tire, rather than a
    # flat-colored disc.
    for row in range(WHEEL_SIZE):
        for col in range(WHEEL_SIZE):
            color = HUB_COLOR if row in (1, 2) or col in (1, 2) else WHEEL_COLOR
            canvas.SetPixel(x + col, y + row, color.red, color.green, color.blue)


def _draw_rv(canvas, x, height):
    wheel_top = height - WHEEL_SIZE
    box_top = wheel_top - BOX_HEIGHT
    cab_top = wheel_top - CAB_HEIGHT

    _fill_rect(canvas, x, box_top, BOX_WIDTH, BOX_HEIGHT, BODY_COLOR)
    _fill_rect(canvas, x + BOX_WIDTH, cab_top, CAB_WIDTH, CAB_HEIGHT, BODY_COLOR)

    # Step the box's top-front corner down to the cab's height in two
    # risers: the box's last column is cut down partway (painted over in
    # black, the canvas background), then the cab -- one column further
    # right -- drops the rest of the way. Each riser is 1 column wide, so
    # the transition reads as a staircase rather than a diagonal ramp.
    for row in range(BOX_CAB_STEP):
        canvas.SetPixel(x + BOX_WIDTH - 1, box_top + row, 0, 0, 0)

    window_top = box_top + WINDOW_TOP_FROM_BOX_TOP
    _fill_rect(
        canvas, x + BOX_WINDOW_LEFT, window_top, BOX_WINDOW_WIDTH, WINDOW_HEIGHT,
        GLASS_COLOR,
    )
    _fill_rect(
        canvas, x + VENT_LEFT, window_top, VENT_WIDTH, WINDOW_HEIGHT, GLASS_COLOR
    )
    _draw_rect_outline(
        canvas, x + DOOR_LEFT, box_top + DOOR_TOP, DOOR_WIDTH, DOOR_HEIGHT,
        DOOR_OUTLINE_COLOR,
    )

    # Tail light and headlight share one row, front to back of the vehicle.
    lights_top = cab_top + HEADLIGHT_TOP
    _fill_rect(
        canvas, x + ACCENT_LEFT, lights_top, ACCENT_WIDTH, ACCENT_HEIGHT, ACCENT_COLOR
    )
    _fill_rect(
        canvas,
        x + BOX_WIDTH + CAB_WIDTH - 1,
        lights_top,
        1,
        HEADLIGHT_HEIGHT,
        HEADLIGHT_COLOR,
    )

    for wheel_x in (WHEEL_BACK_X, WHEEL_FRONT_X):
        _draw_wheel(canvas, x + wheel_x, wheel_top)


def run(canvas, width, height):
    # Start fully off the left edge, end fully off the right edge.
    x = -RV_WIDTH
    while x < width:
        canvas.Clear()
        _draw_rv(canvas, x, height)
        canvas = yield canvas

        x += 1


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
