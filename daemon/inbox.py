"""Filesystem 'inbox' used to hand manual animation picks from the web
app to the daemon. The web app drops a file per pick (atomic write +
rename so the daemon never sees a partial file); the daemon polls the
directory once per outer-loop iteration, consumes whatever it finds in
filename order, and deletes each file after reading it.
"""

import os
import time
import uuid
from pathlib import Path

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


def drop_pick(name):
    """Atomically write a pick request for animation `name`."""
    ensure_inbox_dir()
    filename = f"{time.time():.6f}-{uuid.uuid4().hex}-{name}.pick"
    final_path = INBOX_DIR / filename
    tmp_path = INBOX_DIR / f".{filename}.tmp"
    tmp_path.write_text(name)
    os.rename(tmp_path, final_path)  # atomic on POSIX, same filesystem
    return final_path


def drain_picks(valid_names):
    """Read and remove all pending pick files, oldest first, returning
    the list of valid animation names found. Anything whose content
    isn't in `valid_names` is treated as garbage and removed without
    raising."""
    ensure_inbox_dir()
    picks = []
    for path in sorted(INBOX_DIR.glob("*.pick")):
        try:
            content = path.read_text().strip()
        finally:
            path.unlink(missing_ok=True)
        if content in valid_names:
            picks.append(content)
    return picks
