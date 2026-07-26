"""RV arrival: a boxy RV drives left-to-right with turning wheels, while
big background trees drift the other way.

Run standalone:
    python -m animations.rv_arrival
"""

from daemon.matrix import graphics

from animations.drawing import draw_rect_outline, fill_rect, set_pixel

FRAME_DELAY = 0.09
# No DURATION set -- the drive-by finishes on its own once the RV clears
# the right edge.

BODY_COLOR = graphics.Color(225, 220, 205)  # cream/white
GLASS_COLOR = graphics.Color(140, 175, 195)  # pale blue-gray glass
DOOR_OUTLINE_COLOR = graphics.Color(15, 15, 20)
ACCENT_COLOR = graphics.Color(180, 45, 35)  # red side storage box
HEADLIGHT_COLOR = graphics.Color(230, 185, 60)
HUB_COLOR = graphics.Color(130, 130, 130)
# Lighter than "real" tire black, which vanishes into the gaps between
# LEDs at night -- trades accuracy for visibility.
WHEEL_COLOR = graphics.Color(75, 75, 75)

# Two stacked rectangles on a shared ground line: a taller rear "box"
# (camper body) and shorter front "cab" (van chassis) -- the height
# difference reads as the step between them, like a real cab-chassis RV.
BOX_WIDTH = 18
BOX_HEIGHT = 10
CAB_WIDTH = 4
CAB_HEIGHT = 6
RV_WIDTH = BOX_WIDTH + CAB_WIDTH
WHEEL_SIZE = 4
RV_HEIGHT = BOX_HEIGHT + WHEEL_SIZE

# Stepped down in two 1px stages rather than an abrupt drop or diagonal
# ramp -- a true slope doesn't read cleanly at this resolution.
BOX_CAB_STEP = (BOX_HEIGHT - CAB_HEIGHT) // 2

# Positions below are local to the RV's top-left corner; _draw_rv offsets
# by the RV's current x and the ground line.
WINDOW_TOP_FROM_BOX_TOP = 1
WINDOW_HEIGHT = 3
BOX_WINDOW_LEFT = 3
BOX_WINDOW_WIDTH = 7
VENT_LEFT = 15
# One column wider than it looks -- the extra column lands on the box's
# stepped-down corner, so the glass reads as spilling into that slope.
VENT_WIDTH = 3

# Small tail light, rear edge of the box, same row as the headlight so
# they line up across the whole vehicle.
ACCENT_LEFT = 0
ACCENT_WIDTH = 1
ACCENT_HEIGHT = 2

# Outline only (a solid block would read as a random blob, not a door),
# same as the real EKKO. Runs the full height of the box.
DOOR_LEFT = 11
DOOR_WIDTH = 3
DOOR_TOP = 1
DOOR_HEIGHT = BOX_HEIGHT - DOOR_TOP

HEADLIGHT_TOP = 2
HEADLIGHT_HEIGHT = 2

WHEEL_BACK_X = 4
WHEEL_FRONT_X = BOX_WIDTH + (CAB_WIDTH - WHEEL_SIZE) // 2

# Pixels of travel per spoke swap -- ties the "turn" to distance driven
# rather than wall-clock time, so it reads as rolling instead of flickering
# in place.
WHEEL_TOGGLE_INTERVAL = 2

TREE_TRUNK_COLOR = graphics.Color(90, 60, 35)
TREE_LEAF_COLOR = graphics.Color(40, 120, 55)
TREE_WIDTH = 10
TREE_TRUNK_HEIGHT = 5
# Leaves fill nearly the full panel height -- just the trunk and a
# 1-pixel gap at the very top are left out.
TREE_TOP_MARGIN = 1

# Trees drift right-to-left, opposite the RV's drive -- reads as passing
# scenery rather than a static backdrop.
TREE_SPEED = 1
# Frame indices (0 = the moment the RV enters at the left edge) at which
# each tree spawns off the right edge and starts drifting.
TREE_SPAWN_FRAMES = (0, 14, 33, 49, 70)


def _draw_wheel(canvas, x, y, spoke_frame):
    # Two alternating hub shapes -- a "+" and an "x" -- stand in for
    # rotation; there aren't enough pixels for the real thing.
    for row in range(WHEEL_SIZE):
        for col in range(WHEEL_SIZE):
            if spoke_frame == 0:
                is_hub = row in (1, 2) or col in (1, 2)
            else:
                is_hub = row == col or row + col == WHEEL_SIZE - 1
            color = HUB_COLOR if is_hub else WHEEL_COLOR
            set_pixel(canvas, x + col, y + row, color)


def _draw_tree(canvas, x, height):
    # Short trunk under a full-height triangular canopy, tapering from a
    # point to full width just above the trunk -- a simple conifer shape.
    trunk_top = height - TREE_TRUNK_HEIGHT
    trunk_left = x + (TREE_WIDTH - 1) // 2
    fill_rect(canvas, trunk_left, trunk_top, 1, TREE_TRUNK_HEIGHT, TREE_TRUNK_COLOR)

    canopy_height = trunk_top - TREE_TOP_MARGIN
    for row in range(canopy_height):
        row_width = 1 + (TREE_WIDTH - 1) * row // (canopy_height - 1)
        inset = (TREE_WIDTH - row_width) // 2
        fill_rect(
            canvas, x + inset, TREE_TOP_MARGIN + row, row_width, 1, TREE_LEAF_COLOR
        )


def _draw_rv(canvas, x, height, spoke_frame):
    wheel_top = height - WHEEL_SIZE
    box_top = wheel_top - BOX_HEIGHT
    cab_top = wheel_top - CAB_HEIGHT

    fill_rect(canvas, x, box_top, BOX_WIDTH, BOX_HEIGHT, BODY_COLOR)
    fill_rect(canvas, x + BOX_WIDTH, cab_top, CAB_WIDTH, CAB_HEIGHT, BODY_COLOR)

    # Steps the box's front corner down to cab height in two 1-column
    # risers -- box's last column painted over in black, then the cab
    # drops the rest of the way -- reads as a staircase, not a ramp.
    for row in range(BOX_CAB_STEP):
        canvas.SetPixel(x + BOX_WIDTH - 1, box_top + row, 0, 0, 0)

    window_top = box_top + WINDOW_TOP_FROM_BOX_TOP
    fill_rect(
        canvas, x + BOX_WINDOW_LEFT, window_top, BOX_WINDOW_WIDTH, WINDOW_HEIGHT,
        GLASS_COLOR,
    )
    fill_rect(
        canvas, x + VENT_LEFT, window_top, VENT_WIDTH, WINDOW_HEIGHT, GLASS_COLOR
    )
    draw_rect_outline(
        canvas, x + DOOR_LEFT, box_top + DOOR_TOP, DOOR_WIDTH, DOOR_HEIGHT,
        DOOR_OUTLINE_COLOR,
    )

    # Tail light and headlight share one row, front to back of the vehicle.
    lights_top = cab_top + HEADLIGHT_TOP
    fill_rect(
        canvas, x + ACCENT_LEFT, lights_top, ACCENT_WIDTH, ACCENT_HEIGHT, ACCENT_COLOR
    )
    fill_rect(
        canvas,
        x + BOX_WIDTH + CAB_WIDTH - 1,
        lights_top,
        1,
        HEADLIGHT_HEIGHT,
        HEADLIGHT_COLOR,
    )

    for wheel_x in (WHEEL_BACK_X, WHEEL_FRONT_X):
        _draw_wheel(canvas, x + wheel_x, wheel_top, spoke_frame)


def run(canvas, width, height):
    # Start fully off the left edge, end fully off the right edge.
    x = -RV_WIDTH
    frame_index = 0
    while x < width:
        canvas.Clear()

        # Trees are drawn behind the RV, so the RV occludes any it's
        # currently overlapping.
        for spawn_frame in TREE_SPAWN_FRAMES:
            if frame_index < spawn_frame:
                continue
            tree_x = width - TREE_SPEED * (frame_index - spawn_frame)
            if tree_x > -TREE_WIDTH:
                _draw_tree(canvas, tree_x, height)

        spoke_frame = (x // WHEEL_TOGGLE_INTERVAL) % 2
        _draw_rv(canvas, x, height, spoke_frame)
        canvas = yield canvas

        x += 1
        frame_index += 1


if __name__ == "__main__":
    import sys

    from daemon.devrun import run_standalone

    run_standalone(sys.modules[__name__])
