"""
古树模块路由（Interfaces 层）。

仅负责：
- 读取 session 中的 user_id；
- 参数解析；
- 调用 TreeService；
- 统一返回 JSON。
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from application.services.tree_service import TreeError
from interfaces.web_api.bootstrap import services


tree_bp = Blueprint("tree", __name__, url_prefix="/api")


def get_current_user_id() -> int:
    return session.get("user_id", 0)


@tree_bp.get("/tree/status")
def tree_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    data = services.tree_service.get_status(user_id=user_id)
    return jsonify({"ok": True, **data})


@tree_bp.post("/tree/draw")
def tree_draw():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    try:
        data = services.tree_service.draw_today_number(user_id=user_id)
        return jsonify({"ok": True, **data})
    except TreeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@tree_bp.post("/tree/claim")
def tree_claim():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    try:
        data = services.tree_service.claim_week_reward(user_id=user_id)
        return jsonify({"ok": True, **data})
    except TreeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


