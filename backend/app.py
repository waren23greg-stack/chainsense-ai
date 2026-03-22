import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from config.settings import get_config
from middleware.security import apply_security_headers, attach_request_id, log_request_completion, enforce_content_type, check_request_size
from serve_frontend import register_frontend
from utils.session_manager import get_session_manager

load_dotenv()

def create_app():
    app = Flask(__name__)
    cfg = get_config()
    app.config.from_object(cfg)
    for w in cfg.validate(): app.logger.warning(f"CONFIG: {w}")
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=False, allow_headers=["Content-Type","X-Request-Id"], methods=["GET","POST","DELETE","OPTIONS"])
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[app.config["RATELIMIT_DEFAULT"]], storage_uri=app.config["RATELIMIT_STORAGE_URI"], headers_enabled=True)
    app.before_request(attach_request_id)
    app.before_request(enforce_content_type)
    app.before_request(check_request_size)
    app.after_request(apply_security_headers)
    app.after_request(log_request_completion)
    from routes.upload    import upload_bp
    from routes.analytics import analytics_bp
    from routes.ai        import ai_bp
    app.register_blueprint(upload_bp,    url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(ai_bp,        url_prefix="/api")
    limiter.limit(app.config["RATELIMIT_UPLOAD"])(upload_bp)
    limiter.limit(app.config["RATELIMIT_AI"])(ai_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status":"ok","version":"1.0.0","env":app.config["FLASK_ENV"],"active_sessions":get_session_manager(app.config["UPLOAD_FOLDER"]).active_count()})

    @app.errorhandler(400)
    def bad_request(e):   return jsonify({"error":"Bad request.","code":"BAD_REQUEST"}), 400
    @app.errorhandler(404)
    def not_found(e):     return jsonify({"error":"Not found.","code":"NOT_FOUND"}), 404
    @app.errorhandler(413)
    def too_large(e):     return jsonify({"error":f"File too large. Max {app.config['MAX_CONTENT_LENGTH']//(1024*1024)}MB.","code":"TOO_LARGE"}), 413
    @app.errorhandler(429)
    def rate_limited(e):  return jsonify({"error":"Too many requests.","code":"RATE_LIMITED"}), 429
    @app.errorhandler(500)
    def server_error(e):  return jsonify({"error":"Internal server error.","code":"SERVER_ERROR"}), 500

    get_session_manager(app.config["UPLOAD_FOLDER"], app.config["SESSION_TTL"])
    register_frontend(app)
    app.logger.info(f"ChainSense API ready — {app.config['FLASK_ENV']}")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=(os.getenv("FLASK_ENV","production")=="development"))
