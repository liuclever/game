# interfaces/routes/immortalize_routes.py
"""化仙系统路由：化仙池状态、化仙阵、升级等"""

from flask import Blueprint, jsonify, session, request
from interfaces.web_api.bootstrap import services
from application.services.immortalize_pool_service import ImmortalizeError

immortalize_bp = Blueprint('immortalize', __name__, url_prefix='/api/immortalize')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@immortalize_bp.post("/dan/use")
def use_dan():
    """使用化仙丹：仅允许在化仙系统中使用（不走背包use_item）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    try:
        quantity = int(data.get("quantity", 1) or 1)
    except (TypeError, ValueError):
        quantity = 1

    if quantity != 1:
        return jsonify({"ok": False, "error": "化仙丹一次只能使用1颗"}), 400

    if services.inventory_service.get_item_count(user_id, 6015) <= 0:
        return jsonify({"ok": False, "error": "化仙丹不足"}), 400

    try:
        services.inventory_service.remove_item(user_id, 6015, 1)
        result = services.immortalize_pool_service.add_dan_exp(user_id)
        added = result.get("added_exp", 0)
        dan_exp = result.get("dan_exp", 0)
        if added <= 0:
            message = "化仙池已满，化仙丹的经验无法注入"
        elif added < dan_exp:
            message = f"化仙池容量即将溢出，实际注入经验 {added}/{dan_exp}"
        else:
            message = f"成功使用化仙丹，化仙池获得{added}经验"
        return jsonify({"ok": True, "message": message, **result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@immortalize_bp.get("/status")
def get_status():
    """查询化仙状态
    
    返回：
    - level: 化仙池等级
    - current_exp: 当前经验
    - capacity: 容量上限
    - is_full: 是否已满
    - next_upgrade: 下一级升级条件（若有）
    - formation: 化仙阵状态
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        status = services.immortalize_pool_service.get_status(user_id)
        return jsonify({"ok": True, **status})
    except ImmortalizeError as e:
        return jsonify({"ok": False, "error": str(e)})


@immortalize_bp.post("/formation/start")
def start_formation():
    """开启化仙阵
    
    化仙阵持续4小时，每小时自动获得经验（由后台调度器结算）。
    同一时间只能有一个化仙阵运行。
    
    返回：
    - active: 是否激活
    - level: 阵的等级（开启时的化仙池等级）
    - started_at: 开始时间
    - ends_at: 结束时间
    - remaining_seconds: 剩余秒数
    - hourly_exp: 每小时经验
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        result = services.immortalize_pool_service.start_formation(user_id)
        return jsonify({"ok": True, "message": "化仙阵已开启", **result})
    except ImmortalizeError as e:
        return jsonify({"ok": False, "error": str(e)})


@immortalize_bp.get("/formation/status")
def get_formation_status():
    """查询化仙阵状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        status = services.immortalize_pool_service.get_status(user_id)
        formation = status.get("formation", {})
        return jsonify({"ok": True, **formation})
    except ImmortalizeError as e:
        return jsonify({"ok": False, "error": str(e)})


@immortalize_bp.post("/upgrade")
def upgrade_pool():
    """升级化仙池
    
    消耗：
    - 7种结晶（数量随等级递增）
    - 铜钱
    
    前置条件：
    - 玩家等级达到要求
    
    返回：
    - new_level: 新等级
    - current_exp: 当前经验
    - capacity: 新容量
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        result = services.immortalize_pool_service.upgrade_pool(user_id)
        return jsonify({"ok": True, "message": "化仙池升级成功", **result})
    except ImmortalizeError as e:
        return jsonify({"ok": False, "error": str(e)})


@immortalize_bp.get("/upgrade/cost")
def get_upgrade_cost():
    """查询化仙池升级所需材料"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        status = services.immortalize_pool_service.get_status(user_id)
        next_upgrade = status.get("next_upgrade")
        if not next_upgrade:
            return jsonify({
                "ok": True,
                "can_upgrade": False,
                "reason": "已达最高等级",
                "current_level": status.get("level"),
            })
        
        # 查询玩家当前拥有的材料数量
        player = services.player_repo.get_by_id(user_id)
        player_level = player.level if player else 0
        player_gold = player.gold if player else 0
        
        required_level = next_upgrade.get("required_player_level", 0)
        crystal_ids = next_upgrade.get("crystal_item_ids", [])
        crystal_qty = next_upgrade.get("crystal_qty_per_type", 0)
        copper_cost = next_upgrade.get("copper_cost", 0)
        
        materials = []
        all_enough = True
        
        # 检查结晶
        for item_id in crystal_ids:
            owned = services.inventory_service.get_item_count(user_id, item_id)
            enough = owned >= crystal_qty
            if not enough:
                all_enough = False
            item_info = services.item_repo.get_by_id(item_id)
            item_name = item_info.name if item_info else f"结晶{item_id}"
            materials.append({
                "item_id": item_id,
                "name": item_name,
                "required": crystal_qty,
                "owned": owned,
                "has_enough": enough,
            })
        
        # 检查铜钱
        gold_enough = player_gold >= copper_cost
        if not gold_enough:
            all_enough = False
        materials.append({
            "item_id": 0,
            "name": "铜钱",
            "required": copper_cost,
            "owned": player_gold,
            "has_enough": gold_enough,
        })
        
        # 检查玩家等级
        level_enough = player_level >= required_level
        if not level_enough:
            all_enough = False
        
        return jsonify({
            "ok": True,
            "can_upgrade": all_enough,
            "current_level": status.get("level"),
            "to_level": next_upgrade.get("to_level"),
            "required_player_level": required_level,
            "player_level": player_level,
            "level_enough": level_enough,
            "materials": materials,
        })
    except ImmortalizeError as e:
        return jsonify({"ok": False, "error": str(e)})


@immortalize_bp.get("/config")
def get_config():
    """获取化仙系统配置（供前端展示用）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    config = services.immortalize_pool_service.config
    return jsonify({
        "ok": True,
        "dan_exp": config.get_all_dan_exp(),
        "pool_max_level": config.get_pool_max_level(),
        "pool_capacity": config.get_all_pool_capacity(),
        "formation_duration_hours": config.get_formation_duration_hours(),
        "formation_hourly_exp": config.get_all_formation_hourly_exp(),
        "beast_ratio": config.get_all_beast_ratio(),
        "pool_upgrade": config.get_all_pool_upgrade_requirements(),
    })
