from flask import Blueprint, jsonify, session, request

from application.services.inventory_service import InventoryError
from application.services.exchange_service import ExchangeError
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

def get_current_user_id() -> int:
    return session.get('user_id', 0)


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

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "qinglong"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/qinglong')
def exchange_qinglong():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "qinglong"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/jueying/status')
def get_jueying_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "jueying"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/jueying')
def exchange_jueying():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "jueying"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/baihu/status')
def get_baihu_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "baihu"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/baihu')
def exchange_baihu():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "baihu"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/businiao/status')
def get_businiao_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "businiao"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/businiao')
def exchange_businiao():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "businiao"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/luosha/status')
def get_luosha_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "luosha"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@exchange_bp.post('/beast/luosha')
def exchange_luosha():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "luosha"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/xuanwu/status')
def get_xuanwu_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "xuanwu"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/xuanwu')
def exchange_xuanwu():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "xuanwu"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/beast/zhuque/status')
def get_zhuque_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.get_divine_beast_status(user_id, "zhuque"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.post('/beast/zhuque')
def exchange_zhuque():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        return jsonify(services.exchange_service.exchange_divine_beast(user_id, "zhuque"))
    except ExchangeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@exchange_bp.get('/item/nilin/status')
def get_nilin_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    inventory_service = services.inventory_service
    current_nilin = inventory_service.get_item_count(user_id, SHEN_NILIN_ITEM_ID)

    return jsonify({
        "ok": True,
        "current_nilin": current_nilin,
    })


@exchange_bp.post('/item/nilin')
def exchange_nilin():
    # 按需求：神·逆鳞碎片(3011) -> 神·逆鳞(3010) 的兑换不提供“兑换页按钮”；
    # 统一走背包内“使用碎片自动合成”的方式。
    return jsonify({"ok": False, "error": "神·逆鳞碎片请在背包内直接合成（集齐100块自动合成1块）"}), 400
