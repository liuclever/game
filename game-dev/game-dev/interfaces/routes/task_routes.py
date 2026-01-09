from flask import Blueprint, jsonify, request, session

from interfaces.web_api.bootstrap import services
from application.services.task_reward_service import TaskRewardError
from application.services.activity_gift_service import ActivityGiftError

task_bp = Blueprint("task", __name__, url_prefix="/api/task")


def _current_user_id() -> int:
    return session.get("user_id", 0)


@task_bp.get("/reward/status")
def get_task_reward_status():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    rewards = services.task_reward_service.list_rewards(user_id)
    return jsonify({"ok": True, "rewards": rewards})


@task_bp.get("/daily_activity")
def get_daily_activity():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = services.daily_activity_service.get_activity_data(user_id)
    return jsonify({"ok": True, "data": data})


@task_bp.post("/reward/claim")
def claim_task_reward():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    reward_key = data.get("key") or data.get("type")
    if not reward_key:
        return jsonify({"ok": False, "error": "缺少奖励类型"}), 400

    try:
        result = services.task_reward_service.claim_reward(user_id, reward_key)
        return jsonify(result)
    except TaskRewardError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@task_bp.post("/activity_gift/claim")
def claim_activity_gift():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    gift_key = data.get("key")
    if not gift_key:
        return jsonify({"ok": False, "error": "缺少礼包标识"}), 400

    try:
        result = services.activity_gift_service.claim_gift(user_id, gift_key)
        return jsonify(result)
    except ActivityGiftError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
