from flask import Blueprint, request, jsonify, current_app
import os, pandas as pd
from middleware.security import sanitize_filename, safe_join, sha256_file
from utils.csv_validator import validate_csv_upload, ValidationError, detect_column_roles
from utils.session_manager import get_session_manager

upload_bp = Blueprint("upload", __name__)

def _mgr(): return get_session_manager(current_app.config["UPLOAD_FOLDER"], current_app.config["SESSION_TTL"])

def _summary(df, sid, fname):
    return {"session_id": sid, "filename": fname, "rows": len(df), "columns": len(df.columns),
            "column_names": df.columns.tolist(), "detected_roles": detect_column_roles(df),
            "null_counts": {k: int(v) for k,v in df.isnull().sum().items()},
            "preview": df.head(8).fillna("").to_dict(orient="records"),
            "memory_kb": round(df.memory_usage(deep=True).sum() / 1024, 1)}

@upload_bp.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files: return jsonify({"error":"No file field.","code":"MISSING_FILE"}), 400
    file = request.files["file"]
    if not file or file.filename == "": return jsonify({"error":"No file selected.","code":"EMPTY_FILENAME"}), 400
    ext = file.filename.rsplit(".",1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]: return jsonify({"error":f"Only CSV accepted. Got .{ext}","code":"INVALID_EXTENSION"}), 400
    try:
        df = validate_csv_upload(file)
    except ValidationError as e:
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 422
    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return jsonify({"error":"Upload failed.","code":"SERVER_ERROR"}), 500
    mgr = _mgr()
    sid = mgr.create_session(sanitize_filename(file.filename), "")
    try:
        dest = safe_join(current_app.config["UPLOAD_FOLDER"], f"upload_{sid}.csv")
        df.to_csv(dest, index=False)
        mgr._store[sid]["file_hash"] = sha256_file(dest)
    except Exception as e:
        current_app.logger.error(f"Save error: {e}")
        return jsonify({"error":"Could not save file.","code":"SAVE_ERROR"}), 500
    return jsonify({"success": True, "data": _summary(df, sid, sanitize_filename(file.filename))}), 201

@upload_bp.route("/demo", methods=["GET"])
def load_demo():
    p = os.path.join(current_app.config["UPLOAD_FOLDER"], "demo.csv")
    if not os.path.isfile(p): return jsonify({"error":"Demo not found. Run generate_demo.py.","code":"DEMO_MISSING"}), 404
    try:
        df = pd.read_csv(p)
        return jsonify({"success": True, "data": _summary(df, "demo", "supply_chain_demo.csv")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route("/session/<sid>", methods=["GET"])
def session_info(sid):
    from middleware.security import validate_session_id
    if not validate_session_id(sid): return jsonify({"error":"Invalid session ID."}), 400
    info = _mgr().session_info(sid)
    if not info: return jsonify({"error":"Session not found or expired."}), 404
    return jsonify({"success": True, "data": info})

@upload_bp.route("/session/<sid>", methods=["DELETE"])
def delete_session(sid):
    from middleware.security import validate_session_id
    if not validate_session_id(sid): return jsonify({"error":"Invalid session ID."}), 400
    deleted = _mgr().delete_session(sid)
    if not deleted: return jsonify({"error":"Session not found."}), 404
    return jsonify({"success": True, "message": f"Session {sid} deleted."})
