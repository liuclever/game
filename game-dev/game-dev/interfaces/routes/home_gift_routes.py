from flask import Blueprint, jsonify, request, session

from interfaces.web_api.bootstrap import services
from application.services.home_gift_service import HomeGiftError


gifts_bp = Blueprint('gifts', __name__, url_prefix='/api/gifts')


def _current_user_id() -> int:
    return session.get('user_id', 0)


@gifts_bp.get('/list')
def list_gifts():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(services.home_gift_service.list_gifts(user_id))


@gifts_bp.post('/claim')
def claim_gift():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json(silent=True) or {}
    gift_key = data.get('key')
    if not gift_key:
        return jsonify({"ok": False, "error": "缺少礼包标识"}), 400

    try:
        result = services.home_gift_service.claim(user_id, gift_key)
        return jsonify(result)
    except HomeGiftError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
