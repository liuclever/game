# interfaces/routes/inventory_routes.py
"""背包系统路由"""

from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from domain.services.skill_book_system import is_valid_skill_book

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@inventory_bp.get("/list")
def get_inventory_list():
    """
    获取背包物品列表
    打开背包时调用，会自动执行临时物品转移
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 先执行临时物品转移
    transferred = services.inventory_service.transfer_temp_to_bag(user_id)
    
    # 获取正式背包物品（不含临时）
    items = services.inventory_service.get_inventory(user_id, include_temp=False)
    
    # 获取背包信息
    bag_info = services.inventory_service.get_bag_info(user_id)
    
    return jsonify({
        "ok": True,
        "items": [
            {
                "id": item.inv_item.id,
                "item_id": item.item_info.id,
                "name": item.item_info.name,
                "type": item.item_info.type,
                "quantity": item.inv_item.quantity,
                "description": item.item_info.description,
                "is_temporary": item.inv_item.is_temporary,
            }
            for item in items
        ],
        "bag_info": bag_info,
        "transferred": transferred,  # 本次转移的物品
    })


@inventory_bp.get("/temp")
def get_temp_items():
    """获取临时背包物品"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    items = services.inventory_service.get_temp_items(user_id)
    
    return jsonify({
        "ok": True,
        "items": [
            {
                "id": item.inv_item.id,
                "item_id": item.item_info.id,
                "name": item.item_info.name,
                "type": item.item_info.type,
                "quantity": item.inv_item.quantity,
                "description": item.item_info.description,
                "created_at": item.inv_item.created_at.strftime("%m-%d %H:%M") if item.inv_item.created_at else "",
            }
            for item in items
        ],
    })


@inventory_bp.get("/info")
def get_bag_info():
    """获取背包信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    bag_info = services.inventory_service.get_bag_info(user_id)
    return jsonify({"ok": True, **bag_info})


@inventory_bp.get("/skill-books")
def get_skill_books():
    """获取背包中的技能书列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    items = services.inventory_service.get_inventory(user_id, include_temp=False)
    skill_books = []
    for it in items or []:
        try:
            item_id = int(it.item_info.id)
        except Exception:
            continue
        if not is_valid_skill_book(item_id):
            continue
        skill_books.append({
            "id": it.inv_item.id,
            "item_id": item_id,
            "name": it.item_info.name,
            "full_name": it.item_info.name,
            "quantity": it.inv_item.quantity,
        })

    return jsonify({
        "ok": True,
        "skillBooks": skill_books,
    })


@inventory_bp.get("/upgrade_info")
def get_upgrade_info():
    """获取背包升级信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    upgrade_info = services.inventory_service.get_upgrade_cost(user_id)
    return jsonify({"ok": True, **upgrade_info})


@inventory_bp.post("/upgrade")
def upgrade_bag():
    """升级背包"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        bag = services.inventory_service.upgrade_bag(user_id)
        return jsonify({
            "ok": True,
            "message": f"背包升级成功！当前等级：{bag.bag_level}，容量：{bag.capacity}",
            "bag_level": bag.bag_level,
            "capacity": bag.capacity,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@inventory_bp.post("/use")
def use_item():
    """使用物品
    
    支持两种方式：
    1. 传入 id（背包记录ID）
    2. 传入 item_id（物品模板ID），自动查找背包中该物品
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    inv_item_id = data.get("id")
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 1))
    
    # 如果传入item_id而非id，则查找背包中该物品的记录ID
    if not inv_item_id and item_id:
        inv_item = services.inventory_service.find_item_by_item_id(user_id, item_id)
        if inv_item:
            inv_item_id = inv_item.id
        else:
            return jsonify({"ok": False, "error": "背包中没有该物品"})
    
    if not inv_item_id:
        return jsonify({"ok": False, "error": "缺少物品ID"})
        
    try:
        message = services.inventory_service.use_item(user_id, inv_item_id, quantity)
        return jsonify({
            "ok": True,
            "message": message
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@inventory_bp.post("/add")

def add_item():
    """添加物品到背包（测试用）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    item_id = int(data.get("item_id", 0))
    quantity = int(data.get("quantity", 1))
    
    if item_id == 0:
        return jsonify({"ok": False, "error": "item_id 必填"})
    
    try:
        inv_item, is_temp = services.inventory_service.add_item(user_id, item_id, quantity)
        return jsonify({
            "ok": True,
            "message": f"添加成功：+{quantity}",
            "item": {
                "id": inv_item.id,
                "item_id": inv_item.item_id,
                "quantity": inv_item.quantity,
                "is_temporary": is_temp,
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@inventory_bp.get("/item-count")
def get_item_count():
    """查询指定物品数量"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    raw_item_id = request.args.get("item_id")
    if raw_item_id is None:
        return jsonify({"ok": False, "error": "item_id 必填"}), 400

    try:
        item_id = int(raw_item_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "item_id 必须为整数"}), 400

    include_temp_raw = (request.args.get("include_temp") or "").strip().lower()
    include_temp = include_temp_raw in {"1", "true", "t", "yes", "y"}

    count = services.inventory_service.get_item_count(user_id, item_id, include_temp=include_temp)

    return jsonify({
        "ok": True,
        "item_id": item_id,
        "count": count,
        "include_temp": include_temp,
    })
