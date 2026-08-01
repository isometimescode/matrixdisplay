"""Flask app: mobile-first page listing the daemon's animations, tap to
queue one as the next thing played on the real panel.

Run against the emulator/dev daemon:
    python -m web.run
"""

from flask import Flask, redirect, render_template, request, url_for

from daemon.inbox import MAX_TEXT_LEN, drop_pick, drop_text_pick
from daemon.run import SEQUENCE
from daemon.settings import get_timezone, set_timezone

ANIMATION_NAMES = [module.__name__.rsplit(".", 1)[-1] for module in SEQUENCE]


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        queued = request.args.get("queued")
        if queued not in ANIMATION_NAMES:
            queued = None
        queued_text = request.args.get("queued_text")
        return render_template(
            "index.html",
            animations=ANIMATION_NAMES,
            queued=queued,
            queued_text=queued_text,
            max_text_len=MAX_TEXT_LEN,
            current_timezone=get_timezone(),
        )

    @app.post("/play/<name>")
    def play(name):
        if name not in ANIMATION_NAMES:
            return "Unknown animation", 404
        drop_pick(name)
        return redirect(url_for("index", queued=name))

    @app.post("/play-text")
    def play_text():
        text = request.form.get("text", "").strip()[:MAX_TEXT_LEN]
        if not text:
            return redirect(url_for("index"))
        drop_text_pick(text)
        return redirect(url_for("index", queued_text=text))

    @app.post("/settings/timezone")
    def update_timezone():
        tz = request.form.get("timezone", "").strip()
        if tz:
            try:
                set_timezone(tz)
            except ValueError:
                pass
        return redirect(url_for("index"))

    return app
