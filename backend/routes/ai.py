from flask import Blueprint, request, jsonify, current_app
import pandas as pd, json, urllib.request, urllib.error, re
from middleware.security import validate_session_id
from utils.session_manager import get_session_manager
from services.analytics_service import AnalyticsService

ai_bp = Blueprint("ai", __name__)

SYSTEM_PROMPT = """You are ChainSense AI — an expert supply chain analyst.
Rules:
- Ground every answer in the data provided. Never fabricate numbers.
- Flag risks with severity: Low / Medium / High.
- Keep responses direct: 2-4 sentences simple, up to 8 for deep analysis.
- If a chart helps, end with exactly: CHART_SUGGESTION: <type> | <x_field> | <y_field>
  Valid types: bar, line, pie, scatter
- If data is insufficient, say so honestly.
"""

_DANGEROUS = re.compile(r"[<>{}\[\]\\]")
MAX_MSG    = 1000
MAX_HIST   = 10

def _sanitize(text): return _DANGEROUS.sub("", text)[:MAX_MSG].strip()

def _call_claude(messages, system, key, model, max_tokens):
    payload = json.dumps({"model": model, "max_tokens": max_tokens, "system": system, "messages": messages}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["content"][0]["text"]
    except urllib.error.HTTPError as e:
        code = e.code
        current_app.logger.error(f"Claude API {code}")
        if code == 401: return "AI authentication failed. Check your API key."
        if code == 429: return "AI service busy. Wait a moment and retry."
        return "AI service error. Try again shortly."
    except Exception as e:
        current_app.logger.error(f"Claude request failed: {e}")
        return "Could not reach AI service."

def _parse_chart(reply):
    if "CHART_SUGGESTION:" not in reply: return reply, None
    parts = reply.split("CHART_SUGGESTION:", 1)
    try:
        cp = [p.strip() for p in parts[1].strip().split("|")]
        return parts[0].strip(), {"type": cp[0] if cp else None, "x_field": cp[1] if len(cp)>1 else None, "y_field": cp[2] if len(cp)>2 else None}
    except: return parts[0].strip(), None

@ai_bp.route("/ai/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True)
    if not body: return jsonify({"error":"Invalid JSON.","code":"BAD_REQUEST"}), 400
    msg, sid, hist = body.get("message","").strip(), body.get("session_id","demo"), body.get("history",[])
    if not msg: return jsonify({"error":"Message empty.","code":"EMPTY_MESSAGE"}), 400
    if not validate_session_id(sid): return jsonify({"error":"Invalid session ID.","code":"INVALID_SESSION"}), 400
    msg = _sanitize(msg)
    if not msg: return jsonify({"error":"Message has invalid characters.","code":"INVALID_MESSAGE"}), 400
    mgr  = get_session_manager(current_app.config["UPLOAD_FOLDER"])
    path = mgr.get_file_path(sid)
    if not path: return jsonify({"error":"Session not found or expired.","code":"NOT_FOUND"}), 404
    try:
        df = pd.read_csv(path); mgr.touch(sid)
    except Exception as e:
        return jsonify({"error":"Could not load data.","code":"DATA_ERROR"}), 500
    key = current_app.config.get("ANTHROPIC_API_KEY","")
    if not key:
        return jsonify({"success":True,"reply":"Add ANTHROPIC_API_KEY to .env to enable AI features.","chart_suggestion":None})
    svc      = AnalyticsService(df)
    system   = f"{SYSTEM_PROMPT}\n\n{svc.build_ai_context()}"
    safe_hist = [{"role": t["role"], "content": str(t["content"])[:2000]}
                 for t in hist[-MAX_HIST:] if t.get("role") in ("user","assistant") and t.get("content")]
    messages = safe_hist + [{"role":"user","content":msg}]
    raw      = _call_claude(messages, system, key, current_app.config["CLAUDE_MODEL"], current_app.config["CLAUDE_MAX_TOKENS"])
    reply, chart = _parse_chart(raw)
    return jsonify({"success":True,"reply":reply,"chart_suggestion":chart})
