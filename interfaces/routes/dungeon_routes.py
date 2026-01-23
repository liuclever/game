from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update, get_connection
from interfaces.web_api.bootstrap import services
from domain.services.pvp_battle_engine import PvpPlayer, PvpBeast, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills
from infrastructure.config.bone_system_config import get_bone_system_config
from application.services.inventory_service import InventoryError
import json
import random
import os
from datetime import date
from datetime import datetime
import math

dungeon_bp = Blueprint('dungeon', __name__, url_prefix='/api/dungeon')

DEFAULT_TOTAL_FLOORS = 35
BOSS_FLOORS = {35}  # 只有最后一层是 BOSS
RANDOM_EVENT_FLOORS = {5, 10, 15, 20, 25, 30}

# 楼层事件类型概率
def generate_floor_event_type(floor):
    """根据楼层生成事件类型"""
    if floor in RANDOM_EVENT_FLOORS:
        return random.choice(['climb', 'vitality_spring', 'rps'])
    
    if floor in BOSS_FLOORS:
        return 'boss'
    
    # 非 BOSS 层：75% 幻兽，10% 巨型宝箱，15% 神秘宝箱
    roll = random.random()
    if roll < 0.75:
        return 'beast'
    elif roll < 0.85:
        return 'giant_chest'
    else:
        return 'mystery_chest'

def load_dungeon_beasts_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/dungeon_beasts.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_dungeon_by_name(dungeon_name):
    config = load_dungeon_beasts_config()
    for dungeon_id, dungeon_data in config['dungeons'].items():
        if dungeon_data['name'] == dungeon_name:
            return dungeon_data
    return None


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _load_maps_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/maps.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _find_city_index(maps: list, city_name: str) -> int:
    for i, m in enumerate(maps):
        if m.get('name') == city_name:
            return i
    return -1


def _get_remaining_move_seconds(user_id: int) -> int:
    rows = execute_query(
        "SELECT location, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return 0

    row = rows[0]
    moving_to = row.get('moving_to')
    started_at = row.get('last_map_move_at')
    if not moving_to or not isinstance(started_at, datetime):
        return 0

    current_city = row.get('location') or '落龙镇'
    maps = _load_maps_config()
    start_index = _find_city_index(maps, current_city)
    target_index = _find_city_index(maps, moving_to)
    if start_index < 0 or target_index < 0:
        return 0

    distance = abs(target_index - start_index)
    total_seconds = distance * 60
    elapsed = (datetime.now() - started_at).total_seconds()
    remaining = int(math.ceil(total_seconds - elapsed))
    return max(0, remaining)


def _ensure_not_moving(user_id: int):
    remaining = _get_remaining_move_seconds(user_id)
    if remaining > 0:
        return jsonify({"ok": False, "error": f"移动中，无法进行副本操作（剩余{remaining}秒）"}), 400
    return None


def _ensure_daily_dice(user_id: int):
    today = date.today()
    try:
        rows = execute_query(
            "SELECT dice, last_dice_grant_date FROM player WHERE user_id = %s",
            (user_id,),
        )
        if not rows:
            return

        row = rows[0]
        last_date = row.get('last_dice_grant_date')
        if last_date and str(last_date) == str(today):
            return

        execute_update(
            "UPDATE player SET dice = GREATEST(dice, 15), last_dice_grant_date = %s WHERE user_id = %s",
            (today, user_id),
        )
    except Exception:
        execute_update(
            "UPDATE player SET dice = GREATEST(dice, 15) WHERE user_id = %s",
            (user_id,),
        )


def _to_pvp_beasts_from_player(raw_beasts: list) -> list[PvpBeast]:
    """将数据库中的幻兽数据转换为 PvpBeast，包含装备和技能加成。"""
    beasts: list[PvpBeast] = []
    for b in raw_beasts:
        # nature 中包含“法系”则按法攻，否则按物攻
        nature = getattr(b, "nature", "") or ""
        attack_type = "magic" if "法" in nature else "physical"
        skills = getattr(b, "skills", []) or []

        # 裸属性
        raw_hp = int(getattr(b, "hp", 0) or 0)
        raw_pa = int(getattr(b, "physical_attack", 0) or 0)
        raw_ma = int(getattr(b, "magic_attack", 0) or 0)
        raw_pd = int(getattr(b, "physical_defense", 0) or 0)
        raw_md = int(getattr(b, "magic_defense", 0) or 0)
        raw_spd = int(getattr(b, "speed", 0) or 0)

        # 1) 战灵加成 (百分比)
        hp = raw_hp
        pa = raw_pa
        ma = raw_ma
        pd = raw_pd
        md = raw_md
        spd = raw_spd

        try:
            equipped_spirits = services.spirit_repo.get_by_beast_id(b.id)
        except Exception:
            equipped_spirits = []

        hp_bp, pa_bp, ma_bp, pd_bp, md_bp, spd_bp = 0, 0, 0, 0, 0, 0
        for sp in equipped_spirits:
            for ln in getattr(sp, "lines", []) or []:
                if not getattr(ln, "unlocked", False):
                    continue
                attr = getattr(ln, "attr_key", "") or ""
                val = int(getattr(ln, "value_bp", 0) or 0)
                if attr == "hp_pct": hp_bp += val
                elif attr == "attack_pct":
                    if attack_type == "magic": ma_bp += val
                    else: pa_bp += val
                elif attr == "physical_defense_pct": pd_bp += val
                elif attr == "magic_defense_pct": md_bp += val
                elif attr == "speed_pct": spd_bp += val

        hp += int(raw_hp * hp_bp / 10000)
        pa += int(raw_pa * pa_bp / 10000)
        ma += int(raw_ma * ma_bp / 10000)
        pd += int(raw_pd * pd_bp / 10000)
        md += int(raw_md * md_bp / 10000)
        spd += int(raw_spd * spd_bp / 10000)

        # 2) 战骨加成 (固定值)
        bone_cfg = get_bone_system_config()
        try:
            bones = services.bone_repo.get_by_beast_id(b.id)
        except Exception:
            bones = []

        bone_hp, bone_atk, bone_pd, bone_md, bone_spd = 0, 0, 0, 0, 0
        for bn in bones:
            st = bone_cfg.calc_bone_stats(bn.stage, bn.slot, bn.level)
            bone_hp += int(st.get("hp", 0) or 0)
            bone_atk += max(int(st.get("physical_attack", 0) or 0), int(st.get("magic_attack", 0) or 0))
            bone_pd += int(st.get("physical_defense", 0) or 0)
            bone_md += int(st.get("magic_defense", 0) or 0)
            bone_spd += int(st.get("speed", 0) or 0)

        hp += bone_hp
        pd += bone_pd
        md += bone_md
        spd += bone_spd
        if attack_type == "magic": ma += bone_atk
        else: pa += bone_atk

        # 3) 技能加成
        (f_hp, f_pa, f_ma, f_pd, f_md, f_spd, spec) = apply_buff_debuff_skills(
            skills=skills, attack_type=attack_type,
            raw_hp=hp, raw_physical_attack=pa, raw_magic_attack=ma,
            raw_physical_defense=pd, raw_magic_defense=md, raw_speed=spd
        )

        beasts.append(PvpBeast(
            id=b.id, name=b.name, hp_max=f_hp, hp_current=f_hp,
            physical_attack=f_pa, magic_attack=f_ma,
            physical_defense=f_pd, magic_defense=f_md, speed=f_spd,
            attack_type=attack_type, skills=skills,
            hp_aptitude=getattr(b, "hp_aptitude", 0) or 0,
            attack_aptitude=getattr(b, "magic_attack_aptitude", 0) or (getattr(b, "physical_attack_aptitude", 0) or 0),
            physical_defense_aptitude=getattr(b, "physical_defense_aptitude", 0) or 0,
            magic_defense_aptitude=getattr(b, "magic_defense_aptitude", 0) or 0,
            speed_aptitude=getattr(b, "speed_aptitude", 0) or 0,
            poison_enhance=spec.get("poison_enhance", 0.0),
            critical_resist=spec.get("critical_resist", 0.0),
            immune_counter=bool(spec.get("immune_counter", False)),
            poison_resist=spec.get("poison_resist", 0.0)
        ))
    return beasts


def _to_pvp_beasts_from_config(config_beasts: list) -> list[PvpBeast]:
    """将副本配置中的幻兽数据转换为 PvpBeast。"""
    beasts: list[PvpBeast] = []
    for i, b in enumerate(config_beasts):
        stats = b.get('stats', {})
        attack_type = b.get('attack_type', 'physical')
        if attack_type == 'magical': attack_type = 'magic'
        
        # 副本幻兽属性直接使用配置值，不计算装备加成
        hp = stats.get('hp', 0)
        pa = stats.get('atk', 0) if attack_type == 'physical' else 0
        ma = stats.get('matk', 0) if attack_type == 'magic' else 0
        pd = stats.get('def', 0)
        md = stats.get('mdef', 0)
        spd = stats.get('speed', 0)
        
        # 副本幻兽技能生效 (根据 dungeon_beasts.json 说明，有些可能不触发，但逻辑上支持)
        skills = b.get('skills', [])
        
        (f_hp, f_pa, f_ma, f_pd, f_md, f_spd, spec) = apply_buff_debuff_skills(
            skills=skills, attack_type=attack_type,
            raw_hp=hp, raw_physical_attack=pa, raw_magic_attack=ma,
            raw_physical_defense=pd, raw_magic_defense=md, raw_speed=spd
        )

        beasts.append(PvpBeast(
            id=-(i + 1), # 使用负数 ID 区分副本幻兽
            name=b['name'], hp_max=f_hp, hp_current=f_hp,
            physical_attack=f_pa, magic_attack=f_ma,
            physical_defense=f_pd, magic_defense=f_md, speed=f_spd,
            attack_type=attack_type, skills=skills,
            poison_enhance=spec.get("poison_enhance", 0.0),
            critical_resist=spec.get("critical_resist", 0.0),
            immune_counter=bool(spec.get("immune_counter", False)),
            poison_resist=spec.get("poison_resist", 0.0)
        ))
    return beasts


def _format_battle_result(pvp_result, attacker_name, defender_name):
    """将 PvpBattleResult 转换为前端需要的 battles 结构。"""
    def build_segment(battle_idx, logs):
        if not logs: return None
        rounds = []
        for idx, log in enumerate(logs, start=1):
            rounds.append({
                "round": idx,
                "action": log.description,
                "a_hp": log.attacker_hp_after,
                "d_hp": log.defender_hp_after,
            })
        
        # 判定胜负
        last = logs[-1]
        # player_id == 0 表示副本方(defender_name)，非0表示玩家方(attacker_name)
        # 注意：这里的attacker/defender是本次攻击行为中的攻守方，而非整场战斗的挑战者/被挑战者
        log_attacker_owner = attacker_name if last.attacker_player_id != 0 else defender_name
        log_defender_owner = attacker_name if last.defender_player_id != 0 else defender_name
        
        if last.defender_hp_after <= 0:
            winner = "attacker"
            res_text = f"『{log_defender_owner}』的{last.defender_name}阵亡，『{log_attacker_owner}』的{last.attacker_name}获胜"
        else:
            # 这种情况通常是反击/反震导致攻击者阵亡，或者回合结束
            winner = "defender"
            res_text = f"『{log_attacker_owner}』的{last.attacker_name}阵亡，『{log_defender_owner}』的{last.defender_name}获胜"
            
        return {
            "battle_num": battle_idx,
            "winner": winner,
            "rounds": rounds,
            "result": res_text
        }

    battles = []
    current_pair = None
    current_logs = []
    
    for log in pvp_result.logs:
        pair = frozenset({log.attacker_beast_id, log.defender_beast_id})
        if current_pair is None:
            current_pair = pair
            current_logs.append(log)
        elif pair == current_pair:
            current_logs.append(log)
        else:
            seg = build_segment(len(battles) + 1, current_logs)
            if seg: battles.append(seg)
            current_pair = pair
            current_logs = [log]
            
    if current_logs:
        seg = build_segment(len(battles) + 1, current_logs)
        if seg: battles.append(seg)
        
    return battles


DICE_BAG_ITEM_ID = 6010

def get_bone_soul_item_id(dungeon_name):
    """根据副本/地图获取对应的骨魂 ID"""
    dungeon_config = load_dungeon_config()
    
    # 查找所属地图
    target_map = None
    target_dungeon = None
    for m in dungeon_config['maps']:
        for d in m['dungeons']:
            if d['name'] == dungeon_name:
                target_map = m
                target_dungeon = d
                break
        if target_map: break
        
    if not target_map:
        return None
        
    map_name = target_map['map_name']
    
    if map_name == "幻灵镇": return 2001 # 碎空骨魂
    if map_name == "定老城": return 2002 # 猎魔骨魂
    if map_name == "迷雾城": return 2003 # 龙炎骨魂
    if map_name == "飞龙港": return 2004 # 奔雷骨魂
    if map_name == "落龙镇": return 2005 # 凌霄骨魂
    if map_name == "圣龙城":
        if dungeon_name == "皇城迷宫": return 2007 # 武神骨魂
        return 2006 # 麒麟骨魂
    if map_name == "乌托邦":
        if dungeon_name == "幻光公园": return 2009 # 毁灭骨魂
        return 2008 # 弑天骨魂
        
    return None


@dungeon_bp.route('/dice-info', methods=['GET'])
def get_dice_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err

    _ensure_daily_dice(user_id)
    
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
    bag_count = services.inventory_service.get_item_count(user_id, DICE_BAG_ITEM_ID)
    
    return jsonify({
        "ok": True,
        "dice": player.dice,
        "bag_count": bag_count
    })


@dungeon_bp.route('/dice/use-bag', methods=['POST'])
def use_dice_bag():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err

    _ensure_daily_dice(user_id)
    
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
    bag_count = services.inventory_service.get_item_count(user_id, DICE_BAG_ITEM_ID)
    if bag_count <= 0:
        return jsonify({"ok": False, "error": "骰子包不足"}), 400
        
    # 消耗 1 个骰子包
    services.inventory_service.remove_item(user_id, DICE_BAG_ITEM_ID, 1)
    
    # 获得 10 个骰子
    player.dice += 10
    services.player_repo.save(player)
    
    return jsonify({
        "ok": True,
        "message": "使用成功，获得10个骰子",
        "dice": player.dice,
        "bag_count": bag_count - 1
    })


def load_dungeon_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/dungeon_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@dungeon_bp.route('/progress', methods=['GET'])
def get_progress():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err

    _ensure_daily_dice(user_id)
    
    # 检查等级限制
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    dungeon_config = load_dungeon_config()
    current_map = next((m for m in dungeon_config['maps'] if m['map_name'] == player.location), None)
    
    if current_map and player.level < current_map['player_level_min']:
        return jsonify({"ok": False, "error": f"等级不足，需达到{current_map['player_level_min']}级才能进入{player.location}副本"}), 403

    dungeon_name = request.args.get('dungeon_name', '镇妖塔')
    
    # 每日重置上限：5次
    DAILY_RESET_LIMIT = 5
    
    sql = """
        SELECT current_floor, total_floors, floor_cleared, floor_event_type, resets_today, last_reset_date, loot_claimed
        FROM player_dungeon_progress 
        WHERE user_id = %s AND dungeon_name = %s
    """
    results = execute_query(sql, (user_id, dungeon_name))
    
    if results:
        row = results[0]
        floor_cleared = row.get('floor_cleared', True)
        if floor_cleared is None:
            floor_cleared = True
        floor_event_type = row.get('floor_event_type', 'beast')
        if not floor_event_type:
            floor_event_type = 'beast'
        
        loot_claimed = row.get('loot_claimed', True)
        if loot_claimed is None:
            loot_claimed = True
        
        # 处理每日重置计数
        resets_today = row.get('resets_today', 0)
        last_reset_date = row.get('last_reset_date')
        if last_reset_date and str(last_reset_date) != str(date.today()):
            resets_today = 0
            
        player = services.player_repo.get_by_id(user_id)
        dice_count = player.dice if player else 0
        
        return jsonify({
            "ok": True,
            "current_floor": row['current_floor'],
            "total_floors": row['total_floors'],
            "floor_cleared": floor_cleared,
            "floor_event_type": floor_event_type,
            "dice": dice_count,
            "energy": f"{player.energy}/{player.max_energy}",
            "resets_today": resets_today,
            "reset_limit": DAILY_RESET_LIMIT,
            "loot_claimed": loot_claimed
        })
    else:
        player = services.player_repo.get_by_id(user_id)
        dice_count = player.dice if player else 0
        
        return jsonify({
            "ok": True,
            "current_floor": 1,
            "total_floors": DEFAULT_TOTAL_FLOORS,
            "floor_cleared": True,
            "floor_event_type": "beast",
            "dice": dice_count,
            "resets_today": 0,
            "reset_limit": DAILY_RESET_LIMIT,
            "loot_claimed": True
        })


def load_vip_privileges():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/vip_privileges.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@dungeon_bp.route('/reset', methods=['POST'])
def reset_dungeon():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '镇妖塔')
    
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 每日重置上限：5次
    DAILY_RESET_LIMIT = 5
    RESET_COST = 200  # 元宝
            
    # 检查当前重置次数
    sql = "SELECT resets_today, last_reset_date FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s"
    results = execute_query(sql, (user_id, dungeon_name))
    
    resets_today = 0
    if results:
        resets_today = results[0].get('resets_today', 0)
        last_reset_date = results[0].get('last_reset_date')
        # 如果是新的一天，重置计数
        if last_reset_date and str(last_reset_date) != str(date.today()):
            resets_today = 0
            
    if resets_today >= DAILY_RESET_LIMIT:
        return jsonify({"ok": False, "error": f"今日重置次数已达上限({DAILY_RESET_LIMIT}次)"}), 400
        
    # 检查元宝
    if player.yuanbao < RESET_COST:
        return jsonify({"ok": False, "error": f"元宝不足，重置副本需要{RESET_COST}元宝"}), 400
        
    # 扣除元宝
    player.yuanbao -= RESET_COST
    services.player_repo.save(player)
    
    # 重置进度
    execute_update("""
        INSERT INTO player_dungeon_progress (user_id, dungeon_name, current_floor, floor_cleared, floor_event_type, resets_today, last_reset_date, loot_claimed)
        VALUES (%s, %s, 1, TRUE, 'beast', %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE 
            current_floor = 1, 
            floor_cleared = TRUE, 
            floor_event_type = 'beast', 
            resets_today = %s, 
            last_reset_date = %s,
            loot_claimed = TRUE,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, dungeon_name, resets_today + 1, date.today(), resets_today + 1, date.today()))
    
    return jsonify({
        "ok": True,
        "message": f"重置成功！消耗{RESET_COST}元宝，已从第一层开始挑战",
        "current_floor": 1,
        "resets_today": resets_today + 1,
        "yuanbao": player.yuanbao
    })


@dungeon_bp.route('/advance', methods=['POST'])
def advance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err

    _ensure_daily_dice(user_id)
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '镇妖塔')
    dice_value = data.get('dice_value')
    
    if dice_value is None:
        dice_value = random.randint(1, 6)
    else:
        try:
            dice_value = int(dice_value)
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "骰子点数格式无效"}), 400
    
    if dice_value < 1 or dice_value > 6:
        return jsonify({"ok": False, "error": "骰子点数无效"}), 400
    
    sql = """
        SELECT current_floor, total_floors, floor_cleared, floor_event_type 
        FROM player_dungeon_progress 
        WHERE user_id = %s AND dungeon_name = %s
    """
    results = execute_query(sql, (user_id, dungeon_name))
    
    if results:
        old_floor = results[0]['current_floor']
        total_floors = results[0]['total_floors']
        floor_cleared = results[0].get('floor_cleared', True)
        floor_event_type = results[0].get('floor_event_type') or 'beast'
        if floor_cleared is None:
            floor_cleared = True
    else:
        old_floor = 1
        total_floors = DEFAULT_TOTAL_FLOORS
        floor_cleared = True
        floor_event_type = 'beast'
    
    if not floor_cleared and floor_event_type in ('beast', 'boss'):
        return jsonify({"ok": False, "error": "请先击败本层幻兽才能前进"}), 400
    
    # 规则：35层通关后必须重置
    if old_floor == total_floors and floor_cleared:
        return jsonify({"ok": False, "error": "已通关本副本，请先重置后再继续挑战"}), 400
    
    # 检查并扣除骰子
    player = services.player_repo.get_by_id(user_id)
    if not player or player.dice <= 0:
        return jsonify({"ok": False, "error": "骰子不足，请先补充"}), 400
    
    player.dice -= 1
    services.player_repo.save(player)
    
    new_floor = old_floor + dice_value
    
    # 规则：不可以跳过最后一层
    if old_floor < total_floors and new_floor >= total_floors:
        new_floor = total_floors
    
    # 生成楼层事件类型
    floor_event_type = generate_floor_event_type(new_floor)
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            upsert_sql = """
                INSERT INTO player_dungeon_progress (user_id, dungeon_name, current_floor, total_floors, floor_cleared, floor_event_type, loot_claimed)
                VALUES (%s, %s, %s, %s, FALSE, %s, TRUE)
                ON DUPLICATE KEY UPDATE 
                    current_floor = VALUES(current_floor), 
                    floor_cleared = FALSE, 
                    floor_event_type = VALUES(floor_event_type), 
                    loot_claimed = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(upsert_sql, (user_id, dungeon_name, new_floor, total_floors, floor_event_type))
            conn.commit()
    finally:
        conn.close()
    
    return jsonify({
        "ok": True,
        "old_floor": old_floor,
        "new_floor": new_floor,
        "dice_value": dice_value,
        "dice": player.dice,
        "total_floors": total_floors,
        "floor_event_type": floor_event_type
    })


MIZONG_ITEM_ID = 6002


@dungeon_bp.route('/mizong/info', methods=['GET'])
def get_mizong_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    count = services.inventory_service.get_item_count(user_id, MIZONG_ITEM_ID)
    return jsonify({"ok": True, "count": count})


@dungeon_bp.route('/mizong/use', methods=['POST'])
def use_mizong():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '镇妖塔')
    steps = int(data.get('steps', 0))
    
    if steps < 1 or steps > 6:
        return jsonify({"ok": False, "error": "前进层数无效，必须为1-6"}), 400
    
    count = services.inventory_service.get_item_count(user_id, MIZONG_ITEM_ID)
    if count <= 0:
        return jsonify({"ok": False, "error": "迷踪符不足"}), 400
    
    sql = """
        SELECT current_floor, total_floors, floor_cleared, floor_event_type 
        FROM player_dungeon_progress 
        WHERE user_id = %s AND dungeon_name = %s
    """
    results = execute_query(sql, (user_id, dungeon_name))
    
    if results:
        old_floor = results[0]['current_floor']
        total_floors = results[0]['total_floors']
        floor_cleared = results[0].get('floor_cleared', True)
        floor_event_type = results[0].get('floor_event_type') or 'beast'
        if floor_cleared is None:
            floor_cleared = True
    else:
        old_floor = 1
        total_floors = DEFAULT_TOTAL_FLOORS
        floor_cleared = True
        floor_event_type = 'beast'
    
    if not floor_cleared and floor_event_type in ('beast', 'boss'):
        return jsonify({"ok": False, "error": "请先击败本层幻兽才能使用迷踪符"}), 400
    
    # 规则：35层通关后必须重置
    if old_floor == total_floors and floor_cleared:
        return jsonify({"ok": False, "error": "已通关本副本，请先重置后再继续挑战"}), 400
    
    new_floor = old_floor + steps
    
    # 规则：不可以跳过最后一层
    if old_floor < total_floors and new_floor >= total_floors:
        new_floor = total_floors
    
    # 生成楼层事件类型
    floor_event_type = generate_floor_event_type(new_floor)
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            upsert_sql = """
                INSERT INTO player_dungeon_progress (user_id, dungeon_name, current_floor, total_floors, floor_cleared, floor_event_type, loot_claimed)
                VALUES (%s, %s, %s, %s, FALSE, %s, TRUE)
                ON DUPLICATE KEY UPDATE 
                    current_floor = VALUES(current_floor), 
                    floor_cleared = FALSE, 
                    floor_event_type = VALUES(floor_event_type), 
                    loot_claimed = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(upsert_sql, (user_id, dungeon_name, new_floor, total_floors, floor_event_type))
            conn.commit()
    finally:
        conn.close()
    
    services.inventory_service.remove_item(user_id, MIZONG_ITEM_ID, 1)
    remaining_count = services.inventory_service.get_item_count(user_id, MIZONG_ITEM_ID)
    
    return jsonify({
        "ok": True,
        "old_floor": old_floor,
        "new_floor": new_floor,
        "steps": steps,
        "total_floors": total_floors,
        "remaining_count": remaining_count,
        "floor_event_type": floor_event_type
    })


@dungeon_bp.route('/floor/beasts', methods=['GET'])
def get_floor_beasts():
    user_id = get_current_user_id()
    dungeon_name = request.args.get('dungeon_name', '')
    floor = int(request.args.get('floor', 1))
    
    if not dungeon_name:
        return jsonify({"ok": False, "error": "请提供副本名称"}), 400
    
    # 从数据库获取当前层的事件类型
    floor_event_type = 'beast'
    if user_id:
        sql = "SELECT floor_event_type FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s"
        results = execute_query(sql, (user_id, dungeon_name))
        if results and results[0].get('floor_event_type'):
            floor_event_type = results[0]['floor_event_type']
    
    # 随机事件
    if floor_event_type == 'climb':
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "climb",
            "floor_event_type": "climb",
            "beasts": [],
            "description": "[声望之塔]消耗骰子攀登高塔，有机率获取召唤师声望"
        })
    
    if floor_event_type == 'vitality_spring':
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "vitality_spring",
            "floor_event_type": "vitality_spring",
            "beasts": [],
            "description": "[活力之泉]消耗骰子浸泡泉水，有机率补满活力"
        })
    
    if floor_event_type == 'rps':
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "rps",
            "floor_event_type": "rps",
            "beasts": [],
            "description": "[猜拳]与副本内的神秘人猜拳，赢了前进，输了后退"
        })

    # 宝箱事件
    if floor_event_type == 'giant_chest':
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "giant_chest",
            "floor_event_type": "giant_chest",
            "beasts": [],
            "description": "巨型宝箱 - 可能获得稀有道具"
        })
    
    if floor_event_type == 'mystery_chest':
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "mystery_chest",
            "floor_event_type": "mystery_chest",
            "beasts": [],
            "description": "神秘宝箱 - 内容未知"
        })
    
    if floor in BOSS_FLOORS:
        dungeon_data = get_dungeon_by_name(dungeon_name)
        if dungeon_data and 'beasts' in dungeon_data and 'boss' in dungeon_data['beasts']:
            boss = dungeon_data['beasts']['boss']
            return jsonify({
                "ok": True,
                "floor": floor,
                "floor_type": "boss",
                "floor_event_type": "boss",
                "beasts": [{
                    "id": boss['id'],
                    "name": boss['name'],
                    "level": boss['level'],
                    "count": boss.get('count', 1),
                    "stats": boss.get('stats', {}),
                    "attack_type": boss.get('attack_type', 'physical'),
                    "skills": boss.get('skills', [])
                }],
                "description": f"BOSS层 - 打败它即可通关"
            })
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "boss",
            "floor_event_type": "boss",
            "beasts": [],
            "description": "BOSS层"
        })
    
    dungeon_data = get_dungeon_by_name(dungeon_name)
    if not dungeon_data:
        return jsonify({"ok": False, "error": f"未找到副本: {dungeon_name}"}), 404
    
    beasts = dungeon_data.get('beasts', {})
    normal_beasts = beasts.get('normal', [])
    elite_beasts = beasts.get('elite', [])
    
    all_beasts = normal_beasts + elite_beasts
    
    if not all_beasts:
        return jsonify({
            "ok": True,
            "floor": floor,
            "floor_type": "normal",
            "beasts": [],
            "description": "本层没有幻兽"
        })
    
    chosen_beast = random.choice(all_beasts)
    
    beast_count = chosen_beast.get('count', 1)
    beasts_list = []
    for _ in range(beast_count):
        beasts_list.append({
            "id": chosen_beast['id'],
            "name": chosen_beast['name'],
            "level": chosen_beast['level'],
            "stats": chosen_beast.get('stats', {}),
            "attack_type": chosen_beast.get('attack_type', 'physical'),
            "skills": chosen_beast.get('skills', [])
        })
    
    is_elite = chosen_beast in elite_beasts
    floor_type = "elite" if is_elite else "normal"
    description = f"{dungeon_name}的{'精英' if is_elite else '常见'}幻兽"
    
    return jsonify({
        "ok": True,
        "floor": floor,
        "floor_type": floor_type,
        "floor_event_type": "beast",
        "beasts": beasts_list,
        "description": description
    })


@dungeon_bp.route('/challenge', methods=['POST'])
def challenge_beasts():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    moving_err = _ensure_not_moving(user_id)
    if moving_err:
        return moving_err
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '')
    floor = int(data.get('floor', 1))
    dungeon_beasts_data = data.get('beasts', [])
    
    if not dungeon_name:
        return jsonify({"ok": False, "error": "请提供副本名称"}), 400
    if not dungeon_beasts_data:
        return jsonify({"ok": False, "error": "没有幻兽可挑战"}), 400
    
    # 1. 获取玩家及其出战幻兽
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    raw_player_beasts = services.player_beast_repo.get_team_beasts(user_id)
    if not raw_player_beasts:
        return jsonify({"ok": False, "error": "你没有出战幻兽，请先在幻兽仓库设置出战"}), 400
    
    # 2. 转换为 PVP 引擎需要的格式
    attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(raw_player_beasts)
    defender_pvp_beasts = _to_pvp_beasts_from_config(dungeon_beasts_data)
    
    attacker_player = PvpPlayer(
        player_id=user_id,
        level=player.level,
        beasts=attacker_pvp_beasts,
        name=player.nickname
    )
    
    defender_player = PvpPlayer(
        player_id=0, # 副本 ID 为 0
        level=dungeon_beasts_data[0].get('level', 1),
        beasts=defender_pvp_beasts,
        name=dungeon_name
    )
    
    # 3. 执行战斗
    pvp_result = run_pvp_battle(attacker_player, defender_player)
    is_victory = (pvp_result.winner_player_id == user_id)
    
    # 4. 转换战报格式
    battles = _format_battle_result(pvp_result, player.nickname, dungeon_name)
    
    # 5. 计算评分和文案 (保留原有简单逻辑)
    enemy_level = dungeon_beasts_data[0].get('level', 1)
    if is_victory:
        rating = "S" if player.level >= enemy_level * 1.5 else ("A" if player.level >= enemy_level else "B")
        victory_text = "完美胜利(oooo:××××)" if rating == "S" else "胜利(ooo:×××)"
        
        # 6. 胜利后标记当前层已通关，并掉落战利品
        execute_update("""
            UPDATE player_dungeon_progress 
            SET floor_cleared = TRUE, loot_claimed = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND dungeon_name = %s
        """, (user_id, dungeon_name))
    else:
        rating = "C"
        victory_text = "失败"
    
    battle_data = {
        "is_victory": is_victory,
        "rating": rating,
        "victory_text": victory_text,
        "battles": battles,
        "player_name": player.nickname,
        "player_beast": raw_player_beasts[0].name if raw_player_beasts else "",
        "dungeon_name": dungeon_name,
        "floor": floor,
        "beasts": dungeon_beasts_data
    }
    
    return jsonify({
        "ok": True,
        "battle_data": battle_data,
        "loot": {
            "name": "战利品",
            "cost": 15,
            "double_card": 1,
            "experience": 100 if floor not in BOSS_FLOORS else 0,
            "copper": 600 if floor in BOSS_FLOORS else 0,
            "floor": floor,
            "has_loot": is_victory
        },
        "capturable_beast": dungeon_beasts_data[0]['name'] if (is_victory and floor not in BOSS_FLOORS) else None
    })


# 宝箱相关常量
DOUBLE_CARD_ITEM_ID = 6024
CRYSTAL_ITEM_IDS = [1001, 1002, 1003, 1004, 1005, 1006, 1007]  # 七类结晶
VITALITY_GRASS_ITEM_ID = 4001  # 活力草
CAPTURE_BALL_ITEM_ID = 4002  # 捕捉球
STRONG_CAPTURE_BALL_ITEM_ID = 4003  # 强力捕捉球
CHEST_ENERGY_COST = 15  # 开启宝箱消耗活力

# 副本捕捉成功率（百分比）
CAPTURE_BALL_SUCCESS_RATE = {
    CAPTURE_BALL_ITEM_ID: 25,
    STRONG_CAPTURE_BALL_ITEM_ID: 45,
}


def _normalize_beast_name(beast_name: str) -> str:
    """将副本显示用的幻兽名归一化为模板名（例如：去掉“精英·”前缀）"""
    name = (beast_name or "").strip()
    for prefix in ("精英·", "精英.", "精英 ", "精英"):
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
            break
    return name


def _resolve_template_id_by_name(beast_name: str):
    """通过幻兽名称找到模板ID，找不到返回 None"""
    target = _normalize_beast_name(beast_name)
    if not target:
        return None
    
    all_templates = services.beast_template_repo.get_all() or {}
    for tpl in all_templates.values():
        if getattr(tpl, "name", None) == target:
            return getattr(tpl, "id", None)
    return None


@dungeon_bp.route('/chest/open', methods=['POST'])
def open_chest():
    """开启宝箱"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '')
    chest_type = data.get('chest_type', '')  # giant_chest 或 mystery_chest
    cost_type = data.get('cost_type', 'energy')  # energy 或 double_card
    
    if not dungeon_name:
        return jsonify({"ok": False, "error": "请提供副本名称"}), 400
    
    if chest_type not in ('giant_chest', 'mystery_chest'):
        return jsonify({"ok": False, "error": "无效的宝箱类型"}), 400
    
    if cost_type not in ('energy', 'double_card'):
        return jsonify({"ok": False, "error": "无效的消耗类型"}), 400
    
    # 检查当前层是否是宝箱事件
    sql = "SELECT floor_event_type, current_floor FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s"
    results = execute_query(sql, (user_id, dungeon_name))
    
    if not results:
        return jsonify({"ok": False, "error": "未找到副本进度"}), 404
    
    current_event = results[0].get('floor_event_type')
    current_floor = results[0].get('current_floor', 1)
    
    if current_event != chest_type:
        return jsonify({"ok": False, "error": "当前层不是宝箱事件"}), 400
    
    # 检查并消耗资源
    is_double = False
    if cost_type == 'energy':
        # 检查活力
        player_rows = execute_query("SELECT energy FROM player WHERE user_id = %s", (user_id,))
        if not player_rows:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        current_energy = player_rows[0].get('energy', 0)
        if current_energy < CHEST_ENERGY_COST:
            return jsonify({"ok": False, "error": f"活力不足，需要{CHEST_ENERGY_COST}点活力"}), 400
        # 扣除活力
        execute_update("UPDATE player SET energy = energy - %s WHERE user_id = %s", (CHEST_ENERGY_COST, user_id))
    else:
        # 检查双倍卡
        double_card_count = services.inventory_service.get_item_count(user_id, DOUBLE_CARD_ITEM_ID)
        if double_card_count <= 0:
            return jsonify({"ok": False, "error": "双倍卡不足"}), 400
        # 扣除双倍卡
        services.inventory_service.remove_item(user_id, DOUBLE_CARD_ITEM_ID, 1)
        is_double = True
    
    # 生成宝箱奖励
    multiplier = 2 if is_double else 1
    rewards = []
    
    # 随机选择一个结晶
    crystal_id = random.choice(CRYSTAL_ITEM_IDS)
    crystal_names = {
        1001: "金之结晶", 1002: "木之结晶", 1003: "水之结晶",
        1004: "火之结晶", 1005: "土之结晶", 1006: "风之结晶", 1007: "电之结晶"
    }
    crystal_name = crystal_names.get(crystal_id, "结晶")
    
    if chest_type == 'giant_chest':
        # 巨型宝箱：500铜钱 + 1活力草 + 1随机结晶 + 1捕捉球
        copper_amount = 500 * multiplier
        grass_amount = 1 * multiplier
        crystal_amount = 1 * multiplier
        ball_amount = 1 * multiplier
        
        rewards.append({"type": "copper", "name": "铜钱", "amount": copper_amount, "item_id": None})
        rewards.append({"type": "item", "name": "活力草", "amount": grass_amount, "item_id": VITALITY_GRASS_ITEM_ID})
        rewards.append({"type": "item", "name": crystal_name, "amount": crystal_amount, "item_id": crystal_id})
        rewards.append({"type": "item", "name": "捕捉球", "amount": ball_amount, "item_id": CAPTURE_BALL_ITEM_ID})
        
        # 发放奖励
        execute_update("UPDATE player SET gold = gold + %s WHERE user_id = %s", (copper_amount, user_id))
        services.inventory_service.add_item(user_id, VITALITY_GRASS_ITEM_ID, grass_amount)
        services.inventory_service.add_item(user_id, crystal_id, crystal_amount)
        services.inventory_service.add_item(user_id, CAPTURE_BALL_ITEM_ID, ball_amount)
    else:
        # 神秘宝箱：300铜钱 + 1随机结晶
        copper_amount = 300 * multiplier
        crystal_amount = 1 * multiplier
        
        rewards.append({"type": "copper", "name": "铜钱", "amount": copper_amount, "item_id": None})
        rewards.append({"type": "item", "name": crystal_name, "amount": crystal_amount, "item_id": crystal_id})
        
        # 发放奖励
        execute_update("UPDATE player SET gold = gold + %s WHERE user_id = %s", (copper_amount, user_id))
        services.inventory_service.add_item(user_id, crystal_id, crystal_amount)
    
    # 标记当前层已通关
    execute_update("""
        UPDATE player_dungeon_progress 
        SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (user_id, dungeon_name))
    
    return jsonify({
        "ok": True,
        "chest_type": chest_type,
        "floor": current_floor,
        "rewards": rewards,
        "is_double": is_double,
        "message": "开启宝箱成功！" + ("（双倍奖励）" if is_double else "")
    })


@dungeon_bp.route('/capture/info', methods=['GET'])
def get_capture_info():
    """获取副本捕捉页面所需信息（捕捉球数量等）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    counts = {
        str(CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, CAPTURE_BALL_ITEM_ID),
        str(STRONG_CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, STRONG_CAPTURE_BALL_ITEM_ID),
    }
    return jsonify({"ok": True, "counts": counts})


@dungeon_bp.route('/capture', methods=['POST'])
def capture_beast():
    """副本捕捉：消耗捕捉球并按概率获得当前副本幻兽"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = (data.get('dungeon_name') or '').strip()
    beast_name = (data.get('beast_name') or '').strip()
    floor = int(data.get('floor', 0) or 0)
    # 强制设为 1 级（副本捕捉规则）
    level = 1
    ball_item_id = int(data.get('ball_item_id', 0) or 0)
    
    if not dungeon_name:
        return jsonify({"ok": False, "error": "请提供副本名称"}), 400
    if not beast_name:
        return jsonify({"ok": False, "error": "请提供要捕捉的幻兽名称"}), 400
    if floor <= 0:
        return jsonify({"ok": False, "error": "floor 无效"}), 400
    
    success_rate = CAPTURE_BALL_SUCCESS_RATE.get(ball_item_id)
    if success_rate is None:
        return jsonify({"ok": False, "error": "无效的捕捉球类型"}), 400
    
    # 校验副本进度：必须仍处于该层，且该层已通关（代表刚战胜幻兽/事件已完成）
    prog = execute_query(
        "SELECT current_floor, floor_cleared, floor_event_type FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (user_id, dungeon_name),
    )
    if not prog:
        return jsonify({"ok": False, "error": "未找到副本进度"}), 404
    
    current_floor = int(prog[0].get("current_floor", 0) or 0)
    floor_cleared = bool(prog[0].get("floor_cleared", False))
    floor_event_type = prog[0].get("floor_event_type") or "beast"
    
    if current_floor != floor:
        return jsonify({"ok": False, "error": "当前层已变化，无法捕捉"}), 400
    if not floor_cleared:
        return jsonify({"ok": False, "error": "请先击败本层幻兽再尝试捕捉"}), 400
    if current_floor in BOSS_FLOORS or floor_event_type == "boss":
        return jsonify({"ok": False, "error": "BOSS不可捕捉"}), 400
    if floor_event_type in ("giant_chest", "mystery_chest"):
        return jsonify({"ok": False, "error": "当前层为宝箱事件，无法捕捉"}), 400
    
    # 解析模板ID（副本配置的 id 是字符串，因此按名称匹配模板）
    template_id = _resolve_template_id_by_name(beast_name)
    if not template_id:
        return jsonify({"ok": False, "error": f"该幻兽暂不支持捕捉：{beast_name}"}), 400
    
    # 检查捕捉球数量
    ball_count = services.inventory_service.get_item_count(user_id, ball_item_id)
    if ball_count <= 0:
        return jsonify({"ok": False, "error": "捕捉球不足"}), 400
    
    # 先检查幻兽栏容量（避免先扣球后失败）
    beast_count = services.player_beast_repo.count_by_user(user_id)
    # 获取VIP幻兽栏上限
    from application.services.vip_service import get_beast_slot_limit
    player = services.player_repo.get_by_id(user_id)
    vip_level = getattr(player, 'vip_level', 0) or 0
    max_beast_slots = get_beast_slot_limit(vip_level)
    if beast_count >= max_beast_slots:
        return jsonify({"ok": False, "error": f"幻兽栏已满（{beast_count}/{max_beast_slots}），请先整理"}), 400
    
    # 扣除捕捉球
    try:
        services.inventory_service.remove_item(user_id, ball_item_id, 1)
    except InventoryError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "error": "扣除捕捉球失败"}), 500
    
    roll = random.randint(1, 100)
    success = roll <= int(success_rate)
    
    if not success:
        counts = {
            str(CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, CAPTURE_BALL_ITEM_ID),
            str(STRONG_CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, STRONG_CAPTURE_BALL_ITEM_ID),
        }
        return jsonify({
            "ok": True,
            "success": False,
            "success_rate": int(success_rate),
            "roll": roll,
            "message": f"捕捉失败（成功率{success_rate}%，掷出{roll}）",
            "counts": counts,
        })
    
    # 捕捉成功：获得对应的“召唤球”道具，存入背包
    # 召唤球 ID 规则：20000 + template_id
    ball_id = 20000 + template_id
    item_tpl = services.item_repo.get_by_id(ball_id)
    
    if not item_tpl:
        # 如果配置中确实漏掉了该召唤球，返回一个友好的错误而不是抛出异常导致 500
        # 理论上更新了 items.json 后不应进入此分支
        return jsonify({
            "ok": False, 
            "error": f"捕捉成功但系统配置缺失该幻兽的召唤球(ID:{ball_id})，请联系管理员"
        }), 400

    ball_name = item_tpl.name
    
    try:
        services.inventory_service.add_item(user_id, ball_id, 1)
    except Exception as e:
        # 如果增加道具失败（例如背包和临时背包都满了，虽然目前逻辑支持临时背包），返还捕捉球
        try:
            services.inventory_service.add_item(user_id, ball_item_id, 1)
        except:
            pass
        return jsonify({"ok": False, "error": f"获得召唤球失败：{str(e)}"}), 500
    
    counts = {
        str(CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, CAPTURE_BALL_ITEM_ID),
        str(STRONG_CAPTURE_BALL_ITEM_ID): services.inventory_service.get_item_count(user_id, STRONG_CAPTURE_BALL_ITEM_ID),
    }
    return jsonify({
        "ok": True,
        "success": True,
        "success_rate": int(success_rate),
        "roll": roll,
        "message": f"捕捉成功！获得了【{ball_name}】，已存入背包",
        "counts": counts,
    })


@dungeon_bp.route('/event/climb', methods=['POST'])
def event_climb():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '')
    
    player = services.player_repo.get_by_id(user_id)
    if not player or player.dice <= 0:
        return jsonify({"ok": False, "error": "骰子不足"}), 400
    
    # 消耗 1 骰子
    player.dice -= 1
    
    # 33.3% 成功
    roll = random.random()
    success = roll < 0.333
    
    prestige_gain = 0
    if success:
        if player.level < 30: prestige_gain = 100
        elif player.level < 40: prestige_gain = 150
        elif player.level < 50: prestige_gain = 200
        elif player.level < 60: prestige_gain = 400
        elif player.level < 70: prestige_gain = 800
        else: prestige_gain = 1200
        
        player.prestige += prestige_gain
    
    services.player_repo.save(player)
    
    # 无论成功失败，都标记本层已通关，允许玩家继续前进
    execute_update("""
        UPDATE player_dungeon_progress 
        SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (user_id, dungeon_name))
    
    return jsonify({
        "ok": True,
        "success": success,
        "prestige_gain": prestige_gain,
        "dice": player.dice,
        "message": f"攀登{'成功' if success else '失败'}" + (f"，获得{prestige_gain}声望" if success else "")
    })


@dungeon_bp.route('/event/vitality-spring', methods=['POST'])
def event_vitality_spring():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '')
    
    player = services.player_repo.get_by_id(user_id)
    if not player or player.dice <= 0:
        return jsonify({"ok": False, "error": "骰子不足"}), 400
    
    # 消耗 1 骰子
    player.dice -= 1
    
    # 25% 成功
    roll = random.random()
    success = roll < 0.25
    
    if success:
        player.energy = player.max_energy # 恢复满活力
    
    services.player_repo.save(player)
    
    # 无论成功失败，都标记本层已通关，允许玩家继续前进
    execute_update("""
        UPDATE player_dungeon_progress 
        SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (user_id, dungeon_name))
    
    return jsonify({
        "ok": True,
        "success": success,
        "dice": player.dice,
        "energy": player.energy,
        "message": f"浸泡{'成功' if success else '失败'}" + ("，活力已补满" if success else "")
    })


@dungeon_bp.route('/event/rps', methods=['POST'])
def event_rps():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '')
    player_choice = data.get('choice') # stone, scissors, paper
    
    if player_choice not in ['stone', 'scissors', 'paper']:
        return jsonify({"ok": False, "error": "无效的选择"}), 400
        
    choices = ['stone', 'scissors', 'paper']
    bot_choice = random.choice(choices)
    
    # 胜负判定
    if player_choice == bot_choice:
        result = 'draw'
    elif (player_choice == 'stone' and bot_choice == 'scissors') or \
         (player_choice == 'scissors' and bot_choice == 'paper') or \
         (player_choice == 'paper' and bot_choice == 'stone'):
        result = 'win'
    else:
        result = 'lose'
        
    # 处理进度变化
    sql = "SELECT current_floor, total_floors FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s"
    results = execute_query(sql, (user_id, dungeon_name))
    
    if not results:
        return jsonify({"ok": False, "error": "未找到进度"}), 404
        
    old_floor = results[0]['current_floor']
    total_floors = results[0]['total_floors']
    
    change = random.randint(1, 6)
    new_floor = old_floor
    
    if result == 'win':
        new_floor = min(total_floors, old_floor + change)
    elif result == 'lose':
        new_floor = max(1, old_floor - change)
        
    # 生成新楼层事件类型
    floor_event_type = generate_floor_event_type(new_floor)
    
    execute_update("""
        UPDATE player_dungeon_progress 
        SET current_floor = %s, floor_cleared = FALSE, floor_event_type = %s, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (new_floor, floor_event_type, user_id, dungeon_name))
    
    choice_map = {'stone': '石头', 'scissors': '剪刀', 'paper': '布'}
    
    return jsonify({
        "ok": True,
        "result": result,
        "player_choice": choice_map[player_choice],
        "bot_choice": choice_map[bot_choice],
        "change": change if result != 'draw' else 0,
        "new_floor": new_floor,
        "message": f"猜拳{ '平局' if result == 'draw' else ('获胜' if result == 'win' else '失败') }"
    })


@dungeon_bp.route('/loot/open', methods=['POST'])
def open_loot():
    """开启战利品"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    dungeon_name = data.get('dungeon_name', '镇妖塔')
    cost_type = data.get('cost_type', 'energy')  # energy 或 double_card
    
    # 1. 检查进度和战利品状态
    sql = """
        SELECT current_floor, floor_cleared, loot_claimed 
        FROM player_dungeon_progress 
        WHERE user_id = %s AND dungeon_name = %s
    """
    results = execute_query(sql, (user_id, dungeon_name))
    
    if not results:
        return jsonify({"ok": False, "error": "未找到副本进度"}), 404
    
    row = results[0]
    if not row['floor_cleared']:
        return jsonify({"ok": False, "error": "请先战胜本层幻兽"}), 400
    if row['loot_claimed']:
        return jsonify({"ok": False, "error": "战利品已领取"}), 400
        
    # 2. 检查并消耗资源
    is_double = (cost_type == 'double_card')
    if cost_type == 'energy':
        player = services.player_repo.get_by_id(user_id)
        if player.energy < 15:
            return jsonify({"ok": False, "error": "活力不足，开启战利品需要15点活力"}), 400
        player.energy -= 15
        services.player_repo.save(player)
    elif cost_type == 'double_card':
        count = services.inventory_service.get_item_count(user_id, DOUBLE_CARD_ITEM_ID)
        if count <= 0:
            return jsonify({"ok": False, "error": "双倍卡不足"}), 400
        services.inventory_service.remove_item(user_id, DOUBLE_CARD_ITEM_ID, 1)
    else:
        return jsonify({"ok": False, "error": "无效的消耗类型"}), 400
        
    # 3. 发放奖励
    multiplier = 2 if is_double else 1
    current_floor = row['current_floor']
    is_boss = (current_floor in BOSS_FLOORS)
    
    rewards = {}
    
    # 奖励1：结晶 (BOSS和普通怪都有)
    crystal_id = random.choice(CRYSTAL_ITEM_IDS)
    crystal_names = {
        1001: "金之结晶", 1002: "木之结晶", 1003: "水之结晶",
        1004: "火之结晶", 1005: "土之结晶", 1006: "风之结晶", 1007: "电之结晶"
    }
    crystal_name = crystal_names.get(crystal_id, "结晶")
    crystal_amount = 1 * multiplier
    services.inventory_service.add_item(user_id, crystal_id, crystal_amount)
    rewards["crystal"] = {"id": crystal_id, "name": crystal_name, "amount": crystal_amount}

    if is_boss:
        # BOSS 奖励：铜钱 600 + 30% 骨魂
        copper_amount = 600 * multiplier
        execute_update("UPDATE player SET gold = gold + %s WHERE user_id = %s", (copper_amount, user_id))
        rewards["copper"] = {"amount": copper_amount}
        
        # 30% 概率出骨魂
        if random.random() < 0.3:
            bone_soul_id = get_bone_soul_item_id(dungeon_name)
            if bone_soul_id:
                bone_soul_amount = 1 * multiplier
                services.inventory_service.add_item(user_id, bone_soul_id, bone_soul_amount)
                
                # 获取骨魂名称
                bone_soul_names = {
                    2001: "碎空骨魂", 2002: "猎魔骨魂", 2003: "龙炎骨魂",
                    2004: "奔雷骨魂", 2005: "凌霄骨魂", 2006: "麒麟骨魂",
                    2007: "武神骨魂", 2008: "弑天骨魂", 2009: "毁灭骨魂"
                }
                rewards["bone_soul"] = {
                    "id": bone_soul_id,
                    "name": bone_soul_names.get(bone_soul_id, "骨魂"),
                    "amount": bone_soul_amount
                }
    else:
        # 普通怪奖励：幻兽经验
        exp_per_beast = 100 * multiplier
        team_beasts = services.player_beast_repo.get_team_beasts(user_id)
        player = services.player_repo.get_by_id(user_id)
        
        beast_rewards = []
        for beast in team_beasts:
            # 等级限制：不可超过玩家等级 5 级以上
            max_level = player.level + 5
            if beast.level < max_level:
                old_level = beast.level
                beast.add_exp(exp_per_beast, max_level=max_level)
                    
                services.player_beast_repo.save(beast)
                beast_rewards.append({
                    "id": beast.id,
                    "name": beast.name,
                    "old_level": old_level,
                    "new_level": beast.level,
                    "exp_gained": exp_per_beast
                })
            else:
                beast_rewards.append({
                    "id": beast.id,
                    "name": beast.name,
                    "old_level": beast.level,
                    "new_level": beast.level,
                    "exp_gained": 0,
                    "capped": True
                })
        rewards["beast_exp"] = beast_rewards
            
    # 4. 更新领取状态
    execute_update("""
        UPDATE player_dungeon_progress 
        SET loot_claimed = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (user_id, dungeon_name))
    
    return jsonify({
        "ok": True,
        "is_double": is_double,
        "is_boss": is_boss,
        "rewards": rewards,
        "message": "领取战利品成功！"
    })
