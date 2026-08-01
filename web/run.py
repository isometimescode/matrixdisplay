"""Entrypoint for `python -m web.run`, matching the systemd unit's
ExecStart (see systemd/matrixdisplay-web.service)."""

from web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
