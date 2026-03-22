import os
from flask import send_from_directory, send_file

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "static_frontend")

def register_frontend(app):
    if not os.path.isdir(FRONTEND_DIR):
        return

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "assets"), filename)

    @app.route("/favicon.svg")
    def serve_favicon():
        return send_from_directory(FRONTEND_DIR, "favicon.svg")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        full = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(full):
            return send_from_directory(FRONTEND_DIR, path)
        return send_file(os.path.join(FRONTEND_DIR, "index.html"))
