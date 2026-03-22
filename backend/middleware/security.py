from flask import request, jsonify, g
import os, re, uuid, time, hashlib

def apply_security_headers(response):
    response.headers["X-Content-Type-Options"]  = "nosniff"
    response.headers["X-Frame-Options"]         = "DENY"
    response.headers["X-XSS-Protection"]        = "1; mode=block"
    response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"]           = "no-store, no-cache, must-revalidate"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'none'; object-src 'none'; frame-ancestors 'none';"
    response.headers.pop("Server", None)
    return response

def attach_request_id():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.monotonic()

def log_request_completion(response):
    ms = round((time.monotonic() - g.get("start_time", time.monotonic())) * 1000, 1)
    print(f"[{g.get('request_id','-')}] {request.method} {request.path} → {response.status_code} ({ms}ms)")
    response.headers["X-Request-Id"] = g.get("request_id", "-")
    return response

def enforce_content_type():
    if request.path == "/api/ai/chat" and request.method == "POST":
        if not (request.content_type or "").startswith("application/json"):
            return jsonify({"error": "Content-Type must be application/json", "code": "INVALID_CONTENT_TYPE"}), 415

def check_request_size():
    if request.method in ("POST", "PUT") and request.content_length:
        if "application/json" in (request.content_type or "") and request.content_length > 64 * 1024:
            return jsonify({"error": "Request body too large", "code": "PAYLOAD_TOO_LARGE"}), 413

SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9_\-\.]")

def sanitize_filename(filename):
    base = os.path.basename(filename)
    base = SAFE_FILENAME_RE.sub("_", base).lstrip(".")[:100]
    return base or "upload"

def safe_join(base_dir, *parts):
    base   = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base, *parts))
    if not target.startswith(base + os.sep) and target != base:
        raise ValueError(f"Path traversal detected")
    return target

SESSION_ID_RE = re.compile(r"^[a-f0-9]{8}$|^demo$")

def validate_session_id(session_id):
    return bool(SESSION_ID_RE.match(str(session_id)))

def mask_api_key(key):
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-4:]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
