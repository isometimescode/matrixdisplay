"""Small persisted app setting: which timezone the clock animation
displays in. Lives beside the inbox (daemon/inbox.py) in the same shared
tmpfs directory, so it's readable/writable by both the web app (user
`pi`) and the daemon (user `daemon`, post-privilege-drop) without any
extra provisioning -- but it resets on reboot rather than surviving a
power cycle, since tmpfs doesn't persist. That's an acceptable trade for
an appliance that's powered on per event: the web UI's "use my phone's
time zone" button makes re-syncing a one-tap fix rather than an SSH
session.
"""

import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_DEFAULT_SETTINGS_FILE = (
    Path(__file__).resolve().parent.parent / "var" / "settings.json"
)
SETTINGS_FILE = Path(
    os.environ.get("MATRIXDISPLAY_SETTINGS_FILE", _DEFAULT_SETTINGS_FILE)
)

DEFAULT_TIMEZONE = "America/Los_Angeles"


def is_valid_timezone(tz_name):
    try:
        ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        return False
    return True


def get_timezone():
    """The currently-set timezone name, falling back to the default if
    nothing's been set yet or the stored value is no longer valid."""
    try:
        data = json.loads(SETTINGS_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_TIMEZONE
    tz = data.get("timezone")
    return tz if tz and is_valid_timezone(tz) else DEFAULT_TIMEZONE


def set_timezone(tz_name):
    """Atomically persist `tz_name` (an IANA zone key, e.g.
    "America/Denver") as the current timezone."""
    if not is_valid_timezone(tz_name):
        raise ValueError(f"Unknown timezone: {tz_name}")
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = SETTINGS_FILE.with_name(f".{SETTINGS_FILE.name}.tmp")
    tmp_path.write_text(json.dumps({"timezone": tz_name}))
    os.rename(tmp_path, SETTINGS_FILE)  # atomic on POSIX, same filesystem
