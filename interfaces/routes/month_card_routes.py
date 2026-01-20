from flask import Blueprint, jsonify, session

from application.services.month_card_service import MonthCardError
from interfaces.web_api.bootstrap import services


month_card_bp = Blueprint("month_card", __name__, url_prefix="/api/sponsor/month-card")


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@month_card_bp.get("/status")
def get_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "未登录"}), 401

    try:
        data = services.month_card_service.get_status(user_id)
        return jsonify({"ok": True, "data": data})
    except MonthCardError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@month_card_bp.post("/purchase")
def purchase():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "未登录"}), 401

    try:
        result = services.month_card_service.purchase(user_id)
        return jsonify({"ok": True, "data": result})
    except MonthCardError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@month_card_bp.post("/claim")
def claim():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "未登录"}), 401

    try:
        result = services.month_card_service.claim_daily_reward(user_id)
        return jsonify({"ok": True, "data": result})
    except MonthCardError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
