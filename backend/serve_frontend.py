import os
from flask import send_from_directory, send_file

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "static_frontend")

def register_frontend(app):
    if not os.path.isdir(FRONTEND_DIR):
        return

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        full = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(full):
            return send_from_directory(FRONTEND_DIR, path)
        return send_file(os.path.join(FRONTEND_DIR, "index.html"))
