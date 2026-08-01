"""Filesystem 'inbox' used to hand manual animation picks from the web
app to the daemon. The web app drops a file per pick (atomic write +
rename so the daemon never sees a partial file); the daemon polls the
directory once per outer-loop iteration, consumes whatever it finds in
filename order, and deletes each file after reading it.

A pick file holds a kind on its first line ("name" or "text") and the
payload on the rest -- a named animation to play, or free text to feed
to the scrolling-text animation.
"""

import os
import time
import uuid
from pathlib import Path

MAX_TEXT_LEN = 120

# On the Pi, MATRIXDISPLAY_INBOX_DIR points at /run/matrixdisplay/inbox --
# tmpfs, shared between the daemon (root, dropping to user `daemon` once
# RGBMatrix has initialized the hardware) and the web app (user `pi`).
# It can't live under the repo checkout: that's inside pi's home
# directory, which is mode 700 and blocks every other user from even
# traversing into it, regardless of how the inbox itself is permissioned.
# Provisioned at boot -- owned root:matrixdisplay, mode 2770 -- via
# systemd-tmpfiles (see systemd/matrixdisplay-tmpfiles.conf), so it
# already exists with the right permissions before either service starts.
# Falls back to a repo-relative path for local dev, where both sides run
# as the same user and none of this applies.
_DEFAULT_INBOX_DIR = Path(__file__).resolve().parent.parent / "var" / "inbox"
INBOX_DIR = Path(os.environ.get("MATRIXDISPLAY_INBOX_DIR", _DEFAULT_INBOX_DIR))


def ensure_inbox_dir():
    """Create the inbox dir if missing -- a dev-machine convenience. On
    the Pi this is a no-op: systemd-tmpfiles already created it before
    either service started."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    return INBOX_DIR


def _drop(kind, payload):
    ensure_inbox_dir()
    filename = f"{time.time():.6f}-{uuid.uuid4().hex}-{kind}.pick"
    final_path = INBOX_DIR / filename
    tmp_path = INBOX_DIR / f".{filename}.tmp"
    tmp_path.write_text(f"{kind}\n{payload}")
    os.rename(tmp_path, final_path)  # atomic on POSIX, same filesystem
    return final_path


def drop_pick(name):
    """Atomically write a pick request for animation `name`."""
    return _drop("name", name)


def drop_text_pick(text):
    """Atomically write a pick request for free-scrolling `text`."""
    return _drop("text", text[:MAX_TEXT_LEN])


def drain_picks(valid_names):
    """Read and remove all pending pick files, oldest first, returning
    a list of `(kind, value)` pairs -- `("name", <animation name>)` or
    `("text", <message>)`. Anything malformed, an unknown animation
    name, or blank text is treated as garbage and removed without
    raising."""
    ensure_inbox_dir()
    picks = []
    for path in sorted(INBOX_DIR.glob("*.pick")):
        try:
            content = path.read_text()
        finally:
            path.unlink(missing_ok=True)
        kind, _, value = content.partition("\n")
        if kind == "name" and value in valid_names:
            picks.append(("name", value))
        elif kind == "text":
            value = value.strip()
            if value:
                picks.append(("text", value[:MAX_TEXT_LEN]))
    return picks
