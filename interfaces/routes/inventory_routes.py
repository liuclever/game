# interfaces/routes/inventory_routes.py
"""背包系统路由"""

from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from domain.services.skill_book_system import is_valid_skill_book

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _get_chest_star_level(player_level: int) -> int:
    """根据玩家等级获取宝箱星级
    
    30-39级: 3星
    40-49级: 4星
    50-59级: 5星
    60-69级: 6星
    70-79级: 7星
    80级及以上: 8星
    """
    if player_level < 30:
        return 0
    elif player_level < 40:
        return 3
    elif player_level < 50:
        return 4
    elif player_level < 60:
        return 5
    elif player_level < 70:
        return 6
    elif player_level < 80:
        return 7
    else:
        return 8


def _get_star_prefix(star_level: int) -> str:
    """根据星级数字获取中文星级前缀
    
    3 -> "三星"
    4 -> "四星"
    5 -> "五星"
    6 -> "六星"
    7 -> "七星"
    8 -> "八星"
    """
    star_map = {
        3: "三星",
        4: "四星",
        5: "五星",
        6: "六星",
        7: "七星",
        8: "八星",
    }
    return star_map.get(star_level, "")


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
    
    # 清理当前用户数量为0的物品（防止数据异常）
    try:
        from infrastructure.db.connection import execute_update
        execute_update("DELETE FROM player_inventory WHERE user_id = %s AND quantity <= 0", (user_id,))
    except:
        pass  # 忽略清理失败的情况
    
    # 获取正式背包物品（不含临时）
    items = services.inventory_service.get_inventory(user_id, include_temp=False)
    
    # 获取背包信息
    bag_info = services.inventory_service.get_bag_info(user_id)
    
    # 获取玩家信息（用于计算宝箱星级）
    player = services.player_repo.get_by_id(user_id)
    player_level = player.level if player else 0
    
    result_items = []
    for item in items:
        # 再次过滤数量为0的物品（双重保险）
        if item.inv_item.quantity <= 0:
            continue
        can_use, action_name = services.inventory_service.can_use_or_open_item(item.item_info)
        
        # 动态生成镇妖宝箱的星级名称
        item_name = item.item_info.name
        if item.item_info.id in (92001, 92002):  # 试炼宝箱或炼狱宝箱
            star_level = _get_chest_star_level(player_level)
            star_prefix = _get_star_prefix(star_level)
            if star_prefix:
                item_name = f"{star_prefix}{item_name}"
        
        result_items.append({
            "id": item.inv_item.id,
            "item_id": item.item_info.id,
            "name": item_name,
            "type": item.item_info.type,
            "quantity": item.inv_item.quantity,
            "description": item.item_info.description,
            "is_temporary": item.inv_item.is_temporary,
            "can_use_or_open": can_use,
            "action_name": action_name,  # "打开" 或 "使用" 或 ""
        })
    
    return jsonify({
        "ok": True,
        "items": result_items,
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
    
    # 获取玩家信息（用于计算宝箱星级）
    player = services.player_repo.get_by_id(user_id)
    player_level = player.level if player else 0
    
    result_items = []
    for item in items:
        # 过滤掉数量为0的物品
        if item.inv_item.quantity <= 0:
            continue
        can_use, action_name = services.inventory_service.can_use_or_open_item(item.item_info)
        
        # 动态生成镇妖宝箱的星级名称
        item_name = item.item_info.name
        if item.item_info.id in (92001, 92002):  # 试炼宝箱或炼狱宝箱
            star_level = _get_chest_star_level(player_level)
            star_prefix = _get_star_prefix(star_level)
            if star_prefix:
                item_name = f"{star_prefix}{item_name}"
        
        result_items.append({
            "id": item.inv_item.id,
            "item_id": item.item_info.id,
            "name": item_name,
            "type": item.item_info.type,
            "quantity": item.inv_item.quantity,
            "description": item.item_info.description,
            "created_at": item.inv_item.created_at.strftime("%m-%d %H:%M") if item.inv_item.created_at else "",
            "can_use_or_open": can_use,
            "action_name": action_name,
        })
    
    return jsonify({
        "ok": True,
        "items": result_items,
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
        result = services.inventory_service.use_item(user_id, inv_item_id, quantity)
        return jsonify({
            "ok": True,
            "message": result.get("message", "使用成功"),
            "rewards": result.get("rewards", {})
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


@inventory_bp.get("/item/detail")
def get_item_detail():
    """获取道具详情"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    inv_item_id = request.args.get("id")
    if not inv_item_id:
        return jsonify({"ok": False, "error": "缺少道具ID"})
    
    try:
        inv_item_id = int(inv_item_id)
        items = services.inventory_service.get_inventory(user_id, include_temp=False)
        found = None
        for item in items:
            if item.inv_item.id == inv_item_id:
                found = item
                break
        
        if not found:
            return jsonify({"ok": False, "error": "道具不存在"})
        
        can_use, action_name = services.inventory_service.can_use_or_open_item(found.item_info)
        return jsonify({
            "ok": True,
            "item": {
                "id": found.inv_item.id,
                "item_id": found.item_info.id,
                "name": found.item_info.name,
                "type": found.item_info.type,
                "quantity": found.inv_item.quantity,
                "description": found.item_info.description,
                "can_use_or_open": can_use,
                "action_name": action_name,
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@inventory_bp.post("/recycle")
def recycle_item():
    """回收道具（出售获得铜钱）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    inv_item_id = data.get("id")
    quantity = int(data.get("quantity", 1))
    
    if not inv_item_id:
        return jsonify({"ok": False, "error": "缺少物品ID"})
    
    try:
        # 获取道具信息
        inv_item = services.inventory_service.inventory_repo.get_by_id(inv_item_id)
        if not inv_item or inv_item.user_id != user_id:
            return jsonify({"ok": False, "error": "道具不存在"})
        
        if inv_item.quantity < quantity:
            return jsonify({"ok": False, "error": "道具数量不足"})
        
        # 获取物品模板
        item_template = services.inventory_service.item_repo.get_by_id(inv_item.item_id)
        if not item_template:
            return jsonify({"ok": False, "error": "物品模板不存在"})
        
        # 计算回收价格（根据物品类型和ID）
        recycle_price_per_item = 10  # 默认每个10铜钱
        if item_template.type == "consumable":
            recycle_price_per_item = 20
        elif item_template.type == "material":
            recycle_price_per_item = 15
        
        total_price = recycle_price_per_item * quantity
        
        # 扣除道具
        services.inventory_service._remove_item_from_slot(inv_item_id, quantity)
        
        # 增加铜钱
        if services.inventory_service.player_repo:
            player = services.inventory_service.player_repo.get_by_id(user_id)
            if player:
                player.gold = int(getattr(player, "gold", 0) or 0) + total_price
                services.inventory_service.player_repo.save(player)
        
        return jsonify({
            "ok": True,
            "message": f"回收成功，获得铜钱×{total_price}",
            "gold": total_price
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
