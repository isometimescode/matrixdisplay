"""Flask app: mobile-first page listing the daemon's animations, tap to
queue one as the next thing played on the real panel.

Run against the emulator/dev daemon:
    python -m web.run
"""

from flask import Flask, redirect, render_template, request, url_for

from daemon.inbox import drop_pick
from daemon.run import SEQUENCE

ANIMATION_NAMES = [module.__name__.rsplit(".", 1)[-1] for module in SEQUENCE]


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        queued = request.args.get("queued")
        if queued not in ANIMATION_NAMES:
            queued = None
        return render_template("index.html", animations=ANIMATION_NAMES, queued=queued)

    @app.post("/play/<name>")
    def play(name):
        if name not in ANIMATION_NAMES:
            return "Unknown animation", 404
        drop_pick(name)
        return redirect(url_for("index", queued=name))

    return app
