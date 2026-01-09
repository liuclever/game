from flask import Blueprint, jsonify, session, request

from application.services.inventory_service import InventoryError
from interfaces.web_api.bootstrap import services

exchange_bp = Blueprint('exchange', __name__, url_prefix='/api/exchange')

SHEN_NILIN_ITEM_ID = 3010
SHEN_NILIN_FRAGMENT_ITEM_ID = 3011
NILIN_EXCHANGE_COST = 100

GOD_HERB_ITEM_ID = 3012
GOD_HERB_FRAGMENT_ITEM_ID = 3013
GOD_HERB_EXCHANGE_COST = 20

GOD_CRYSTAL_ITEM_ID = 3014
GOD_CRYSTAL_EXCHANGE_COST = 30

QINGLONG_REQUIRED = 12
QINGLONG_BALL_ITEM_ID = 26064

XUANWU_REQUIRED = 10
XUANWU_BALL_ITEM_ID = 26063

ZHUQUE_REQUIRED = 10
ZHUQUE_BALL_ITEM_ID = 26062

JUEYING_REQUIRED = 8
JUEYING_BALL_ITEM_ID = 26061

BAIHU_REQUIRED = 6
BAIHU_BALL_ITEM_ID = 26058

BUSINIAO_REQUIRED = 4
BUSINIAO_BALL_ITEM_ID = 26059

LUOSHA_REQUIRED = 6
LUOSHA_BALL_ITEM_ID = 26060


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _build_status_response(required: int, ball_item_id: int, user_id: int):
    inventory_service = services.inventory_service
    current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID)
    ball_count = inventory_service.get_item_count(user_id, ball_item_id)

    return {
        "ok": True,
        "required": required,
        "current_nilin": current_nilin,
        "has_ball": ball_count > 0,
        "can_exchange": current_nilin >= required,
    }


def _exchange_beast(required: int, ball_item_id: int, success_message: str, user_id: int):
    inventory_service = services.inventory_service

    if not inventory_service.has_item(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID, required):
        return jsonify({"ok": False, "error": f"神·逆鳞不足（需要{required}块）"}), 400

    try:
        inventory_service.remove_item(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID, required)
        inventory_service.add_item(user_id, ball_item_id, 1)
    except InventoryError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "message": success_message,
        "current_nilin": current_nilin,
    })


@exchange_bp.get('/item/god-herb/status')
def get_god_herb_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    inventory_service = services.inventory_service
    current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "current_fragment": current_fragment,
    })


@exchange_bp.get('/item/god-crystal/status')
def get_god_crystal_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    inventory_service = services.inventory_service
    current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "current_fragment": current_fragment,
    })


@exchange_bp.post('/item/god-crystal')
def exchange_god_crystal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    payload = request.get_json(silent=True) or {}
    try:
        exchange_count = int(payload.get('count', 1))
    except (TypeError, ValueError):
        exchange_count = 1

    if exchange_count < 1:
        exchange_count = 1

    total_cost = GOD_CRYSTAL_EXCHANGE_COST * exchange_count

    inventory_service = services.inventory_service
    if not inventory_service.has_item(user_id, GOD_HERB_FRAGMENT_ITEM_ID, total_cost):
        current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)
        return jsonify({
            "ok": False,
            "error": f"进化碎片不足，需要{total_cost}个（当前：{current_fragment}个）",
        }), 400

    try:
        inventory_service.remove_item(user_id, GOD_HERB_FRAGMENT_ITEM_ID, total_cost)
        inventory_service.add_item(user_id, GOD_CRYSTAL_ITEM_ID, exchange_count)
    except InventoryError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "message": f"兑换成功，获得进化圣水晶×{exchange_count}",
        "current_fragment": current_fragment,
    })


@exchange_bp.post('/item/god-herb')
def exchange_god_herb():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    payload = request.get_json(silent=True) or {}
    try:
        exchange_count = int(payload.get('count', 1))
    except (TypeError, ValueError):
        exchange_count = 1

    if exchange_count < 1:
        exchange_count = 1

    total_cost = GOD_HERB_EXCHANGE_COST * exchange_count

    inventory_service = services.inventory_service
    if not inventory_service.has_item(user_id, GOD_HERB_FRAGMENT_ITEM_ID, total_cost):
        current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)
        return jsonify({
            "ok": False,
            "error": f"进化碎片不足，需要{total_cost}个（当前：{current_fragment}个）",
        }), 400

    try:
        inventory_service.remove_item(user_id, GOD_HERB_FRAGMENT_ITEM_ID, total_cost)
        inventory_service.add_item(user_id, GOD_HERB_ITEM_ID, exchange_count)
    except InventoryError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    current_fragment = inventory_service.get_item_count(user_id, GOD_HERB_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "message": f"兑换成功，获得进化神草×{exchange_count}",
        "current_fragment": current_fragment,
    })


@exchange_bp.get('/beast/qinglong/status')
def get_qinglong_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(QINGLONG_REQUIRED, QINGLONG_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/qinglong')
def exchange_qinglong():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=QINGLONG_REQUIRED,
        ball_item_id=QINGLONG_BALL_ITEM_ID,
        success_message="兑换成功，获得神·青龙召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/jueying/status')
def get_jueying_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(JUEYING_REQUIRED, JUEYING_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/jueying')
def exchange_jueying():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=JUEYING_REQUIRED,
        ball_item_id=JUEYING_BALL_ITEM_ID,
        success_message="兑换成功，获得神·绝影召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/baihu/status')
def get_baihu_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(BAIHU_REQUIRED, BAIHU_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/baihu')
def exchange_baihu():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=BAIHU_REQUIRED,
        ball_item_id=BAIHU_BALL_ITEM_ID,
        success_message="兑换成功，获得神·白虎召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/businiao/status')
def get_businiao_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(BUSINIAO_REQUIRED, BUSINIAO_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/businiao')
def exchange_businiao():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=BUSINIAO_REQUIRED,
        ball_item_id=BUSINIAO_BALL_ITEM_ID,
        success_message="兑换成功，获得神·不死鸟召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/luosha/status')
def get_luosha_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(LUOSHA_REQUIRED, LUOSHA_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/luosha')
def exchange_luosha():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=LUOSHA_REQUIRED,
        ball_item_id=LUOSHA_BALL_ITEM_ID,
        success_message="兑换成功，获得神·罗刹召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/xuanwu/status')
def get_xuanwu_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(XUANWU_REQUIRED, XUANWU_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/xuanwu')
def exchange_xuanwu():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=XUANWU_REQUIRED,
        ball_item_id=XUANWU_BALL_ITEM_ID,
        success_message="兑换成功，获得神·玄武召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/beast/zhuque/status')
def get_zhuque_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return jsonify(_build_status_response(ZHUQUE_REQUIRED, ZHUQUE_BALL_ITEM_ID, user_id))


@exchange_bp.post('/beast/zhuque')
def exchange_zhuque():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    return _exchange_beast(
        required=ZHUQUE_REQUIRED,
        ball_item_id=ZHUQUE_BALL_ITEM_ID,
        success_message="兑换成功，获得神·朱雀召唤球×1",
        user_id=user_id,
    )


@exchange_bp.get('/item/nilin/status')
def get_nilin_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    inventory_service = services.inventory_service
    current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "current_nilin": current_nilin,
    })


@exchange_bp.post('/item/nilin')
def exchange_nilin():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    payload = request.get_json(silent=True) or {}
    try:
        exchange_count = int(payload.get('count', 1))
    except (TypeError, ValueError):
        exchange_count = 1

    if exchange_count < 1:
        exchange_count = 1

    total_cost = NILIN_EXCHANGE_COST * exchange_count

    inventory_service = services.inventory_service
    if not inventory_service.has_item(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID, total_cost):
        current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID)
        return jsonify({
            "ok": False,
            "error": f"神·逆鳞碎片不足，需要{total_cost}块（当前：{current_nilin}块）",
        }), 400

    try:
        inventory_service.remove_item(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID, total_cost)
        inventory_service.add_item(user_id, SHEN_NILIN_ITEM_ID, exchange_count)
    except InventoryError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_FRAGMENT_ITEM_ID)

    return jsonify({
        "ok": True,
        "message": f"兑换成功，获得神·逆鳞×{exchange_count}",
        "current_nilin": current_nilin,
    })
