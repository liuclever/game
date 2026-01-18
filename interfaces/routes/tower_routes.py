# interfaces/routes/tower_routes.py
"""闯塔、镇妖相关路由"""

from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.tower_service import TowerError, PlayerBeast
from infrastructure.config.bone_system_config import get_bone_system_config

tower_bp = Blueprint('tower', __name__, url_prefix='/api')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def get_team_player_beasts(user_id: int) -> list:
    """获取战斗队幻兽并计算战斗属性（含战灵、战骨、魔魂加成）"""
    from typing import List
    beast_data_list = services.player_beast_repo.get_team_beasts(user_id=user_id)
    if not beast_data_list:
        return []
    
    player_beasts: List[PlayerBeast] = []
    
    for b in beast_data_list:
        # 使用统一转换服务获取应用装备加成后的基础属性
        stats = services.beast_pvp_service.get_beast_stats(b)
        
        hp = stats["hp"]
        pa = stats["physical_attack"]
        ma = stats["magic_attack"]
        pd = stats["physical_defense"]
        md = stats["magic_defense"]
        spd = stats["speed"]

        attack = max(pa, ma)
        defense = max(pd, md)

        player_beasts.append(
            PlayerBeast(
                id=b.id,
                name=b.name,
                realm=b.realm,
                level=b.level,
                hp=hp,
                attack=attack,
                defense=defense,
                speed=spd,
                nature=b.nature or "",
                physical_attack=pa,
                magic_attack=ma,
                physical_defense=pd,
                magic_defense=md,
                skills=b.skills or [],
            )
        )
    
    return player_beasts

    
    return player_beasts


# ===== 闯塔接口 =====
@tower_bp.get("/tower/info")
def get_tower_info():
    """获取闯塔信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    tower_type = request.args.get("type", "tongtian")
    info = services.tower_service.get_tower_info(user_id=user_id, tower_type=tower_type)
    return jsonify(info)


@tower_bp.get("/tower/guardian/<int:floor>")
def get_tower_guardian(floor: int):
    """获取某层守塔幻兽信息"""
    tower_type = request.args.get("type", "tongtian")
    guardians = services.tower_service.get_floor_guardians(tower_type, floor)
    return jsonify({"floor": floor, "guardians": guardians})


@tower_bp.post("/tower/challenge")
def tower_challenge():
    """手动挑战一层"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    use_buff = data.get("use_buff", True)
    
    player_beasts = get_team_player_beasts(user_id=user_id)
    if not player_beasts:
        return jsonify({"ok": False, "error": "战斗队中没有幻兽"}), 400
    
    try:
        battle = services.tower_service.challenge_floor(
            user_id=user_id,
            tower_type=tower_type,
            player_beasts=player_beasts,
            use_buff=use_buff,
        )
        return jsonify({
            "ok": True,
            "battle": battle.to_dict(),
            "state": services.tower_service.get_tower_info(user_id=user_id, tower_type=tower_type),
        })
    except TowerError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@tower_bp.post("/tower/auto")
def tower_auto_challenge():
    """自动闯塔"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    use_buff = data.get("use_buff", True)
    
    player_beasts = get_team_player_beasts(user_id=user_id)
    
    try:
        result = services.tower_service.auto_challenge(
            user_id=user_id,
            tower_type=tower_type,
            player_beasts=player_beasts,
            use_buff=use_buff,
        )
        return jsonify({
            "ok": True,
            "result": result.to_dict(),
            "state": services.tower_service.get_tower_info(user_id=user_id, tower_type=tower_type),
        })
    except TowerError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@tower_bp.get("/tower/battle/<int:battle_index>")
def get_tower_battle_detail(battle_index: int):
    """获取战报详情"""
    return jsonify({"error": "战报详情功能待实现"}), 501


@tower_bp.post("/tower/reset")
def tower_reset():
    """退出闯塔，重置层数"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    pending_rewards = data.get("pending_rewards", None)
    
    result = services.tower_service.reset_tower(
        user_id=user_id, tower_type=tower_type, pending_rewards=pending_rewards
    )
    return jsonify({"ok": True, "state": result})


@tower_bp.get("/tower/guardian/<tower_type>/<int:floor>")
def get_guardian_detail(tower_type: str, floor: int):
    """获取守塔幻兽详情"""
    guardians = services.tower_config_repo.get_guardians_for_floor(tower_type, floor)
    if not guardians:
        return jsonify({"ok": False, "error": "未找到守塔幻兽"}), 404
    
    guardian = guardians[0]
    combat_power = int((guardian.hp + guardian.physical_attack + guardian.magic_attack + 
                        guardian.physical_defense + guardian.magic_defense + guardian.speed) / 10)
    
    return jsonify({
        "ok": True,
        "guardian": {
            "name": guardian.name,
            "description": guardian.description,
            "level": guardian.level,
            "nature": guardian.nature,
            "hp": guardian.hp,
            "physical_attack": guardian.physical_attack,
            "magic_attack": guardian.magic_attack,
            "physical_defense": guardian.physical_defense,
            "magic_defense": guardian.magic_defense,
            "speed": guardian.speed,
            "combat_power": combat_power,
        }
    })


@tower_bp.get("/tower/player-beast/<int:beast_id>")
def get_player_beast_detail(beast_id: int):
    """获取玩家幻兽详情"""
    beast_data = services.player_beast_repo.get_by_id(beast_id)
    if not beast_data:
        return jsonify({"ok": False, "error": "未找到幻兽"}), 404

    try:
        from domain.services.beast_stats import calc_total_stats_with_bonus
        from domain.services.mosoul_system import calc_mosoul_bonus_from_repo
        from infrastructure.db import mosoul_repo_mysql as mosoul_repo
        from interfaces.routes.beast_routes import _calc_beast_stats, get_exp_to_next_level
        from domain.services.beast_stats import calc_beast_aptitude_stars, get_beast_equipment_counts

        beast_data = _calc_beast_stats(beast_data)
        services.player_beast_repo.update_beast(beast_data)

        beast_dict = beast_data.to_dict()
        beast_dict["exp_max"] = get_exp_to_next_level(beast_data.level)

        template = services.beast_template_repo.get_by_name(beast_data.name)
        beast_dict["template_id"] = template.id if template else None

        aptitudes = {
            "hp": beast_data.hp_aptitude,
            "speed": beast_data.speed_aptitude,
            "physical_attack": beast_data.physical_attack_aptitude,
            "magic_attack": beast_data.magic_attack_aptitude,
            "physical_defense": beast_data.physical_defense_aptitude,
            "magic_defense": beast_data.magic_defense_aptitude,
        }
        beast_dict["aptitude_stars"] = calc_beast_aptitude_stars(beast_data.name, beast_data.realm, aptitudes)

        equipment_counts = get_beast_equipment_counts(
            beast_id, beast_data.level, mosoul_repo, services.bone_repo, services.spirit_repo
        )
        beast_dict.update(equipment_counts)

        base_stats = {
            "hp": beast_dict.get("hp") or 0,
            "physical_attack": beast_dict.get("physical_attack") or 0,
            "magic_attack": beast_dict.get("magic_attack") or 0,
            "physical_defense": beast_dict.get("physical_defense") or 0,
            "magic_defense": beast_dict.get("magic_defense") or 0,
            "speed": beast_dict.get("speed") or 0,
        }

        spirit_bonus = services.spirit_service.calc_spirit_bonus_for_beast(beast_id, beast_data.nature, base_stats)
        equipped_bones = services.bone_repo.get_by_beast_id(beast_id)
        bone_bonus = services.bone_service.calc_bone_bonus(equipped_bones)
        equipped_mosouls = mosoul_repo.get_mosouls_by_beast(beast_id)
        mosoul_bonus = calc_mosoul_bonus_from_repo(equipped_mosouls, base_stats)

        total_stats = calc_total_stats_with_bonus(base_stats, spirit_bonus, bone_bonus, mosoul_bonus)
        beast_dict.update(total_stats)

        return jsonify({"ok": True, "beast": beast_dict})
    except Exception:
        return jsonify({"ok": True, "beast": beast_data.to_dict()})


# ===== 鼓舞系统 =====
INSPIRE_DURATION_SECONDS = 30 * 60
INSPIRE_PILL_ITEM_ID = 8001


@tower_bp.get("/tower/inspire/status")
def get_inspire_status():
    """获取鼓舞状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query
    from datetime import datetime
    
    try:
        rows = execute_query(
            "SELECT inspire_expire_time FROM player WHERE user_id = %s", (user_id,)
        )
    except Exception as e:
        if "Unknown column" in str(e) and "inspire_expire_time" in str(e):
            rows = []
        else:
            raise
    
    active = False
    remaining_seconds = 0
    
    if rows and rows[0].get('inspire_expire_time'):
        expire_time = rows[0]['inspire_expire_time']
        if isinstance(expire_time, datetime):
            now = datetime.now()
            if expire_time > now:
                active = True
                remaining_seconds = int((expire_time - now).total_seconds())
    
    pill_count = 0
    inv_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    if inv_rows:
        pill_count = inv_rows[0].get('quantity', 0)
    
    return jsonify({
        "ok": True,
        "active": active,
        "remaining_seconds": remaining_seconds,
        "inspire_pill_count": pill_count,
    })


@tower_bp.post("/tower/inspire/use")
def use_inspire_pill():
    """使用鼓舞丹"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query, execute_update
    from datetime import datetime, timedelta
    
    try:
        rows = execute_query(
            "SELECT inspire_expire_time FROM player WHERE user_id = %s", (user_id,)
        )
    except Exception as e:
        if "Unknown column" in str(e) and "inspire_expire_time" in str(e):
            return jsonify({
                "ok": False,
                "error": "数据库缺少 inspire_expire_time 字段，请先执行数据库更新脚本后再使用鼓舞丹",
            }), 400
        raise
    
    if rows and rows[0].get('inspire_expire_time'):
        expire_time = rows[0]['inspire_expire_time']
        if isinstance(expire_time, datetime) and expire_time > datetime.now():
            return jsonify({"ok": False, "error": "鼓舞效果正在生效中，无法叠加使用！"})
    
    inv_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    
    if not inv_rows or inv_rows[0].get('quantity', 0) <= 0:
        return jsonify({"ok": False, "error": "鼓舞丹不足！"})
    
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    
    expire_time = datetime.now() + timedelta(seconds=INSPIRE_DURATION_SECONDS)
    try:
        execute_update(
            "UPDATE player SET inspire_expire_time = %s WHERE user_id = %s",
            (expire_time, user_id)
        )
    except Exception as e:
        if "Unknown column" in str(e) and "inspire_expire_time" in str(e):
            return jsonify({
                "ok": False,
                "error": "数据库缺少 inspire_expire_time 字段，请先执行数据库更新脚本后再使用鼓舞丹",
            }), 400
        raise
    
    return jsonify({
        "ok": True,
        "message": "使用鼓舞丹成功！战力提升10%，持续30分钟。"
    })


# ===== 镇妖接口 =====
@tower_bp.get("/zhenyao/info")
def get_zhenyao_info():
    """获取镇妖信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    info = services.zhenyao_service.get_zhenyao_info(user_id=user_id)
    
    # 获取今日已用次数
    from application.services.zhenyao_service import TRIAL_DAILY_LIMIT, HELL_DAILY_LIMIT, ZHENYAO_FU_ITEM_ID
    trial_used, hell_used = services.zhenyao_service.daily_count_repo.get_today_count(user_id)
    
    # 获取背包中的实时镇妖符数量
    zhenyao_fu_count = 0
    try:
        from infrastructure.db.connection import execute_query
        inv_rows = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, ZHENYAO_FU_ITEM_ID)
        )
        if inv_rows:
            zhenyao_fu_count = inv_rows[0].get('quantity', 0)
    except Exception:
        zhenyao_fu_count = 0
    
    return jsonify({
        "ok": info.can_zhenyao,
        "can_zhenyao": info.can_zhenyao,
        "player_level": info.player_level,
        "rank_name": info.rank_name,
        "zhenyao_range": info.zhenyao_range,
        "tower_max_floor": info.tower_max_floor,
        "trial_count": len(info.trial_floors),
        "hell_count": len(info.hell_floors),
        "trial_used": trial_used,
        "hell_used": hell_used,
        "trial_limit": TRIAL_DAILY_LIMIT,
        "hell_limit": HELL_DAILY_LIMIT,
        "zhenyao_fu_count": zhenyao_fu_count,  # 添加实时镇妖符数量
        "error": info.error_msg,
    })


@tower_bp.get("/zhenyao/floors")
def get_zhenyao_floors():
    """获取镇妖层数列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    floor_type = request.args.get("type", "trial")
    result = services.zhenyao_service.get_floor_list(user_id=user_id, floor_type=floor_type)
    return jsonify(result)


@tower_bp.post("/zhenyao/occupy")
def occupy_zhenyao_floor():
    """占领某层"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    floor = int(data.get("floor", 0))
    
    if floor <= 0:
        return jsonify({"ok": False, "error": "无效的层数"}), 400
    
    result = services.zhenyao_service.occupy_floor(user_id=user_id, floor=floor)
    return jsonify(result)


@tower_bp.post("/zhenyao/challenge")
def challenge_zhenyao_floor():
    """挑战某层"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    floor = int(data.get("floor", 0))
    
    if floor <= 0:
        return jsonify({"ok": False, "error": "无效的层数"}), 400
    
    result = services.zhenyao_service.challenge_floor(user_id=user_id, floor=floor)
    return jsonify(result)


@tower_bp.get("/zhenyao/dynamics")
def get_zhenyao_dynamics():
    """获取镇妖动态"""
    user_id = get_current_user_id()
    dynamic_type = request.args.get("type", "all")
    limit = int(request.args.get("limit", 20))
    
    dynamics = services.zhenyao_service.get_dynamics(
        user_id=user_id, dynamic_type=dynamic_type, limit=limit
    )
    return jsonify({"ok": True, "dynamics": dynamics})


@tower_bp.get("/zhenyao/battle/<int:battle_id>")
def get_zhenyao_battle(battle_id: int):
    """获取镇妖战斗详情"""
    log = services.zhenyao_service.get_battle_log(battle_id)
    if not log:
        return jsonify({"ok": False, "error": "战斗记录不存在"}), 404
    
    return jsonify({"ok": True, "battle": log})
