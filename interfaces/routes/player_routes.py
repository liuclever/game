# interfaces/routes/player_routes.py
"""玩家相关路由：个人信息、晋级、修行等"""

from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.cultivation_service import CultivationService
from application.services.signin_service import SigninError
from domain.services.pvp_battle_engine import PvpBeast, PvpPlayer, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills
from infrastructure.db.connection import execute_update, execute_query
import json
from pathlib import Path
from datetime import date

player_bp = Blueprint('player', __name__, url_prefix='/api')

# 修行系统已被整合入 services.cultivation_service


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@player_bp.get("/player/info")
def get_player_info():
    """获取玩家基础信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    player = services.player_repo.get_by_id(user_id=user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 活力恢复处理
    if player.recover_energy():
        services.player_repo.save(player)

    return jsonify({
        "ok": True,
        "player": {
            "user_id": player.user_id,
            "nickname": player.nickname,
            "level": player.level,
            "rank_name": player.get_rank_name(),
            "exp": player.exp,
            "next_exp": player.exp_to_next_level(),
            "gold": player.gold,
            "copper": player.copper,
            "yuanbao": player.yuanbao,
            "silver_diamond": player.silver_diamond,
            "energy": player.energy,
            "max_energy": player.max_energy,
            "vip_level": player.vip_level
        }
    })


@player_bp.get("/player/profile")
def get_player_profile():
    """获取其他玩家的个人信息页"""
    target_id = request.args.get("id", type=int)
    if not target_id:
        return jsonify({"ok": False, "error": "缺少玩家ID"}), 400
    
    player = services.player_repo.get_by_id(user_id=target_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 即使是查看他人信息，如果该玩家长时间没上线，也帮他计算下活力（可选，但为了数据一致性建议做）
    if player.recover_energy():
        services.player_repo.save(player)
    
    # 获取玩家幻兽（战斗队）
    beasts = services.player_beast_repo.get_team_beasts(target_id)
    beasts_data = [
        {
            "id": b.id,
            "name": b.name,
            "realm": b.realm,
            "level": b.level,
            "combat_power": b.combat_power,
        }
        for b in beasts
    ]

    # 让他人资料页的战宠数据也与幻兽系统一致：重算属性与战力（含装备）
    try:
        from interfaces.routes.beast_routes import _calc_beast_stats, _calc_total_combat_power_with_equipment

        beasts_data = []
        for b in beasts:
            b = _calc_beast_stats(b)
            services.player_beast_repo.update_beast(b)
            total_power = _calc_total_combat_power_with_equipment(b)
            beasts_data.append({
                "id": b.id,
                "name": b.name,
                "realm": b.realm,
                "level": b.level,
                "combat_power": total_power,
            })
    except Exception:
        pass
    
    # 获取玩家动态
    from infrastructure.db.zhenyao_battle_repo_mysql import MySQLZhenyaoBattleRepo
    battle_repo = MySQLZhenyaoBattleRepo()
    logs = battle_repo.get_user_battles(target_id, limit=10)
    dynamics = []
    for log in logs:
        time_str = log.created_at.strftime("%m-%d %H:%M") if log.created_at else ""
        if log.is_success:
            text = f"聚魂阵无人镇守，抢夺{log.floor}层聚魂阵成功！"
        else:
            text = f"挑战{log.defender_name}的第{log.floor}层失败！"
        dynamics.append({"time": time_str, "text": text})

    # 联盟信息：返回真实联盟名/等级（未加入则为空）
    alliance_name = None
    alliance_level = None
    try:
        member = services.alliance_repo.get_member(target_id)
        if member:
            alliance = services.alliance_repo.get_alliance_by_id(member.alliance_id)
            if alliance:
                alliance_name = alliance.name
                alliance_level = alliance.level
    except Exception:
        pass
    
    return jsonify({
        "ok": True,
        "player": {
            "user_id": player.user_id,
            "nickname": player.nickname,
            "level": player.level,
            "rank_name": player.get_rank_name(),
            "exp": player.exp,
            "next_exp": player.exp_to_next_level(),
            "gold": player.gold,
            "gender": "男",
            "charm_level": 1,
            "charm": player.charm,
            "prestige": player.prestige,
            "energy": player.energy,
            "max_energy": player.max_energy,
            "crystal_tower": player.crystal_tower,
            "spirit_stone": player.crystal_tower,
            "vip_level": player.vip_level,
            "wins": 0,
            "battles": 0,
            "arena_rank": 1,
            "arena_position": 1,
            "status": player.location,
            "status_detail": "修行中",
            "mount": "破天飞剑",
            "alliance": alliance_name,
            "alliance_title": None,
            "alliance_level": alliance_level,
            "title": "飞龙之王",
        },
        "beasts": beasts_data,
        "dynamics": dynamics,
    })


@player_bp.post("/player/signin")
def player_signin():
    """玩家签到（当日仅一次）。

    返回：
    - ok: bool
    - issuer_name: str（颁发者：盟战榜前三联盟随机一个）
    - reward: {base_copper, copper, multiplier}
    - signin_streak: int
    - last_signin_date: YYYY-MM-DD
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        result = services.signin_service.do_signin(player_id=user_id)
    except SigninError:
        return jsonify({"ok": False, "error": "今日已签到"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    return jsonify({"ok": True, **(result or {})})



@player_bp.post("/player/levelup")
def player_levelup():
    """晋级"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        result = services.cultivation_service.levelup(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ===== 修行系统 =====
def _deprecated_cultivation_api():
    return jsonify({
        "ok": False,
        "error": "该接口已下线，请使用 /api/cultivation/* (cultivation_routes.py)",
    }), 410


@player_bp.get("/_deprecated/cultivation/status")
def get_cultivation_status():
    """获取修行状态"""
    return _deprecated_cultivation_api()


@player_bp.get("/_deprecated/cultivation/options")
def get_cultivation_options():
    """获取修行地图选项"""
    return _deprecated_cultivation_api()


@player_bp.post("/_deprecated/cultivation/start")
def start_cultivation():
    """开始修行"""
    return _deprecated_cultivation_api()


@player_bp.post("/_deprecated/cultivation/harvest")
def harvest_cultivation():
    """领取修行奖励（结束修行）"""
    return _deprecated_cultivation_api()


@player_bp.post("/_deprecated/cultivation/stop")
def stop_cultivation():
    """终止修行（同结束修行）"""
    return _deprecated_cultivation_api()


# ===== 切磋系统 =====
def _build_spar_battle_data(pvp_result, attacker_player: PvpPlayer, defender_player: PvpPlayer,
                           attacker_beasts=None, defender_beasts=None) -> dict:
    """根据 PvpBattleResult 构建切磋战报数据结构"""
    attacker_name = attacker_player.name or str(attacker_player.player_id)
    defender_name = defender_player.name or str(defender_player.player_id)

    def get_player_name(pid: int) -> str:
        return attacker_name if pid == attacker_player.player_id else defender_name

    def get_side_flag(pid: int) -> str:
        return "attacker" if pid == attacker_player.player_id else "defender"

    def build_battle_segment(battle_index: int, seg_logs):
        if not seg_logs:
            return {
                "battle_num": battle_index,
                "attacker_beast": "",
                "defender_beast": "",
                "winner": "defender",
                "rounds": [],
                "result": "",
            }

        rounds = []
        for idx, log in enumerate(seg_logs, start=1):
            rounds.append({
                "round": idx,
                "action": log.description,
                "a_hp": log.attacker_hp_after,
                "d_hp": log.defender_hp_after,
            })

        beast_state = {}
        for log in seg_logs:
            if log.attacker_beast_id != 0:
                beast_state[(log.attacker_player_id, log.attacker_beast_id)] = (
                    log.attacker_name,
                    log.attacker_hp_after,
                )
            if log.defender_beast_id != 0:
                beast_state[(log.defender_player_id, log.defender_beast_id)] = (
                    log.defender_name,
                    log.defender_hp_after,
                )

        winner_player_id = pvp_result.winner_player_id
        winner_beast_name = ""
        loser_beast_name = ""
        winner_hp = 0

        keys = list(beast_state.keys())
        if keys:
            if len(keys) == 1:
                keys = keys * 2
            (p1, b1), (p2, b2) = keys[0], keys[1]
            name1, hp1 = beast_state[(p1, b1)]
            name2, hp2 = beast_state[(p2, b2)]

            if hp1 > 0 and hp2 <= 0:
                winner_player_id = p1
                winner_beast_name, winner_hp = name1, hp1
                loser_beast_name = name2
            elif hp2 > 0 and hp1 <= 0:
                winner_player_id = p2
                winner_beast_name, winner_hp = name2, hp2
                loser_beast_name = name1
            elif hp1 != hp2:
                if hp1 > hp2:
                    winner_player_id = p1
                    winner_beast_name, winner_hp = name1, hp1
                    loser_beast_name = name2
                else:
                    winner_player_id = p2
                    winner_beast_name, winner_hp = name2, hp2
                    loser_beast_name = name1

        winner_player_name = get_player_name(winner_player_id)
        winner_flag = get_side_flag(winner_player_id)

        if winner_beast_name and loser_beast_name:
            result_text = f"『{winner_player_name}』的{winner_beast_name}获胜，剩余气血{winner_hp}"
        else:
            result_text = f"『{winner_player_name}』获胜"

        return {
            "battle_num": battle_index,
            "attacker_beast": "",
            "defender_beast": "",
            "winner": winner_flag,
            "rounds": rounds,
            "result": result_text,
        }

    battles = []
    current_pair = None
    current_logs = []

    for log in pvp_result.logs:
        if log.attacker_beast_id == 0 and current_pair is not None:
            current_logs.append(log)
            continue

        pair = frozenset({log.attacker_beast_id, log.defender_beast_id})

        if current_pair is None:
            current_pair = pair
            current_logs.append(log)
        elif pair == current_pair:
            current_logs.append(log)
        else:
            battles.append(build_battle_segment(len(battles) + 1, current_logs))
            current_pair = pair
            current_logs = [log]

    if current_logs:
        battles.append(build_battle_segment(len(battles) + 1, current_logs))

    is_victory = pvp_result.winner_player_id == attacker_player.player_id
    
    # 计算战斗结果符号
    attacker_wins = sum(1 for b in battles if b.get('winner') == 'attacker')
    defender_wins = len(battles) - attacker_wins
    
    # 生成结果符号，例如 (⚬⚬⚬⚬:×××)
    result_symbol = f"({'⚬' * attacker_wins}:{'×' * defender_wins})"
    
    # 判断胜利类型
    if is_victory:
        if defender_wins == 0:
            result_text = f"完美胜利{result_symbol}"
        else:
            result_text = f"胜利{result_symbol}"
    else:
        result_text = f"失败{result_symbol}"
    
    # 构建幻兽信息（用于显示经验）
    attacker_beasts_info = []
    if attacker_beasts:
        realm_names = ['', '凡界', '人界', '地界', '天界', '神界']
        for beast in attacker_beasts:
            realm_str = str(beast.realm) if hasattr(beast, 'realm') and beast.realm else ''
            if realm_str.isdigit():
                realm_idx = int(realm_str)
                realm_name = realm_names[realm_idx] if realm_idx < len(realm_names) else '凡界'
            else:
                realm_name = realm_str or '凡界'
            
            attacker_beasts_info.append({
                "name": beast.name,
                "realm": realm_name,
                "exp_gain": 0,
                "template_id": beast.template_id if hasattr(beast, 'template_id') else None,
            })
    else:
        for beast in attacker_player.beasts:
            attacker_beasts_info.append({
                "name": beast.name, "realm": "凡界", "exp_gain": 0, "template_id": None,
            })
    
    defender_beasts_info = []
    if defender_beasts:
        realm_names = ['', '凡界', '人界', '地界', '天界', '神界']
        for beast in defender_beasts:
            realm_str = str(beast.realm) if hasattr(beast, 'realm') and beast.realm else ''
            if realm_str.isdigit():
                realm_idx = int(realm_str)
                realm_name = realm_names[realm_idx] if realm_idx < len(realm_names) else '凡界'
            else:
                realm_name = realm_str or '凡界'
            
            defender_beasts_info.append({
                "name": beast.name,
                "realm": realm_name,
                "template_id": beast.template_id if hasattr(beast, 'template_id') else None,
            })
    else:
        for beast in defender_player.beasts:
            defender_beasts_info.append({
                "name": beast.name, "realm": "凡界", "template_id": None,
            })
    
    # 生成战斗过程摘要
    for battle in battles:
        rounds = battle.get('rounds', [])
        if rounds:
            first_action = rounds[0].get('action', '')
            battle['summary'] = first_action
        else:
            battle['summary'] = '战斗结束'

    return {
        "is_victory": is_victory,
        "result": result_text,
        "attacker_id": attacker_player.player_id,
        "attacker_name": attacker_name,
        "defender_id": defender_player.player_id,
        "defender_name": defender_name,
        "total_turns": pvp_result.total_turns,
        "battles": battles,
        "attacker_beasts": attacker_beasts_info,
        "defender_beasts": defender_beasts_info,
        "incense_bonus": "无",
        "energy_cost": 15,
    }


def _get_vip_energy_max(vip_level: int) -> int:
    """根据VIP等级获取活力上限"""
    base_dir = Path(__file__).resolve().parents[2]
    config_path = base_dir / "configs" / "vip_privileges.json"
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for lv_data in data.get("vip_levels", []):
            if lv_data.get("level") == vip_level:
                return lv_data.get("privileges", {}).get("vitality_max", 100)
    except Exception:
        pass
    return 100


@player_bp.post("/player/infuse")
def infuse_crystal():
    """灌注：给目标玩家的水晶塔+5，自己魅力+10"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    target_id = data.get("target_id")
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标玩家ID"})

    target_id = int(target_id)
    if target_id == user_id:
        return jsonify({"ok": False, "error": "不能给自己灌注"})

    target = services.player_repo.get_by_id(target_id)
    if not target:
        return jsonify({"ok": False, "error": "目标玩家不存在"})

    # 目标玩家每天只能被灌注一次（不触发登录任务副作用，直接操作repo）
    try:
        today = date.today()
        target_activity = services.daily_activity_repo.get_by_user_id(target_id)
        if target_activity:
            target_activity.reset_if_new_day(today)
            if "infused_today" in (target_activity.completed_tasks or []):
                return jsonify({"ok": False, "error": "对方今日已被灌注过"})
        else:
            from domain.entities.daily_activity import DailyActivity
            target_activity = DailyActivity(user_id=target_id, last_updated_date=today)
    except Exception:
        target_activity = None

    # 每天同一目标只能灌注一次（按灌注者维度）
    try:
        activity = services.daily_activity_service.get_activity(user_id)
        progress_key = f"infuse_target:{target_id}"
        if progress_key in (activity.completed_tasks or []):
            return jsonify({"ok": False, "error": "今日已灌注过该玩家"})
    except Exception:
        pass

    execute_update("UPDATE player SET crystal_tower = crystal_tower + 5 WHERE user_id = %s", (target_id,))
    execute_update("UPDATE player SET charm = charm + 10 WHERE user_id = %s", (user_id,))

    # 记录活跃度行为：每日灌注3人获得9点活跃度
    services.daily_activity_service.record_infuse(user_id, target_id)

    # 记录目标玩家已被灌注（当日一次）
    try:
        if target_activity is not None:
            if "infused_today" not in (target_activity.completed_tasks or []):
                target_activity.completed_tasks.append("infused_today")
            services.daily_activity_repo.save(target_activity)
    except Exception:
        pass

    rows = execute_query("SELECT charm FROM player WHERE user_id = %s", (user_id,))
    new_charm = rows[0]["charm"] if rows else 0

    return jsonify({
        "ok": True,
        "message": f"灌注成功！你的魅力值+10，对方水晶塔+5",
        "charm": new_charm,
    })


@player_bp.post("/player/claim-crystal")
def claim_crystal():
    """领取水晶塔活力：将水晶塔数值加到活力值，水晶塔归零"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"})

    if player.crystal_tower <= 0:
        return jsonify({"ok": False, "error": "水晶塔没有可领取的活力"})

    old_energy = player.energy
    # 强制增加能量并应用上限（由实体或逻辑控制）
    # 这里我们直接手动应用上限逻辑以确保准确性
    new_energy = min(player.energy + player.crystal_tower, player.max_energy)
    gained = new_energy - old_energy
    
    player.energy = new_energy
    player.crystal_tower = 0
    services.player_repo.save(player)

    return jsonify({
        "ok": True,
        "message": f"领取成功！活力+{gained}",
        "energy": player.energy,
        "crystal_tower": 0,
    })


@player_bp.post("/player/spar")
def spar_battle():
    """切磋：与其他玩家进行一场友谊赛"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    target_id = data.get("target_id")
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标玩家ID"})

    target_id = int(target_id)
    if target_id == user_id:
        return jsonify({"ok": False, "error": "不能与自己切磋"})

    attacker = services.player_repo.get_by_id(user_id)
    defender = services.player_repo.get_by_id(target_id)

    if not attacker:
        return jsonify({"ok": False, "error": "玩家不存在"})
    if not defender:
        return jsonify({"ok": False, "error": "对方玩家不存在"})

    attacker_beasts = services.player_beast_repo.get_team_beasts(user_id)
    defender_beasts = services.player_beast_repo.get_team_beasts(target_id)

    if not attacker_beasts:
        return jsonify({"ok": False, "error": "你没有出战幻兽"})
    if not defender_beasts:
        return jsonify({"ok": False, "error": "对方没有出战幻兽"})

    attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(attacker_beasts)
    defender_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(defender_beasts)

    attacker_player = PvpPlayer(
        player_id=user_id,
        level=attacker.level,
        beasts=attacker_pvp_beasts,
        name=attacker.nickname,
    )
    defender_player = PvpPlayer(
        player_id=target_id,
        level=defender.level,
        beasts=defender_pvp_beasts,
        name=defender.nickname,
    )

    pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
    
    # 保存切磋记录
    is_win = pvp_result.winner_player_id == user_id
    try:
        execute_update(
            "INSERT INTO spar_records (attacker_id, defender_id, is_victory) VALUES (%s, %s, %s)",
            (user_id, target_id, 1 if is_win else 0)
        )
        
        # 查询切磋战绩
        spar_stats = execute_query(
            "SELECT COUNT(*) as total, SUM(is_victory) as wins FROM spar_records WHERE attacker_id = %s OR defender_id = %s",
            (user_id, user_id)
        )
        if spar_stats:
            total = int(spar_stats[0].get('total', 0))
            wins = int(spar_stats[0].get('wins', 0) or 0)
            win_rate = (wins / total * 100) if total > 0 else 0
        else:
            total = 0
            wins = 0
            win_rate = 0
    except Exception as e:
        print(f"保存切磋记录失败: {e}")
        total = 0
        wins = 0
        win_rate = 0
    
    battle_data = _build_spar_battle_data(pvp_result, attacker_player, defender_player,
                                          attacker_beasts, defender_beasts)
    
    # 添加战绩统计
    battle_data['spar_wins'] = wins
    battle_data['spar_total'] = total
    battle_data['spar_win_rate'] = f"{win_rate:.2f}"

    return jsonify({
        "ok": True,
        "win": is_win,
        "message": f"切磋{'胜利' if is_win else '失败'}！",
        "battle": battle_data,
    })



@player_bp.get("/player/spar/recent")
def get_recent_spar_records():
    """获取最近的切磋记录"""
    limit = int(request.args.get('limit', 10))
    
    try:
        records = execute_query(
            """SELECT sr.id, sr.attacker_id, sr.defender_id, sr.is_victory, sr.created_at,
                      p1.nickname as player1_name, p1.level as player1_level,
                      p2.nickname as player2_name, p2.level as player2_level
               FROM spar_records sr
               LEFT JOIN player p1 ON sr.attacker_id = p1.user_id
               LEFT JOIN player p2 ON sr.defender_id = p2.user_id
               ORDER BY sr.created_at DESC
               LIMIT %s""",
            (limit,)
        )
        
        result = []
        for r in records:
            result.append({
                'id': r['id'],
                'player1_id': r['attacker_id'],
                'player1_name': r['player1_name'] or '未知',
                'player1_level': r['player1_level'] or 1,
                'player2_id': r['defender_id'],
                'player2_name': r['player2_name'] or '未知',
                'player2_level': r['player2_level'] or 1,
                'is_victory': bool(r['is_victory']),
                'created_at': r['created_at'].strftime('%Y-%m-%d %H:%M:%S') if r['created_at'] else ''
            })
        
        return jsonify({"ok": True, "records": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
