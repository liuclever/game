# interfaces/routes/beast_routes.py
"""幻兽相关路由：幻兽栏、战斗队管理、技能书等"""

import random
import json
import os
from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from infrastructure.db.player_beast_repo_mysql import PlayerBeastData
from infrastructure.db import mosoul_repo_mysql as mosoul_repo
from domain.services.skill_book_system import (
    use_skill_book,
    get_skill_by_item_id,
    get_skill_book_info,
    is_valid_skill_book,
    get_all_skill_books,
    get_replace_rules,
)
from domain.services.beast_stats import (
    calc_beast_aptitude_stars, 
    get_beast_equipment_counts, 
    calc_aptitude_boost,
    get_beast_max_realm
)
from application.services.vip_service import get_beast_slot_limit

beast_bp = Blueprint('beast', __name__, url_prefix='/api/beast')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@beast_bp.get("/list")
def get_beast_list():
    """获取玩家所有幻兽列表
    
    返回：幻兽栏和战斗队数据
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取玩家信息（用于计算最大携带数量）
    player = services.player_repo.get_by_id(user_id=user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 计算最大携带数量（根据等级）
    level = player.level
    if level >= 80:
        max_team_size = 5
    elif level >= 60:
        max_team_size = 4
    elif level >= 40:
        max_team_size = 3
    elif level >= 20:
        max_team_size = 2
    else:
        max_team_size = 1
    
    # 获取VIP等级
    vip_level = getattr(player, 'vip_level', 0) or 0
    
    # 获取所有幻兽
    all_beasts = services.player_beast_repo.get_all_by_user(user_id)

    # 联盟寄存信息
    storage_summary = services.alliance_service.get_beast_storage_summary(user_id)
    stored_beast_ids = services.alliance_service.get_my_stored_beast_ids(user_id) if storage_summary.get("hasAlliance") else []
    stored_beast_ids_set = set(stored_beast_ids)
    storage_capacity = storage_summary.get("capacity", 0)
    storage_count = storage_summary.get("count", 0)
    
    # 分离战斗队和非战斗队
    team_beasts = []
    other_beasts = []
    
    for beast in all_beasts:
        # 跳过寄存在幻兽室中的幻兽
        if beast.id in stored_beast_ids_set:
            continue

        # 重新计算属性和战力
        beast = _calc_beast_stats(beast)
        # 兜底修复：历史数据可能缺少 race，尝试从模板补齐并回写
        if not getattr(beast, "race", ""):
            tpl = None
            try:
                tpl = services.beast_template_repo.get_by_id(getattr(beast, "template_id", 0) or 0)
            except Exception:
                tpl = None
            if tpl and getattr(tpl, "race", ""):
                try:
                    beast.race = tpl.race
                except Exception:
                    pass
        services.player_beast_repo.update_beast(beast)
        total_power = _calc_total_combat_power_with_equipment(beast)
        
        beast_data = {
            "id": beast.id,
            "name": beast.name,
            "realm": beast.realm,
            "level": beast.level,
            "power": total_power,
            "inTeam": beast.is_in_team == 1,
            "teamPosition": beast.team_position,
            # 详细属性
            "hp": beast.hp,
            "physicalAttack": beast.physical_attack,
            "magicAttack": beast.magic_attack,
            "physicalDefense": beast.physical_defense,
            "magicDefense": beast.magic_defense,
            "speed": beast.speed,
            "race": beast.race,
            "nature": beast.nature,
            "personality": beast.personality,
            # 资质信息
            "hp_aptitude": getattr(beast, "hp_aptitude", 0),
            "speed_aptitude": getattr(beast, "speed_aptitude", 0),
            "physical_atk_aptitude": getattr(beast, "physical_attack_aptitude", 0),
            "magic_atk_aptitude": getattr(beast, "magic_attack_aptitude", 0),
            "physical_def_aptitude": getattr(beast, "physical_defense_aptitude", 0),
            "magic_def_aptitude": getattr(beast, "magic_defense_aptitude", 0),
        }
        
        if beast.is_in_team:
            team_beasts.append(beast_data)
        else:
            other_beasts.append(beast_data)
    
    # 战斗队按位置排序
    team_beasts.sort(key=lambda x: x["teamPosition"])
    
    # 合并列表：战斗队在前
    beast_list = team_beasts + other_beasts
    
    return jsonify({
        "ok": True,
        "playerLevel": level,
        "maxTeamSize": max_team_size,
        "maxBeastSlots": get_beast_slot_limit(vip_level),  # 根据VIP等级获取幻兽栏上限
        "storageCount": storage_count,
        "maxStorage": storage_capacity,
        "hasAlliance": storage_summary.get("hasAlliance", False),
        "storedBeastIds": stored_beast_ids,
        "teamBeasts": team_beasts,
        "beastList": beast_list,
        "totalCount": len(beast_list),
    })


@beast_bp.get("/team")
def get_battle_team():
    """获取战斗队幻兽"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    beasts = services.player_beast_repo.get_team_beasts(user_id)
    
    # 重新计算每只幻兽的属性和战力
    result_beasts = []
    for b in beasts:
        b = _calc_beast_stats(b)
        services.player_beast_repo.update_beast(b)
        total_power = _calc_total_combat_power_with_equipment(b)
        result_beasts.append({
            "id": b.id,
            "name": b.name,
            "realm": b.realm,
            "level": b.level,
            "power": total_power,
            "teamPosition": b.team_position,
        })
    
    return jsonify({
        "ok": True,
        "beasts": result_beasts
    })


@beast_bp.post("/join-team")
def join_team():
    """将幻兽加入战斗队"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    # 获取玩家信息
    player = services.player_repo.get_by_id(user_id=user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 计算最大携带数量
    level = player.level
    if level >= 80:
        max_team_size = 5
    elif level >= 60:
        max_team_size = 4
    elif level >= 40:
        max_team_size = 3
    elif level >= 20:
        max_team_size = 2
    else:
        max_team_size = 1
    
    # 检查当前队伍人数
    current_team = services.player_beast_repo.get_team_beasts(user_id)
    if len(current_team) >= max_team_size:
        return jsonify({"ok": False, "error": f"当前等级最多携带{max_team_size}只幻兽"})
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    if beast.is_in_team:
        return jsonify({"ok": False, "error": "该幻兽已在战斗队中"})
    
    # 加入战斗队
    beast.is_in_team = 1
    beast.team_position = len(current_team)  # 放到队尾
    services.player_beast_repo.update_beast(beast)
    
    return jsonify({"ok": True, "message": f"{beast.name}已加入战斗队"})


@beast_bp.post("/leave-team")
def leave_team():
    """将幻兽移出战斗队"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    if not beast.is_in_team:
        return jsonify({"ok": False, "error": "该幻兽不在战斗队中"})
    
    old_position = beast.team_position
    
    # 移出战斗队
    beast.is_in_team = 0
    beast.is_main = False  # 同时清除is_main标记
    beast.team_position = 0
    services.player_beast_repo.update_beast(beast)
    
    # 更新其他幻兽的位置（填补空位）
    team_beasts = services.player_beast_repo.get_team_beasts(user_id)
    for b in team_beasts:
        if b.team_position > old_position:
            b.team_position -= 1
            services.player_beast_repo.update_beast(b)
    
    return jsonify({"ok": True, "message": f"{beast.name}已离开战斗队"})


@beast_bp.post("/move-up")
def move_up():
    """战斗队中上移幻兽"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    if not beast.is_in_team:
        return jsonify({"ok": False, "error": "该幻兽不在战斗队中"})
    
    if beast.team_position == 0:
        return jsonify({"ok": False, "error": "已经在最前面了"})
    
    # 找到上一个位置的幻兽
    team_beasts = services.player_beast_repo.get_team_beasts(user_id)
    prev_beast = None
    for b in team_beasts:
        if b.team_position == beast.team_position - 1:
            prev_beast = b
            break
    
    if prev_beast:
        # 交换位置
        prev_beast.team_position, beast.team_position = beast.team_position, prev_beast.team_position
        services.player_beast_repo.update_beast(prev_beast)
        services.player_beast_repo.update_beast(beast)
    
    return jsonify({"ok": True, "message": "位置已调整"})


# 加载升级经验配置
def _load_level_exp_config():
    """加载升级经验配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'configs', 'beast_level_up_exp.json'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"max_level": 100, "exp_to_next_level": {}}

_LEVEL_EXP_CONFIG = None

def get_exp_to_next_level(level: int) -> int:
    """获取升到下一级所需经验"""
    global _LEVEL_EXP_CONFIG
    if _LEVEL_EXP_CONFIG is None:
        _LEVEL_EXP_CONFIG = _load_level_exp_config()
    
    exp_map = _LEVEL_EXP_CONFIG.get("exp_to_next_level", {})
    max_level = _LEVEL_EXP_CONFIG.get("max_level", 100)
    
    if level >= max_level:
        return 0  # 满级无需经验
    
    return exp_map.get(str(level), 0)


def _calc_total_exp(level: int, current_exp: int) -> int:
    global _LEVEL_EXP_CONFIG
    if _LEVEL_EXP_CONFIG is None:
        _LEVEL_EXP_CONFIG = _load_level_exp_config()

    exp_map = _LEVEL_EXP_CONFIG.get("exp_to_next_level", {})
    max_level = int(_LEVEL_EXP_CONFIG.get("max_level", 100) or 100)

    lv = int(level or 1)
    if lv < 1:
        lv = 1
    if lv > max_level:
        lv = max_level

    total = int(current_exp or 0)
    for i in range(1, lv):
        total += int(exp_map.get(str(i), 0) or 0)
    return total


@beast_bp.get("/<int:beast_id>")
def get_beast_detail(beast_id: int):
    """获取幻兽详情"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    # 重新计算属性（确保属性与等级匹配）
    beast = _calc_beast_stats(beast)
    # 兜底修复：历史数据可能缺少 race，尝试从模板补齐并回写
    if not getattr(beast, "race", ""):
        tpl = None
        try:
            tpl = services.beast_template_repo.get_by_id(getattr(beast, "template_id", 0) or 0)
        except Exception:
            tpl = None
        if tpl and getattr(tpl, "race", ""):
            try:
                beast.race = tpl.race
            except Exception:
                pass
    # 保存更新后的属性到数据库
    services.player_beast_repo.update_beast(beast)
    
    beast_dict = beast.to_dict()
    # 添加升级所需经验
    beast_dict['exp_max'] = get_exp_to_next_level(beast.level)

    template_id = int(beast_dict.get("template_id") or getattr(beast, "template_id", 0) or 0)
    if template_id > 0:
        beast_dict["template_id"] = template_id
    else:
        name = str(getattr(beast, "name", "") or "")
        template = services.beast_template_repo.get_by_name(name)
        if template is None:
            def _norm(s: str) -> str:
                return "".join(ch for ch in str(s or "") if ch not in {" ", "\t", "\r", "\n", "·"})

            key = _norm(name)
            if key:
                for tpl in services.beast_template_repo.get_all().values():
                    if _norm(getattr(tpl, "name", "")) == key:
                        template = tpl
                        break
        beast_dict["template_id"] = template.id if template else None
    
    print("DEBUG magic_attack_aptitude =", beast.magic_attack_aptitude)
    # 计算资质星级
    aptitudes = {
        'hp': beast.hp_aptitude,
        'speed': beast.speed_aptitude,
        'physical_attack': beast.physical_attack_aptitude,
        'magic_attack': beast.magic_attack_aptitude,
        'physical_defense': beast.physical_defense_aptitude,
        'magic_defense': beast.magic_defense_aptitude,
    }
    
    stars = calc_beast_aptitude_stars(beast.name, beast.realm, aptitudes)
    beast_dict['aptitude_stars'] = stars
    
    equipment_counts = get_beast_equipment_counts(
        beast_id, beast.level, mosoul_repo, services.bone_repo, services.spirit_repo
    )
    beast_dict.update(equipment_counts)
    
    from domain.services.beast_stats import calc_total_stats_with_bonus
    from domain.services.mosoul_system import calc_mosoul_bonus_from_repo
    
    base_stats = {
        "hp": beast_dict.get("hp") or 0,
        "physical_attack": beast_dict.get("physical_attack") or 0,
        "magic_attack": beast_dict.get("magic_attack") or 0,
        "physical_defense": beast_dict.get("physical_defense") or 0,
        "magic_defense": beast_dict.get("magic_defense") or 0,
        "speed": beast_dict.get("speed") or 0,
    }
    
    spirit_bonus = services.spirit_service.calc_spirit_bonus_for_beast(beast_id, beast.nature, base_stats)
    equipped_bones = services.bone_repo.get_by_beast_id(beast_id)
    bone_bonus = services.bone_service.calc_bone_bonus(equipped_bones)
    equipped_mosouls = mosoul_repo.get_mosouls_by_beast(beast_id)
    mosoul_bonus = calc_mosoul_bonus_from_repo(equipped_mosouls, base_stats)
    
    total_stats = calc_total_stats_with_bonus(base_stats, spirit_bonus, bone_bonus, mosoul_bonus)
    beast_dict.update(total_stats)
    
    return jsonify({
        "ok": True,
        "beast": beast_dict,
    })


# ===================== 技能书系统 =====================

@beast_bp.get("/skill-books")
def get_skill_books():
    """获取所有技能书列表"""
    books = get_all_skill_books()
    rules = get_replace_rules()
    
    return jsonify({
        "ok": True,
        "skillBooks": books,
        "rules": {
            "maxSkills": rules.get("max_skills", 4),
            "addChance": rules.get("add_chance", 0.5),
            "description": rules.get("rules", {})
        }
    })


@beast_bp.post("/use-skill-book")
def use_skill_book_api():
    """使用技能书修改幻兽技能
    
    请求参数：
    - beastId: 幻兽 ID
    - itemId: 技能书道具 ID
    - replaceIndex: （可选）强制替换的技能索引 (0-3)
    
    返回：
    - success: 是否成功
    - action: "add" | "replace" | "failed"
    - newSkill: 新学习的技能
    - replacedSkill: 被替换的技能（如果是替换操作）
    - finalSkills: 最终技能列表
    - message: 结果描述
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    item_id = data.get("itemId")
    replace_index = data.get("replaceIndex")  # 可选
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽 ID"}), 400
    if not item_id:
        return jsonify({"ok": False, "error": "缺少技能书 ID"}), 400
    
    # 验证技能书有效性
    if not is_valid_skill_book(item_id):
        return jsonify({"ok": False, "error": "无效的技能书"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    # 获取当前技能列表
    current_skills = beast.skills if beast.skills else []
    if isinstance(current_skills, str):
        import json
        try:
            current_skills = json.loads(current_skills)
        except:
            current_skills = []
    
    # 使用技能书
    result = use_skill_book(
        current_skills=current_skills,
        skill_book_item_id=item_id,
        force_replace_index=replace_index
    )
    
    if not result.success:
        return jsonify({
            "ok": False,
            "error": result.message,
            "action": result.action,
            "newSkill": result.new_skill,
        })
    
    # 更新幻兽技能
    beast.skills = result.final_skills
    services.player_beast_repo.update_beast(beast)
    
    # 扣除技能书道具
    try:
        services.inventory_service.remove_item(user_id, item_id, 1)
    except Exception as e:
        # 技能已学习但扣除失败，记录日志但不影响结果
        print(f"打书成功但扣除物品失败: {e}")
    
    return jsonify({
        "ok": True,
        "success": result.success,
        "action": result.action,
        "newSkill": result.new_skill,
        "replacedSkill": result.replaced_skill,
        "finalSkills": result.final_skills,
        "message": result.message,
    })


@beast_bp.get("/<int:beast_id>/skills")
def get_beast_skills(beast_id: int):
    """获取幻兽技能列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    current_skills = beast.skills if beast.skills else []
    if isinstance(current_skills, str):
        import json
        try:
            current_skills = json.loads(current_skills)
        except:
            current_skills = []
    
    rules = get_replace_rules()
    
    return jsonify({
        "ok": True,
        "beastId": beast_id,
        "beastName": beast.name,
        "skills": current_skills,
        "skillCount": len(current_skills),
        "maxSkills": rules.get("max_skills", 4),
    })


# ===================== 成长率倍率配置加载 =====================

_growth_multiplier_cache = None

def _load_growth_multipliers():
    """从配置文件加载成长率倍率映射"""
    global _growth_multiplier_cache
    if _growth_multiplier_cache is not None:
        return _growth_multiplier_cache
    
    import os
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'growth_rate_multipliers.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 转换为 int key 的字典，排序存储
            _growth_multiplier_cache = {int(k): v for k, v in data.get('growth_score_to_multiplier', {}).items()}
    except Exception as e:
        print(f"加载成长率配置失败: {e}")
        _growth_multiplier_cache = {840: 0.3}  # 默认值
    return _growth_multiplier_cache

def _get_growth_multiplier(growth_score: int) -> float:
    """根据成长率评分获取对应倍率
    
    查找不超过 growth_score 的最大键值对应的倍率
    """
    multipliers = _load_growth_multipliers()
    if not multipliers:
        return 0.3
    
    # 排序后找到不超过 growth_score 的最大键
    sorted_keys = sorted(multipliers.keys())
    result_mult = multipliers[sorted_keys[0]]  # 默认取最小的
    
    for key in sorted_keys:
        if key <= growth_score:
            result_mult = multipliers[key]
        else:
            break
    
    return result_mult


# ===================== 属性计算辅助函数 =====================

# Level 1 速度分段规则：
# - 0-1100 => 1
# - 1101-2200 => 2
# - 2201-3300 => 3
# ... 依此类推（每 1100 为一档）
#
# NOTE: 这里按“上界包含”的口径实现：1100 属于第一档、2200 属于第二档。
# 如需让 1100 属于第二档，把实现改为：max(1, (sa // 1100) + 1)
def _calc_level1_speed_from_aptitude(speed_aptitude: int) -> int:
    try:
        sa = int(speed_aptitude or 0)
    except (TypeError, ValueError):
        sa = 0
    if sa < 0:
        sa = 0
    # ceil(sa / 1100)，并把 0 映射到 1
    return max(1, (sa + 1099) // 1100)


def _calc_total_combat_power_with_equipment(beast) -> int:
    try:
        from domain.services.beast_stats import calc_total_stats_with_bonus
        from domain.services.mosoul_system import calc_mosoul_bonus_from_repo

        base_stats = {
            "hp": int(getattr(beast, "hp", 0) or 0),
            "physical_attack": int(getattr(beast, "physical_attack", 0) or 0),
            "magic_attack": int(getattr(beast, "magic_attack", 0) or 0),
            "physical_defense": int(getattr(beast, "physical_defense", 0) or 0),
            "magic_defense": int(getattr(beast, "magic_defense", 0) or 0),
            "speed": int(getattr(beast, "speed", 0) or 0),
        }

        beast_id = getattr(beast, "id", 0)
        nature = getattr(beast, "nature", "")

        spirit_bonus = services.spirit_service.calc_spirit_bonus_for_beast(beast_id, nature, base_stats)
        equipped_bones = services.bone_repo.get_by_beast_id(beast_id)
        bone_bonus = services.bone_service.calc_bone_bonus(equipped_bones)

        equipped_mosouls = mosoul_repo.get_mosouls_by_beast(beast_id)
        mosoul_bonus = calc_mosoul_bonus_from_repo(equipped_mosouls, base_stats)

        total_stats = calc_total_stats_with_bonus(base_stats, spirit_bonus, bone_bonus, mosoul_bonus)
        return int(total_stats.get("combat_power", getattr(beast, "combat_power", 0) or 0) or 0)
    except Exception:
        return int(getattr(beast, "combat_power", 0) or 0)


def _calc_beast_stats(beast, attack_type: str = None):
    """根据幻兽的等级、资质、成长率等重新计算属性"""
    from domain.services.beast_stats import calc_beast_attributes, get_beast_max_realm
    
    # 获取模板以确定最高境界
    template = services.beast_template_repo.get_by_name(beast.name)
    max_realm = "地界"
    if template:
        template_realms = template.realms.keys() if hasattr(template, 'realms') and template.realms else []
        max_realm = get_beast_max_realm(template_realms)
    
    # 统一归一化攻击类型：magical -> magic
    effective_attack_type = getattr(beast, 'attack_type', '') or ''
    if effective_attack_type == 'magical':
        effective_attack_type = 'magic'
    if not effective_attack_type and template:
        effective_attack_type = getattr(template, 'attack_type', '') or ''
    if effective_attack_type == 'magical':
        effective_attack_type = 'magic'

    # 统一修正 nature：优先保持与模板 trait/attack_type 一致
    nature = getattr(beast, 'nature', '') or ''
    trait = getattr(template, 'trait', '') if template else ''
    trait_has_system = ('物系' in str(trait)) or ('法系' in str(trait))
    nature_has_system = ('物系' in str(nature)) or ('法系' in str(nature))

    # 若 trait 本身就是一个可用的 nature（带 物系/法系），优先用它作为纠正目标
    target_nature = str(trait) if trait_has_system else ''

    if not nature_has_system:
        if target_nature:
            nature = target_nature
        else:
            nature = '法系普攻' if effective_attack_type == 'magic' else '物系普攻'
    else:
        # 当数据库 nature 与攻击类型冲突时，优先按 trait，否则按攻击类型纠正
        if effective_attack_type == 'magic' and '物系' in str(nature):
            nature = target_nature or str(nature).replace('物系', '法系', 1)
        if effective_attack_type != 'magic' and '法系' in str(nature):
            nature = target_nature or str(nature).replace('法系', '物系', 1)

    # 将纠正后的 attack_type/nature 写回 beast，便于后续 update_beast 持久化
    if effective_attack_type:
        setattr(beast, 'attack_type', effective_attack_type)
    setattr(beast, 'nature', nature)
    
    attrs = calc_beast_attributes(
        hp_aptitude=beast.hp_aptitude,
        speed_aptitude=getattr(beast, 'speed_aptitude', 0),
        phys_atk_aptitude=beast.physical_attack_aptitude,
        magic_atk_aptitude=beast.magic_attack_aptitude,
        phys_def_aptitude=beast.physical_defense_aptitude,
        magic_def_aptitude=beast.magic_defense_aptitude,
        level=beast.level,
        realm=beast.realm,
        max_realm=max_realm,
        growth_score=beast.growth_rate or 840,
        nature=nature,
    )
    
    beast.hp = attrs["hp"]
    beast.speed = attrs["speed"]
    beast.physical_attack = attrs["physical_attack"]
    beast.magic_attack = attrs["magic_attack"]
    beast.physical_defense = attrs["physical_defense"]
    beast.magic_defense = attrs["magic_defense"]
    beast.combat_power = attrs["combat_power"]
    
    return beast


# ===================== 获取幻兽系统 =====================

def obtain_beast_for_user(user_id: int, template_id=None, realm: str = "地界", level: int = 1):
    """
    获取一只新幻兽（随机从模板中生成）
    - 已重构为使用 BeastService
    """
    try:
        beast = services.beast_service.obtain_beast_randomly(
            user_id=user_id,
            template_id=template_id,
            realm=realm,
            level=level
        )
        
        # 获取模板以计算属性
        template = services.beast_template_repo.get_by_id(beast.template_id)
        
        # 计算实际属性（Beast 领域实体需要通过模板计算）
        hp = beast.calc_hp(template) if template else 0
        attack = beast.calc_attack(template) if template else 0
        defense = beast.calc_defense(template) if template else 0
        speed = beast.calc_speed(template) if template else 0
        
        # 转换为前端需要的格式 (保持兼容性)
        return {
            "ok": True,
            "message": f"成功获得幻兽【{beast.nickname}】！",
            "beast": {
                "id": beast.id,
                "name": beast.nickname,
                "realm": beast.realm,
                "level": beast.level,
                "hp": hp,
                "physicalAttack": attack if template and template.attack_type == "physical" else 0,
                "magicAttack": attack if template and template.attack_type == "magic" else 0,
                "physicalDefense": defense,
                "magicDefense": defense,
                "speed": speed,
                "combatPower": hp + attack + defense + speed,
                "skills": beast.skills,
            }
        }, 200
    except Exception as e:
        return {"ok": False, "error": str(e)}, 200


@beast_bp.post("/obtain")
def obtain_beast():
    """获取一只新幻兽（随机从模板中生成）
    
    请求参数：
    - userId: (可选) 用户ID，默认使用登录用户，未登录时默认为1
    - templateId: (可选) 指定模板ID，不提供则随机选择
    - realm: (可选) 指定境界，默认地界
    - level: (可选) 指定等级，默认1级
    
    返回：
    - beast: 新获得的幻兽信息
    """
    data = request.get_json() or {}
    
    # 支持从参数传入userId（测试用），否则使用登录用户，最后默认为1
    user_id = data.get("userId") or get_current_user_id() or 1
    template_id = data.get("templateId")
    realm = data.get("realm", "地界")
    level = data.get("level", 1)
    
    payload, status_code = obtain_beast_for_user(
        user_id=user_id,
        template_id=template_id,
        realm=realm,
        level=level,
    )
    return jsonify(payload), status_code


@beast_bp.delete("/<int:beast_id>")
def release_beast(beast_id: int):
    """放生幻兽（化仙）
    
    流程：
    1. 卸下战骨/魔魂/战灵并返还
    2. 根据境界返还进化材料
    3. 将幻兽经验按比例注入化仙池
    4. 删除幻兽
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取幻兽信息
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404

    if getattr(beast, "is_in_team", 0):
        return jsonify({"ok": False, "error": "战斗队及出战中幻兽无法化仙"}), 400

    if int(getattr(beast, "level", 0) or 0) < 15:
        return jsonify({"ok": False, "error": "未满15级幻兽无法化仙"}), 400
    
    beast_name = beast.name
    beast_exp = beast.exp
    beast_realm = beast.realm or "地界"
    
    # ========== 1. 卸下战骨 ==========
    unequipped_bones = []
    bones = services.bone_repo.get_by_beast_id(beast_id)
    for bone in bones:
        bone.beast_id = None
        services.bone_repo.save(bone)
        unequipped_bones.append({"id": bone.id, "slot": bone.slot})
    
    # ========== 2. 卸下战灵 ==========
    unequipped_spirits = []
    spirits = services.spirit_repo.get_by_beast_id(beast_id)
    for spirit in spirits:
        spirit.beast_id = None
        services.spirit_repo.save(spirit)
        unequipped_spirits.append({"id": spirit.id, "element": spirit.element})
    
    # ========== 3. 卸下魔魂 ==========
    unequipped_mosouls = []
    equipped_mosouls = services.mosoul_repo.get_equipped_by_beast_id(beast_id)
    for mosoul in equipped_mosouls:
        mosoul.beast_id = None
        services.mosoul_repo.save(mosoul)
        unequipped_mosouls.append({"id": mosoul.id, "name": mosoul.name})
    
    # ========== 4. 根据境界返还进化材料 ==========
    returned_items = []
    realm_to_material = {
        "地界": 3010,   # 神·逆鳞
        "天界": 3012,   # 进化神草
        "神界": 3014,   # 进化圣水晶
    }
    material_id = realm_to_material.get(beast_realm)
    if material_id:
        services.inventory_service.add_item(user_id, material_id, 1)
        item_info = services.item_repo.get_by_id(material_id)
        item_name = item_info.name if item_info else f"物品{material_id}"
        returned_items.append({"item_id": material_id, "name": item_name, "quantity": 1})
    
    # ========== 5. 计算化仙池经验 ==========
    pool_exp_added = 0
    try:
        pool_status = services.immortalize_pool_service.get_status(user_id)
        pool_level = pool_status.get("level", 1)
        ratio = services.immortalize_pool_service.config.get_beast_ratio(pool_level)
        beast_total_exp = _calc_total_exp(getattr(beast, "level", 1), beast_exp)
        if ratio > 0 and beast_total_exp > 0:
            exp_to_add = int(beast_total_exp * ratio)
            if exp_to_add > 0:
                result = services.immortalize_pool_service.add_exp(user_id, exp_to_add)
                pool_exp_added = result.get("added_exp", 0)
    except Exception:
        pass  # 化仙池异常不影响放生流程
    
    # ========== 6. 删除幻兽 ==========
    success = services.player_beast_repo.delete_beast(beast_id, user_id)
    if not success:
        return jsonify({"ok": False, "error": "放生失败"})
    
    return jsonify({
        "ok": True,
        "message": f"{beast_name}已化仙",
        "unequipped_bones": unequipped_bones,
        "unequipped_spirits": unequipped_spirits,
        "unequipped_mosouls": unequipped_mosouls,
        "returned_items": returned_items,
        "pool_exp_added": pool_exp_added,
    })


@beast_bp.get("/templates")
def get_beast_templates():
    """获取所有幻兽模板列表"""
    all_templates = services.beast_template_repo.get_all()
    
    return jsonify({
        "ok": True,
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "race": t.race,
                "rarity": t.rarity,
                "trait": t.trait,
                "attackType": t.attack_type,
                "realm": t.realm,
            }
            for t in all_templates.values()
        ],
        "totalCount": len(all_templates),
    })


@beast_bp.post("/add-exp")
def add_beast_exp():
    """给幻兽增加经验（化仙池经验分配）
    
    请求参数：
    - beastId: 幻兽ID
    - exp: 要分配的经验值
    
    返回：
    - ok: 是否成功
    - oldLevel: 原等级
    - newLevel: 新等级
    - levelUp: 是否升级
    - levelsGained: 升了几级
    - currentExp: 当前经验
    - expToNext: 升级所需经验
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    exp_amount = data.get("exp", 0)
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    if not isinstance(exp_amount, int) or exp_amount <= 0:
        return jsonify({"ok": False, "error": "经验值必须是正整数"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    old_level = beast.level
    
    # 加载经验配置
    global _LEVEL_EXP_CONFIG
    if _LEVEL_EXP_CONFIG is None:
        _LEVEL_EXP_CONFIG = _load_level_exp_config()
    
    max_level = _LEVEL_EXP_CONFIG.get("max_level", 100)
    exp_map = _LEVEL_EXP_CONFIG.get("exp_to_next_level", {})
    
    # 已满级检查
    if beast.level >= max_level:
        return jsonify({"ok": False, "error": "幻兽已满级，无法分配经验"})
    
    # 增加经验并处理升级
    beast.exp = (beast.exp or 0) + exp_amount
    
    # 循环处理升级
    while beast.level < max_level:
        exp_needed = exp_map.get(str(beast.level), 0)
        if exp_needed <= 0:
            break  # 配置缺失，停止升级
        if beast.exp >= exp_needed:
            beast.exp -= exp_needed
            beast.level += 1
        else:
            break
    
    # 计算升了几级
    levels_gained = beast.level - old_level
    
    # 重新计算属性（无论是否升级都重新计算，以修复旧数据）
    beast = _calc_beast_stats(beast)
    
    # 保存到数据库
    services.player_beast_repo.update_beast(beast)
    
    # 获取下一级所需经验
    exp_to_next = exp_map.get(str(beast.level), 0) if beast.level < max_level else 0
    
    return jsonify({
        "ok": True,
        "message": f"成功为【{beast.name}】分配{exp_amount}点经验" + (f"，升了{levels_gained}级！" if levels_gained > 0 else "！"),
        "beastName": beast.name,
        "oldLevel": old_level,
        "newLevel": beast.level,
        "levelUp": levels_gained > 0,
        "levelsGained": levels_gained,
        "currentExp": beast.exp,
        "expToNext": exp_to_next,
    })


@beast_bp.post("/add-exp-from-pool")
def add_beast_exp_from_pool():
    """从化仙池分配经验给幻兽
    
    请求参数：
    - beastId: 幻兽ID
    - exp: 要分配的经验值
    
    会先从化仙池扣除经验，再加到幻兽身上
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    exp_amount = data.get("exp", 0)
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    if not isinstance(exp_amount, int) or exp_amount <= 0:
        return jsonify({"ok": False, "error": "经验值必须是正整数"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    # 从化仙池扣除经验
    try:
        services.immortalize_pool_service.spend_exp(user_id, exp_amount)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    
    old_level = beast.level
    
    # 加载经验配置
    global _LEVEL_EXP_CONFIG
    if _LEVEL_EXP_CONFIG is None:
        _LEVEL_EXP_CONFIG = _load_level_exp_config()
    
    max_level = _LEVEL_EXP_CONFIG.get("max_level", 100)
    exp_map = _LEVEL_EXP_CONFIG.get("exp_to_next_level", {})
    
    # 已满级检查（但仍然扣除经验，只是不升级）
    if beast.level >= max_level:
        return jsonify({
            "ok": True,
            "message": f"幻兽已满级，经验已消耗但无法提升等级",
            "beastName": beast.name,
            "oldLevel": old_level,
            "newLevel": beast.level,
            "levelUp": False,
            "levelsGained": 0,
        })
    
    # 增加经验并处理升级
    beast.exp = (beast.exp or 0) + exp_amount
    
    # 循环处理升级
    while beast.level < max_level:
        exp_needed = exp_map.get(str(beast.level), 0)
        if exp_needed <= 0:
            break
        if beast.exp >= exp_needed:
            beast.exp -= exp_needed
            beast.level += 1
        else:
            break
    
    levels_gained = beast.level - old_level
    
    # 重新计算属性
    beast = _calc_beast_stats(beast)
    
    # 保存到数据库
    services.player_beast_repo.update_beast(beast)
    
    exp_to_next = exp_map.get(str(beast.level), 0) if beast.level < max_level else 0
    
    return jsonify({
        "ok": True,
        "message": f"成功为【{beast.name}】分配{exp_amount}点经验" + (f"，升了{levels_gained}级！" if levels_gained > 0 else "！"),
        "beastName": beast.name,
        "oldLevel": old_level,
        "newLevel": beast.level,
        "levelUp": levels_gained > 0,
        "levelsGained": levels_gained,
        "currentExp": beast.exp,
        "expToNext": exp_to_next,
    })


@beast_bp.post("/evolve")
def evolve_beast():
    """幻兽进化
    
    请求参数：
    - beastId: 幻兽ID
    - nextRealm: 目标境界
    - realmMultiplier: 境界倍率
    
    返回：
    - ok: 是否成功
    - oldRealm: 原境界
    - newRealm: 新境界
    - beast: 更新后的幻兽信息
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    beast_id = data.get("beastId")
    next_realm = data.get("nextRealm", "")
    realm_multiplier = data.get("realmMultiplier", 1.0)
    
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400
    
    if not next_realm:
        return jsonify({"ok": False, "error": "缺少目标境界"}), 400
    
    # 获取幻兽
    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404
    
    old_realm = beast.realm
    
    # ==================== 扣除进化材料 ====================
    # 常量：物品ID
    SHEN_NI_LIN_ITEM_ID = 3010
    EVOLVE_STONE_IDS = {
        20: 3001,  # 黄阶进化石
        30: 3002,  # 玄阶进化石
        40: 3003,  # 地阶进化石
        50: 3004,  # 天阶进化石
        60: 3005,  # 飞马进化石
        70: 3006,  # 天龙进化石
        80: 3007   # 战神进化石
    }
    
    evolve_transition = f"{old_realm}->{next_realm}"
    
    try:
        # 1. 地界->灵界：扣除神·逆鳞×1 + 进化石×10
        if evolve_transition == "地界->灵界":
            # 获取玩家等级来确定进化石
            player = services.player_repo.get_by_id(user_id)
            if not player:
                return jsonify({"ok": False, "error": "玩家不存在"}), 404
            
            player_level = player.level
            # 确定进化石ID（根据玩家等级段）
            evolve_stone_id = None
            for level_threshold in sorted(EVOLVE_STONE_IDS.keys(), reverse=True):
                if player_level >= level_threshold:
                    evolve_stone_id = EVOLVE_STONE_IDS[level_threshold]
                    break
            
            if not evolve_stone_id:
                return jsonify({"ok": False, "error": "玩家等级不足20级，无法进化"}), 400
            
            # 扣除神·逆鳞×1
            services.inventory_service.remove_item(user_id, SHEN_NI_LIN_ITEM_ID, 1)
            # 扣除进化石×10
            services.inventory_service.remove_item(user_id, evolve_stone_id, 10)
        
        # 2. 灵界->神界：扣除神·逆鳞×4 + 进化神草×90 + 铜钱200万
        elif evolve_transition == "灵界->神界":
            # 获取玩家信息
            player = services.player_repo.get_by_id(user_id)
            if not player:
                return jsonify({"ok": False, "error": "玩家不存在"}), 404
            
            # 检查铜钱
            if player.gold < 2000000:
                return jsonify({"ok": False, "error": "铜钱不足，需要200万铜钱"}), 400
            
            # 扣除神·逆鳞×4
            services.inventory_service.remove_item(user_id, SHEN_NI_LIN_ITEM_ID, 4)
            # 扣除进化神草×90（需要通过名称查找item_id）
            # 查找进化神草的item_id
            evolve_god_herb_items = [item for item in services.inventory_service.get_user_items(user_id) 
                                      if item.name == "进化神草"]
            if not evolve_god_herb_items:
                return jsonify({"ok": False, "error": "背包中没有进化神草"}), 400
            evolve_god_herb_id = evolve_god_herb_items[0].item_id
            services.inventory_service.remove_item(user_id, evolve_god_herb_id, 90)
            
            # 扣除铜钱200万
            player.gold -= 2000000
            services.player_repo.update_player(player)
        
        # 3. 神界->天界：扣除神·逆鳞×10 + 进化水晶×60 + 铜钱500万
        elif evolve_transition == "神界->天界":
            # 获取玩家信息
            player = services.player_repo.get_by_id(user_id)
            if not player:
                return jsonify({"ok": False, "error": "玩家不存在"}), 404
            
            # 检查铜钱
            if player.gold < 5000000:
                return jsonify({"ok": False, "error": "铜钱不足，需要500万铜钱"}), 400
            
            # 扣除神·逆鳞×10
            services.inventory_service.remove_item(user_id, SHEN_NI_LIN_ITEM_ID, 10)
            # 扣除进化水晶×60（需要通过名称查找item_id）
            evolve_crystal_items = [item for item in services.inventory_service.get_user_items(user_id) 
                                     if item.name == "进化水晶"]
            if not evolve_crystal_items:
                return jsonify({"ok": False, "error": "背包中没有进化水晶"}), 400
            evolve_crystal_id = evolve_crystal_items[0].item_id
            services.inventory_service.remove_item(user_id, evolve_crystal_id, 60)
            
            # 扣除铜钱500万
            player.gold -= 5000000
            services.player_repo.update_player(player)
    
    except Exception as e:
        # 捕获所有错误（包括材料不足）
        error_msg = str(e)
        if "数量不足" in error_msg or "不足" in error_msg:
            return jsonify({"ok": False, "error": f"材料不足：{error_msg}"}), 400
        return jsonify({"ok": False, "error": f"扣除材料失败：{error_msg}"}), 400
    
    # ==================== 更新境界 ====================
    # 更新境界
    beast.realm = next_realm

    # 计算并应用资质提升（按模板 realms 配置）
    boosts = calc_aptitude_boost(beast.name, old_realm, next_realm)
    
    # 应用资质提升
    beast.hp_aptitude += boosts.get('hp_aptitude', 0)
    beast.speed_aptitude += boosts.get('speed_aptitude', 0)
    beast.physical_attack_aptitude += boosts.get('physical_atk_aptitude', 0)
    beast.magic_attack_aptitude += boosts.get('magic_atk_aptitude', 0)
    beast.physical_defense_aptitude += boosts.get('physical_def_aptitude', 0)
    beast.magic_defense_aptitude += boosts.get('magic_def_aptitude', 0)
    
    # 重新计算属性（使用新境界的倍率和提升后的资质）
    beast = _calc_beast_stats(beast)
    
    # 保存到数据库
    services.player_beast_repo.update_beast(beast)
    
    # 返回更新后的幻兽信息
    beast_dict = beast.to_dict()
    template_id = int(beast_dict.get("template_id") or getattr(beast, "template_id", 0) or 0)
    if template_id > 0:
        beast_dict["template_id"] = template_id
    else:
        name = str(getattr(beast, "name", "") or "")
        template = services.beast_template_repo.get_by_name(name)
        if template is None:
            def _norm(s: str) -> str:
                return "".join(ch for ch in str(s or "") if ch not in {" ", "\t", "\r", "\n", "·"})

            key = _norm(name)
            if key:
                for tpl in services.beast_template_repo.get_all().values():
                    if _norm(getattr(tpl, "name", "")) == key:
                        template = tpl
                        break
        beast_dict["template_id"] = template.id if template else None
    
    return jsonify({
        "ok": True,
        "message": f"【{beast.name}】成功进化至{next_realm}！",
        "oldRealm": old_realm,
        "newRealm": next_realm,
        "beast": beast_dict,
    })


@beast_bp.post("/rebirth")
def rebirth_beast():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    beast_id = int(data.get("beastId", 0) or 0)
    mode = str(data.get("mode", "normal") or "normal")

    if beast_id <= 0:
        return jsonify({"ok": False, "error": "缺少幻兽ID"}), 400

    beast = services.player_beast_repo.get_by_id(beast_id)
    if not beast or beast.user_id != user_id:
        return jsonify({"ok": False, "error": "幻兽不存在"}), 404

    NORMAL_REBIRTH_ITEM_ID = 6017
    MAGIC_REBIRTH_ITEM_ID = 6016

    template = services.beast_template_repo.get_by_id(int(getattr(beast, "template_id", 0) or 0))
    if template is None:
        return jsonify({"ok": False, "error": "幻兽模板不存在"}), 400

    import random
    from domain.services.skill_system import get_skill_config

    personalities = ["勇敢", "精明", "胆小", "谨慎", "傻瓜"]

    def roll_aptitude(max_value: int) -> int:
        try:
            mv = int(max_value or 0)
        except (TypeError, ValueError):
            mv = 0
        if mv <= 0:
            return 0
        x = random.randint(0, 349)
        v = mv - x
        return v if v > 0 else 0

    def choose_initial_skill_names(all_skill_ids):
        ids = list(all_skill_ids or [])
        n = len(ids)
        if n <= 0:
            return []
        k = random.randint(0, n)
        if k <= 0:
            return []
        chosen_ids = random.sample(ids, k)

        config = get_skill_config()
        id_map = config.get("skill_ids", {})
        id_to_name = {v: k for k, v in id_map.items()}
        names = []
        for sid in chosen_ids:
            nm = id_to_name.get(sid)
            if nm:
                names.append(nm)
        return names

    try:
        if mode == "magic":
            services.inventory_service.remove_item(user_id, MAGIC_REBIRTH_ITEM_ID, 1)
        else:
            services.inventory_service.remove_item(user_id, NORMAL_REBIRTH_ITEM_ID, 1)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    beast.hp_aptitude = roll_aptitude(getattr(template, "hp_aptitude_max", 0))
    beast.speed_aptitude = roll_aptitude(getattr(template, "speed_aptitude_max", 0))
    beast.physical_attack_aptitude = roll_aptitude(getattr(template, "physical_atk_aptitude_max", 0))
    beast.magic_attack_aptitude = roll_aptitude(getattr(template, "magic_atk_aptitude_max", 0))
    beast.physical_defense_aptitude = roll_aptitude(getattr(template, "physical_def_aptitude_max", 0))
    beast.magic_defense_aptitude = roll_aptitude(getattr(template, "magic_def_aptitude_max", 0))
    beast.personality = random.choice(personalities)

    if mode != "magic":
        beast.level = 1
        beast.exp = 0
        beast.realm = "地界"
        beast.skills = choose_initial_skill_names(getattr(template, "all_skill_ids", []))

    beast = _calc_beast_stats(beast)
    services.player_beast_repo.update_beast(beast)

    return jsonify({
        "ok": True,
        "mode": mode,
        "beastId": beast_id,
    })
