from flask import Blueprint, request, jsonify, current_app
import pandas as pd
from middleware.security import validate_session_id
from utils.session_manager import get_session_manager
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)

def _load(sid):
    if not validate_session_id(sid): return None, (jsonify({"error":"Invalid session ID.","code":"INVALID_SESSION"}), 400)
    mgr  = get_session_manager(current_app.config["UPLOAD_FOLDER"])
    path = mgr.get_file_path(sid)
    if not path: return None, (jsonify({"error":"Session not found or expired.","code":"NOT_FOUND"}), 404)
    try:
        mgr.touch(sid)
        return pd.read_csv(path), None
    except Exception as e:
        return None, (jsonify({"error":"Could not read data.","code":"READ_ERROR"}), 500)

@analytics_bp.route("/analytics/kpis",           methods=["GET"])
def kpis():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    return jsonify({"success": True, "data": AnalyticsService(df).get_kpis()})

@analytics_bp.route("/analytics/revenue-trend",  methods=["GET"])
def revenue_trend():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    return jsonify({"success": True, "data": AnalyticsService(df).get_revenue_trend()})

@analytics_bp.route("/analytics/forecast",       methods=["GET"])
def forecast():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    return jsonify({"success": True, "data": AnalyticsService(df).get_forecast(min(int(request.args.get("periods",3)),12))})

@analytics_bp.route("/analytics/suppliers",      methods=["GET"])
def suppliers():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    return jsonify({"success": True, "data": AnalyticsService(df).get_supplier_scorecard(min(int(request.args.get("top_n",10)),50))})

@analytics_bp.route("/analytics/risks",          methods=["GET"])
def risks():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    return jsonify({"success": True, "data": AnalyticsService(df).get_risk_alerts()})

@analytics_bp.route("/analytics/full",           methods=["GET"])
def full():
    df, err = _load(request.args.get("session_id","demo"))
    if err: return err
    svc = AnalyticsService(df)
    return jsonify({"success": True, "data": {"kpis": svc.get_kpis(), "revenue_trend": svc.get_revenue_trend(), "forecast": svc.get_forecast(), "suppliers": svc.get_supplier_scorecard(), "risks": svc.get_risk_alerts()}})
