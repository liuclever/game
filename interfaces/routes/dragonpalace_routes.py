"""
龙宫之谜（活动副本）路由
接口层：鉴权、参数解析、调用应用服务、格式化输出
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from interfaces.web_api.bootstrap import services
from application.services.dragonpalace_service import DragonPalaceError
from application.services.inventory_service import InventoryError

dragonpalace_bp = Blueprint("dragonpalace", __name__, url_prefix="/api/dragonpalace")


def get_current_user_id() -> int:
    return session.get("user_id", 0)


@dragonpalace_bp.get("/status")
def status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    return jsonify(services.dragonpalace_service.get_status(user_id=user_id))


@dragonpalace_bp.post("/reset")
def reset_today():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    try:
        return jsonify(services.dragonpalace_service.reset_today(user_id=user_id))
    except DragonPalaceError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@dragonpalace_bp.post("/challenge")
def challenge():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    try:
        return jsonify(services.dragonpalace_service.challenge(user_id=user_id))
    except DragonPalaceError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@dragonpalace_bp.get("/report")
def report():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    try:
        stage = int(request.args.get("stage", "0") or "0")
    except Exception:
        stage = 0
    try:
        return jsonify(services.dragonpalace_service.get_report(user_id=user_id, stage=stage))
    except DragonPalaceError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@dragonpalace_bp.post("/claim")
def claim():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    data = request.get_json() or {}
    try:
        stage = int(data.get("stage", 0) or 0)
    except Exception:
        stage = 0
    try:
        return jsonify(services.dragonpalace_service.claim_reward(user_id=user_id, stage=stage))
    except DragonPalaceError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@dragonpalace_bp.get("/petinfo")
def petinfo():
    """
    关卡详情（抄写配置，不请求外站）。
    前端约定：type=1/2/3 分别对应 海龙门/龙宫城/龙殿。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        stage_type = int(request.args.get("type", "0") or "0")
    except Exception:
        stage_type = 0

    from infrastructure.config.dragonpalace_config import get_dragonpalace_config

    cfg = get_dragonpalace_config()
    stages = cfg.get("stages", []) or []
    stage_cfg = next((s for s in stages if int(s.get("stage", 0) or 0) == stage_type), None)
    if not isinstance(stage_cfg, dict):
        return jsonify({"ok": False, "error": "关卡不存在"}), 404

    enemies = []
    for e in (stage_cfg.get("enemies", []) or []):
        stats = e.get("stats", {}) or {}
        enemies.append({
            "name": str(e.get("name") or ""),
            "attack_type": str(e.get("attack_type") or ""),
            "hp": int(stats.get("hp", 0) or 0),
            "atk": int(stats.get("atk", 0) or 0),
            "def": int(stats.get("def", 0) or 0),
            "mdef": int(stats.get("mdef", 0) or 0),
            "speed": int(stats.get("speed", 0) or 0),
            "power": int(e.get("power", 0) or 0),
            "skills": list(e.get("skills", []) or []),
        })

    return jsonify({
        "ok": True,
        "stage": int(stage_cfg.get("stage", stage_type) or stage_type),
        "name": str(stage_cfg.get("name") or ""),
        "enemies": enemies,
    })


@dragonpalace_bp.post("/open-gift")
def open_gift():
    """
    打开“龙宫之谜探索礼包”（通常在临时背包里）。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    try:
        inv_item_id = int(data.get("inv_item_id", 0) or 0)
    except Exception:
        inv_item_id = 0

    open_all = bool(data.get("open_all", False))
    try:
        open_count = int(data.get("open_count", 1) or 1)
    except Exception:
        open_count = 1

    if inv_item_id <= 0:
        return jsonify({"ok": False, "error": "inv_item_id 必填"}), 400

    try:
        payload = services.inventory_service.open_dragonpalace_explore_gift(
            user_id=user_id,
            inv_item_id=inv_item_id,
            open_count=open_count,
            open_all=open_all,
            consume=True,
        )
        return jsonify(payload)
    except (InventoryError, DragonPalaceError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "error": "打开失败"}), 400


