# Hardware

## Parts

- Raspberry Pi 3 B+
- Adafruit 64x32 RGB LED matrix panel (HUB75-style)
- [Adafruit RGB Matrix Bonnet](https://www.adafruit.com/product/3211) — the
  driver board that connects the panel to the Pi's 40-pin GPIO header. It's
  a passive interface board (level shifters + power protection circuitry);
  all animation logic runs on the Pi itself.
- A dedicated 5V power supply for the matrix panel (4A+ recommended), fed
  into the bonnet's barrel jack. **The panel cannot be powered from the
  Pi** — its own supply/GPIO can't source enough current.

## Driver library

Uses [`rpi-rgb-led-matrix`](https://github.com/hzeller/rpi-rgb-led-matrix)
(hzeller) — the standard library for driving HUB75 panels from a Pi's GPIO
with flicker-free timing. It has Python bindings, and an emulator mode
(`RGBMatrixEmulator`) that mimics the same API in a desktop window, so
animations can be written and tested without the physical panel.

Use the `adafruit-hat` hardware mapping to match the bonnet's wiring.

## Known gotchas

- **Onboard audio must be disabled.** It shares hardware timers with the
  matrix library and causes visible flicker if left on.
- **GPIO timing needs slowing down on faster Pis.** The library's default
  GPIO write speed outruns what the panel can reliably latch on a Pi 3 B+,
  causing visible flicker/ghosting especially at the panel's edges. Fixed
  with `options.gpio_slowdown = 2` in `daemon/matrix.py`.
- **Killing the driver process mid-frame freezes the panel**, since its
  refresh thread dies with it, leaving the LEDs on whatever half-drawn
  multiplexed frame was in progress. `daemon/run.py` handles `SIGTERM`/
  `SIGINT` by clearing the canvas before exiting -- don't `kill -9` it, use
  a normal `kill`/`systemctl stop` so that handler gets to run.
- **The driver process needs root/low-level GPIO access.** Keep it as a
  separate, privileged process from anything web-facing (see the daemon/
  web app split in the main [README](README.md)).

## GPIO pin usage (adafruit-hat mapping)

The bonnet uses GPIO 4 (strobe), 5, 6, 12, 13, 16, 17, 20, 21, 22, 23, 24,
26, 27 for matrix control/color signals. **GPIO2 and GPIO3 are not used**
by the bonnet — confirmed free if a physical button (e.g. a shutdown
button via the `gpio-shutdown` overlay on GPIO3/pin 5) is ever wanted.
Current plan is a web UI shutdown control instead.
