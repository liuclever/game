# interfaces/routes/dev_routes.py
"""开发/测试用接口（仅测试模式启用）。

注意：
- 这些接口用于快速验证玩法逻辑（例如：给玩家加声望后能否晋级）。
- 正式模式下会拒绝访问。
"""

from flask import Blueprint, request, jsonify, session

from application.services.auth_service import is_test_mode
from interfaces.web_api.bootstrap import services
from infrastructure.db.connection import execute_update


dev_bp = Blueprint("dev", __name__, url_prefix="/api/dev")

# 复用修行服务：用于返回最新晋级状态
_cultivation_service = services.cultivation_service


def _current_user_id() -> int:
    return int(session.get("user_id") or 0)


@dev_bp.post("/grant-prestige")
def grant_prestige():
    """给当前登录玩家增加声望（用于测试晋级）。

    body: {"amount": 1000}
    """
    if not is_test_mode():
        # 不在测试模式时直接拒绝（避免正式环境被滥用）
        return jsonify({"ok": False, "error": "dev api disabled"}), 404

    user_id = _current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    try:
        amount = int(data.get("amount", 0))
    except Exception:
        amount = 0

    if amount <= 0:
        return jsonify({"ok": False, "error": "amount 必须是正整数"}), 400

    execute_update(
        "UPDATE player SET prestige = prestige + %s WHERE user_id = %s",
        (amount, user_id),
    )

    status = _cultivation_service.get_cultivation_status(user_id)
    return jsonify({
        "ok": True,
        "added": amount,
        "status": status,
    })
