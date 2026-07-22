# matrixdisplay

A Raspberry Pi 3 B+ driving an Adafruit 64x32 RGB LED matrix panel: plays a
sequence of animations, controllable from a web UI. Built to run in an RV,
so it needs to work without always being on a known network.

**Status: running.** The daemon drives the real panel on the Pi via a
systemd service (`matrixdisplay-daemon`, enabled at boot). The web control
UI isn't built yet.

## How it works

- A **display daemon** (`daemon/`) owns the LED matrix and cycles through a
  sequence of animations, playing manually-picked animations once before
  resuming the sequence where it left off.
- **Animations** (`animations/`) are self-contained modules, each exposing
  a `run(canvas, width, height)` generator that yields one frame at a
  time -- the daemon owns frame timing and `SwapOnVSync`, animations only
  decide what to draw.
- A **web app** will provide a control UI (switch animations, shut down
  cleanly, etc.) and talk to the daemon rather than touching the matrix
  hardware directly -- not built yet.
- Animations can be developed and tested against a software emulator, so
  no physical hardware is required to work on them.

See [HARDWARE.md](HARDWARE.md) for the parts list and wiring.

## Usage

Coming soon — this section will cover installing dependencies, running the
daemon and web app, and using the control UI, once they exist.

## Development

Animations are written against
[`rpi-rgb-led-matrix`](https://github.com/hzeller/rpi-rgb-led-matrix)'s
Python bindings, using its `RGBMatrixEmulator` companion for
hardware-free development. See [HARDWARE.md](HARDWARE.md) for details on
the target hardware.

Requires Python 3.13.5 (pinned in `.python-version` to match the Pi; use
`pyenv` if you have it, or install that version yourself).

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Run the daemon, cycling through the full animation sequence, against the
emulator:

```
python -m daemon.run
```

Or run a single animation on its own -- loops forever, ignoring its normal
duration cap, for quick iteration:

```
python -m animations.camp_logo
```

(swap in `scroll_horizontal`, `stinky_pool`, or `rv_arrival` for any of
the others). Then open <http://localhost:8888> in a browser to watch it.
(The emulator's `browser` adapter serves the display over HTTP — no
desktop environment needed, which also means this works unchanged if you
run it on the Pi itself and view it from your laptop's browser instead.)

If you use VS Code, `.vscode/tasks.json` has ready-made tasks for both of
the above ("Run daemon" and "Run animation (pick)").

Lint with `flake8` (config in `.flake8`).
