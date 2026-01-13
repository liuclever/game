# interfaces/routes/spirit_routes.py
"""战灵系统路由"""

from flask import Blueprint, jsonify, session, request
from interfaces.web_api.bootstrap import services
from application.services.spirit_service import SpiritError


spirit_bp = Blueprint('spirit', __name__, url_prefix='/api/spirit')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@spirit_bp.get("/account")
def get_account():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    acc = services.spirit_service.get_account(user_id)
    return jsonify({"ok": True, "account": acc.to_dict()})


@spirit_bp.post("/unlock-element")
def unlock_element():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    element = str(data.get("element", "") or "")
    if not element:
        return jsonify({"ok": False, "error": "element 必填"}), 400

    try:
        acc = services.spirit_service.unlock_element(user_id, element)
        return jsonify({"ok": True, "account": acc.to_dict()})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.get("/list")
def list_spirits():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    spirits = services.spirit_service.get_spirits(user_id)
    return jsonify({"ok": True, "spirits": [s.to_dict() for s in spirits]})


@spirit_bp.get("/warehouse")
def list_warehouse_spirits():
    """获取灵件室中的战灵（未装备的战灵）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    # 获取所有战灵，筛选出未装备的（beast_id 为 None）
    all_spirits = services.spirit_service.get_spirits(user_id)
    warehouse_spirits = [s for s in all_spirits if s.spirit.beast_id is None]

    # 获取仓库容量配置
    from infrastructure.config.spirit_system_config import get_spirit_system_config
    config = get_spirit_system_config()
    warehouse_capacity = config.get_warehouse_capacity()

    # 元素名称映射
    element_names = {
        "earth": "土",
        "fire": "火",
        "water": "水",
        "wood": "木",
        "metal": "金",
        "god": "神",
    }

    spirits_data = []
    for s in warehouse_spirits:
        sp = s.spirit
        element_name = element_names.get(sp.element, sp.element)
        spirit_display_name = f"{element_name}灵·{sp.race}"
        spirits_data.append({
            "id": sp.id,
            "name": spirit_display_name,
            "element": sp.element,
            "elementName": element_name,
            "race": sp.race,
            "lines": [ln.to_dict() for ln in sp.lines],
        })

    return jsonify({
        "ok": True,
        "spirits": spirits_data,
        "count": len(warehouse_spirits),
        "capacity": warehouse_capacity,
    })


@spirit_bp.get("/<int:spirit_id>")
def get_spirit(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    s = services.spirit_service.get_spirit(user_id, spirit_id)
    if s is None:
        return jsonify({"ok": False, "error": "战灵不存在"}), 404

    return jsonify({"ok": True, "spirit": s.to_dict()})


@spirit_bp.post("/open")
def open_stone():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    element = str(data.get("element", "") or "")
    quantity = int(data.get("quantity", 1) or 1)

    if not element:
        return jsonify({"ok": False, "error": "element 必填"}), 400

    try:
        created = services.spirit_service.open_stone(user_id, element, quantity)
        return jsonify({"ok": True, "created": [s.to_dict() for s in created]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/equip")
def equip_spirit(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    beast_id = int(data.get("beast_id", 0) or 0)
    if beast_id <= 0:
        return jsonify({"ok": False, "error": "beast_id 必填"}), 400

    try:
        s = services.spirit_service.equip_spirit(user_id, beast_id, spirit_id)
        return jsonify({"ok": True, "spirit": s.to_dict()})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/unequip")
def unequip_spirit(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        s = services.spirit_service.unequip_spirit(user_id, spirit_id)
        return jsonify({"ok": True, "spirit": s.to_dict()})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/unlock-line")
def unlock_line(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    line_index = int(data.get("line_index", 0) or 0)

    try:
        s = services.spirit_service.unlock_line(user_id, spirit_id, line_index)
        return jsonify({"ok": True, "spirit": s.to_dict()})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/lock-line")
def lock_line(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    line_index = int(data.get("line_index", 0) or 0)
    locked = bool(data.get("locked", False))

    try:
        s = services.spirit_service.set_line_lock(user_id, spirit_id, line_index, locked)
        return jsonify({"ok": True, "spirit": s.to_dict()})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/refine")
def refine(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        result = services.spirit_service.refine(user_id, spirit_id)
        return jsonify({"ok": True, **result})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/<int:spirit_id>/sell")
def sell(spirit_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        result = services.spirit_service.sell(user_id, spirit_id)
        return jsonify({"ok": True, **result})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.get("/page-data")
def get_spirit_page_data():
    """获取战灵页面所需的所有数据（幻兽列表 + 灵力 + 仓库信息）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    # 获取玩家战灵账户
    acc = services.spirit_service.get_account(user_id)

    player = services.player_repo.get_by_id(user_id)
    player_level = int(getattr(player, "level", 0) or 0) if player else 0

    # 获取所有战灵数量
    spirits = services.spirit_service.get_spirits(user_id)
    warehouse_count = len(spirits)

    # 获取仓库容量配置
    from infrastructure.config.spirit_system_config import get_spirit_system_config
    config = get_spirit_system_config()
    warehouse_capacity = config.get_warehouse_capacity()

    # 获取所有幻兽
    all_beasts = services.player_beast_repo.get_all_by_user(user_id)

    beast_list = [
        {
            "id": b.id,
            "name": b.name,
            "realm": b.realm,
            "level": b.level,
            "race": b.race,
        }
        for b in all_beasts
    ]

    return jsonify({
        "ok": True,
        "beasts": beast_list,
        "spiritPower": acc.spirit_power,
        "warehouseCount": warehouse_count,
        "warehouseCapacity": warehouse_capacity,
        "playerLevel": player_level,
        "unlockedElements": list(acc.unlocked_elements or []),
    })


@spirit_bp.post("/beast/<int:beast_id>/unequip-by-element")
def unequip_spirit_by_element(beast_id: int):
    """按元素槽位卸下战灵（战灵会返回灵件室）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    element = str(data.get("element", "") or "")
    if not element:
        return jsonify({"ok": False, "error": "element 必填"}), 400

    # 查找该幻兽在该元素槽位装备的战灵
    spirits = services.spirit_repo.get_by_beast_id(beast_id)
    target_spirit = None
    for sp in spirits:
        if sp.element == element:
            target_spirit = sp
            break

    if not target_spirit:
        return jsonify({"ok": False, "error": "该槽位没有装备战灵"}), 400

    # 验证所属权
    if target_spirit.user_id != user_id:
        return jsonify({"ok": False, "error": "无权限操作"}), 403

    try:
        s = services.spirit_service.unequip_spirit(user_id, target_spirit.id)
        return jsonify({"ok": True, "spirit": s.to_dict(), "message": "卸下成功，战灵已存入灵件室"})
    except SpiritError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@spirit_bp.post("/grant")
def grant_spirit():
    """测试用：直接发放战灵给玩家"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    # Flask 的 request.get_json() 在 Content-Type 不是 application/json 时会直接抛 415
    # 这里用 silent=True 做容错，避免调用端忘记带 header 时接口不可用
    data = request.get_json(silent=True) or {}
    element = str(data.get("element", "earth") or "earth")  # 默认土灵
    beast_id = data.get("beastId")  # 可选：直接装备到幻兽
    quantity = int(data.get("quantity", 1) or 1)  # 发放数量，默认1

    # 验证元素有效性
    valid_elements = ["earth", "fire", "water", "wood", "metal", "god"]
    if element not in valid_elements:
        return jsonify({"ok": False, "error": f"无效元素，可选：{', '.join(valid_elements)}"}), 400

    if quantity <= 0 or quantity > 100:
        return jsonify({"ok": False, "error": "quantity 必须在1-100之间"}), 400

    created_spirits = []
    for _ in range(quantity):
        # 直接调用内部方法创建战灵
        spirit = services.spirit_service._roll_new_spirit(user_id=user_id, element_key=element)
        services.spirit_service.spirit_repo.save(spirit)

        # 如果指定了幻兽，直接装备
        if beast_id:
            try:
                services.spirit_service.equip_spirit(user_id, beast_id, spirit.id)
            except SpiritError:
                pass  # 装备失败不影响发放

        created_spirits.append({
            "id": spirit.id,
            "element": spirit.element,
            "race": spirit.race,
            "beastId": spirit.beast_id,
        })

    return jsonify({
        "ok": True,
        "message": f"发放成功，共{len(created_spirits)}个战灵",
        "spirits": created_spirits,
    })


@spirit_bp.get("/beast/<int:beast_id>/equipped")
def get_beast_equipped_spirits(beast_id: int):
    """获取指定幻兽的已装备战灵（按元素槽位组织）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    # 获取该幻兽装备的所有战灵
    spirits = services.spirit_repo.get_by_beast_id(beast_id)

    # 元素名称映射
    element_names = {
        "earth": "土",
        "fire": "火",
        "water": "水",
        "wood": "木",
        "metal": "金",
        "god": "神",
    }

    # 构建槽位数据（按元素组织）
    slots_data = {}
    for spirit in spirits:
        element_key = spirit.element
        element_name = element_names.get(element_key, element_key)

        # 获取战灵显示名称（种族 + 元素）
        spirit_display_name = f"{spirit.race}·{element_name}灵"

        slots_data[element_key] = {
            "id": spirit.id,
            "name": spirit_display_name,
            "element": element_key,
            "elementName": element_name,
            "race": spirit.race,
            "lines": [ln.to_dict() for ln in spirit.lines],
        }

    return jsonify({
        "ok": True,
        "beastId": beast_id,
        "slots": slots_data,
    })
