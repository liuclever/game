# interfaces/routes/arena_routes.py
"""擂台系统路由"""

from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update
from interfaces.web_api.bootstrap import services
from infrastructure.db.arena_battle_repo_mysql import MySQLArenaBattleRepo
from domain.services.pvp_battle_engine import PvpBeast, PvpPlayer, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills

arena_bp = Blueprint('arena', __name__, url_prefix='/api/arena')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


# 等级阶段配置
LEVEL_RANKS = [
    (1, 19, '见习', False),
    (20, 29, '黄阶', True),
    (30, 39, '玄阶', True),
    (40, 49, '地阶', True),
    (50, 59, '天阶', True),
    (60, 69, '飞马', True),
    (70, 79, '天龙', True),
    (80, 100, '战神', True),
]

ARENA_BALL_NORMAL = 4002
ARENA_BALL_GOLD = 4003
ARENA_MAX_WINS = 10

# 全局擂台战报仓库实例（当前模块内复用）
ARENA_BATTLE_REPO = MySQLArenaBattleRepo()


def get_vip_arena_limits(vip_level: int) -> tuple:
    """根据VIP等级获取擂台次数限制"""
    import json
    import os
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'vip_privileges.json'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for lv in data.get('vip_levels', []):
            if lv.get('level') == vip_level:
                priv = lv.get('privileges', {})
                return priv.get('arena_normal_limit', 5), priv.get('arena_gold_limit', 10)
    except:
        pass
    return 5, 10  # 默认VIP0的限制


def get_player_rank(level):
    """根据等级获取阶段名称和是否能参与擂台"""
    for min_lv, max_lv, rank_name, can_arena in LEVEL_RANKS:
        if min_lv <= level <= max_lv:
            return rank_name, can_arena
    return '见习', False


def get_arena_ball_id(arena_type):
    return ARENA_BALL_GOLD if arena_type == 'gold' else ARENA_BALL_NORMAL


def get_arena_ball_name(arena_type):
    return '强力捕捉球' if arena_type == 'gold' else '捕捉球'


def get_today_challenge_count(user_id: int) -> int:
    """获取玩家今日已挑战次数"""
    rows = execute_query(
        """SELECT challenge_count FROM arena_daily_challenge 
           WHERE user_id = %s AND challenge_date = CURDATE()""",
        (user_id,)
    )
    return rows[0]['challenge_count'] if rows else 0


def increment_challenge_count(user_id: int):
    """增加玩家今日挑战次数"""
    execute_update(
        """INSERT INTO arena_daily_challenge (user_id, challenge_date, challenge_count)
           VALUES (%s, CURDATE(), 1)
           ON DUPLICATE KEY UPDATE challenge_count = challenge_count + 1""",
        (user_id,)
    )


@arena_bp.get("/info")
def get_arena_info():
    """获取擂台信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    arena_type = request.args.get('type', 'normal')
    
    # 使用player_repo获取玩家信息（与auth/status保持一致）
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = player.level
    player_nickname = player.nickname
    rank_name, can_arena = get_player_rank(player_level)
    
    # 调试日志
    print(f"[DEBUG] 玩家 {player_nickname}(ID:{user_id}) 查询擂台: 阶段={rank_name}, 类型={arena_type}")
    
    if not can_arena:
        return jsonify({
            "ok": True,
            "canArena": False,
            "message": "20级以上才能参与擂台",
            "playerLevel": player_level,
            "rankName": rank_name,
        })
    
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    arena_info = arena_rows[0] if arena_rows else None
    
    # 调试日志
    if arena_info:
        print(f"[DEBUG] 查询到擂台: champion_user_id={arena_info.get('champion_user_id')}, champion_nickname={arena_info.get('champion_nickname')}")
    
    ball_id = get_arena_ball_id(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, ball_id)
    )
    ball_count = ball_rows[0].get('quantity', 0) if ball_rows else 0
    
    # 擂台名称：阶段名 + 擂台
    arena_name = f"{rank_name}擂台"
    arena_type_name = "黄金场" if arena_type == 'gold' else "普通场"
    
    # 判断擂台是否为空
    is_empty = arena_info is None or arena_info.get('champion_user_id') is None
    is_champion = arena_info and arena_info.get('champion_user_id') == user_id
    
    # 调试日志
    print(f"[DEBUG] is_empty={is_empty}, is_champion={is_champion}")
    
    # 获取VIP擂台次数限制
    vip_level = getattr(player, 'vip_level', 0) or 0
    normal_limit, gold_limit = get_vip_arena_limits(vip_level)
    daily_limit = gold_limit if arena_type == 'gold' else normal_limit
    today_count = get_today_challenge_count(user_id)
    
    arena_response = {
        "champion": arena_info['champion_nickname'] if arena_info and arena_info.get('champion_user_id') else None,
        "championUserId": arena_info['champion_user_id'] if arena_info else None,
        "consecutiveWins": arena_info['consecutive_wins'] if arena_info else 0,
        "prizePool": arena_info['prize_pool'] if arena_info else 0,
        "isChampion": is_champion,
        "isEmpty": is_empty,
    }
    
    # 调试日志
    print(f"[DEBUG] 返回的arena对象: {arena_response}")
    
    return jsonify({
        "ok": True,
        "canArena": True,
        "playerLevel": player_level,
        "playerNickname": player_nickname,
        "rankName": rank_name,
        "arenaName": arena_name,
        "arenaTypeName": arena_type_name,
        "arenaType": arena_type,
        "arena": arena_response,
        "ballName": get_arena_ball_name(arena_type),
        "ballCount": ball_count,
        "maxWins": ARENA_MAX_WINS,
        "dailyChallengeLimit": daily_limit,
        "todayChallengeCount": today_count,
        "remainingChallenges": max(0, daily_limit - today_count),
    })


@arena_bp.post("/occupy")
def occupy_arena():
    """占领擂台"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    arena_type = data.get('type', 'normal')
    
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s", (user_id,)
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = rows[0].get('level', 1)
    player_nickname = rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    if not can_arena:
        return jsonify({"ok": False, "error": "20级以上才能参与擂台"})
    
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    if not arena_rows:
        return jsonify({"ok": False, "error": "擂台不存在"})
    
    arena = arena_rows[0]
    if arena['champion_user_id']:
        return jsonify({"ok": False, "error": "擂台已有擂主，请选择挑战"})
    
    ball_id = get_arena_ball_id(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, ball_id)
    )
    ball_count = ball_rows[0].get('quantity', 0) if ball_rows else 0
    
    if ball_count < 1:
        return jsonify({"ok": False, "error": f"{get_arena_ball_name(arena_type)}不足"})
    
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s",
        (user_id, ball_id)
    )
    
    execute_update(
        """UPDATE arena SET champion_user_id = %s, champion_nickname = %s, 
           consecutive_wins = 0, prize_pool = prize_pool + 1, last_battle_time = NOW()
           WHERE rank_name = %s AND arena_type = %s""",
        (user_id, player_nickname, rank_name, arena_type)
    )
    
    return jsonify({
        "ok": True,
        "message": f"成功占领{rank_name}擂台（{'黄金场' if arena_type == 'gold' else '普通场'}）！",
    })


def _build_arena_battle_data(pvp_result, attacker_player: PvpPlayer, defender_player: PvpPlayer) -> dict:
    """根据 PvpBattleResult 构建擂台战报数据结构。

    结构与镇妖战报保持一致：
    {
        "is_victory": bool,
        "attacker_wins": 0/1,
        "defender_wins": 0/1,
        "battles": [ { battle_num, rounds: [{round, action, a_hp, d_hp}], result }, ... ]
    }
    """
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

        beast_state: dict[tuple[int, int], tuple[str, int]] = {}
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
        loser_player_id = attacker_player.player_id if winner_player_id == defender_player.player_id else defender_player.player_id
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
                winner_player_id, loser_player_id = p1, p2
                winner_beast_name, winner_hp = name1, hp1
                loser_beast_name = name2
            elif hp2 > 0 and hp1 <= 0:
                winner_player_id, loser_player_id = p2, p1
                winner_beast_name, winner_hp = name2, hp2
                loser_beast_name = name1
            elif hp1 != hp2:
                if hp1 > hp2:
                    winner_player_id, loser_player_id = p1, p2
                    winner_beast_name, winner_hp = name1, hp1
                    loser_beast_name = name2
                else:
                    winner_player_id, loser_player_id = p2, p1
                    winner_beast_name, winner_hp = name2, hp2
                    loser_beast_name = name1

        winner_player_name = get_player_name(winner_player_id)
        winner_flag = get_side_flag(winner_player_id)

        if winner_beast_name and loser_beast_name:
            result_text = (
                f"『{winner_player_name}』的{winner_beast_name}获胜，剩余气血{winner_hp}"
            )
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
    attacker_wins = 1 if is_victory else 0
    defender_wins = 1 - attacker_wins

    return {
        "is_victory": is_victory,
        "attacker_wins": attacker_wins,
        "defender_wins": defender_wins,
        "battles": battles,
    }


@arena_bp.post("/challenge")
def challenge_arena():
    """挑战擂主"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    arena_type = data.get('type', 'normal')
    
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s", (user_id,)
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = rows[0].get('level', 1)
    player_nickname = rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    if not can_arena:
        return jsonify({"ok": False, "error": "20级以上才能参与擂台"})
    
    # 获取玩家VIP等级
    player = services.player_repo.get_by_id(user_id)
    vip_level = getattr(player, 'vip_level', 0) or 0
    normal_limit, gold_limit = get_vip_arena_limits(vip_level)
    daily_limit = gold_limit if arena_type == 'gold' else normal_limit
    
    # 检查今日挑战次数
    today_count = get_today_challenge_count(user_id)
    if today_count >= daily_limit:
        return jsonify({"ok": False, "error": f"今日挑战次数已用完（{daily_limit}次/天）"})
    
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    if not arena_rows:
        return jsonify({"ok": False, "error": "擂台不存在"})
    
    arena = arena_rows[0]
    if not arena['champion_user_id']:
        return jsonify({"ok": False, "error": "擂台无擂主，请选择占领"})
    
    if arena['champion_user_id'] == user_id:
        return jsonify({"ok": False, "error": "不能挑战自己"})
    
    ball_id = get_arena_ball_id(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, ball_id)
    )
    ball_count = ball_rows[0].get('quantity', 0) if ball_rows else 0
    
    if ball_count < 1:
        return jsonify({"ok": False, "error": f"{get_arena_ball_name(arena_type)}不足"})
    
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s",
        (user_id, ball_id)
    )
    
    # 增加今日挑战次数
    increment_challenge_count(user_id)
    
    execute_update(
        "UPDATE arena SET prize_pool = prize_pool + 1 WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    champion_user_id = arena['champion_user_id']
    champion_nickname = arena['champion_nickname']
    prize_pool = arena['prize_pool'] + 1
    consecutive_wins = arena['consecutive_wins']
  
    # ===== 使用统一 PVP 战斗引擎进行一场幻兽对战 =====
    # 挑战者与擂主都取当前出战幻兽队伍
    challenger_beasts = services.player_beast_repo.get_team_beasts(user_id)
    champion_beasts = services.player_beast_repo.get_team_beasts(champion_user_id)
  
    if not challenger_beasts or not champion_beasts:
        # 没有幻兽时，简单兜底：认为挑战失败
        challenger_wins = False
        battle_data = {"is_victory": False, "attacker_wins": 0, "defender_wins": 1, "battles": []}
    else:
        attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(challenger_beasts)
        defender_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(champion_beasts)
  
        attacker_player = PvpPlayer(
            player_id=user_id,
            level=player_level,
            beasts=attacker_pvp_beasts,
            name=player_nickname,
        )
        # 取擂主等级（若没查到则用原来的连胜纪录不变）
        champ_rows = execute_query(
            "SELECT level, nickname FROM player WHERE user_id = %s",
            (champion_user_id,),
        )
        champion_level = champ_rows[0].get("level", player_level) if champ_rows else player_level
  
        defender_player = PvpPlayer(
            player_id=champion_user_id,
            level=champion_level,
            beasts=defender_pvp_beasts,
            name=champion_nickname,
        )
  
        pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
        challenger_wins = pvp_result.winner_player_id == attacker_player.player_id
        battle_data = _build_arena_battle_data(pvp_result, attacker_player, defender_player)

    # 保存战报到擂台战斗记录表
    battle_id = ARENA_BATTLE_REPO.save_battle(
        arena_type=arena_type,
        rank_name=rank_name,
        challenger_id=user_id,
        challenger_name=player_nickname,
        champion_id=champion_user_id,
        champion_name=champion_nickname,
        is_challenger_win=challenger_wins,
        battle_data=battle_data,
    )

    if challenger_wins:
        execute_update(
            """UPDATE arena SET champion_user_id = %s, champion_nickname = %s, 
               consecutive_wins = 0, prize_pool = 0, last_battle_time = NOW()
               WHERE rank_name = %s AND arena_type = %s""",
            (user_id, player_nickname, rank_name, arena_type)
        )
        
        execute_update(
            """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
               VALUES (%s, %s, %s, 0)
               ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
            (user_id, ball_id, prize_pool, prize_pool)
        )
        
        return jsonify({
            "ok": True,
            "win": True,
            "message": f"恭喜！你击败了{champion_nickname}，成为新擂主！获得奖池{prize_pool}个{get_arena_ball_name(arena_type)}！",
            "prizeWon": prize_pool,
            "battleId": battle_id,
        })
    else:
        new_wins = consecutive_wins + 1
        
        if new_wins >= ARENA_MAX_WINS:
            execute_update(
                """INSERT INTO arena_stats (user_id, rank_name, success_count)
                   VALUES (%s, %s, 1)
                   ON DUPLICATE KEY UPDATE success_count = success_count + 1""",
                (champion_user_id, rank_name)
            )
            
            execute_update(
                """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
                   VALUES (%s, %s, %s, 0)
                   ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
                (champion_user_id, ball_id, prize_pool, prize_pool)
            )
            
            execute_update(
                """UPDATE arena SET champion_user_id = NULL, champion_nickname = NULL, 
                   consecutive_wins = 0, prize_pool = 0, last_battle_time = NOW()
                   WHERE rank_name = %s AND arena_type = %s""",
                (rank_name, arena_type)
            )
            
            return jsonify({
                "ok": True,
                "win": False,
                "message": f"挑战失败！{champion_nickname}达成10连胜，领取奖池{prize_pool}个球后下台！",
                "championStepDown": True,
                "battleId": battle_id,
            })
        else:
            execute_update(
                "UPDATE arena SET consecutive_wins = %s, last_battle_time = NOW() WHERE rank_name = %s AND arena_type = %s",
                (new_wins, rank_name, arena_type)
            )
            
            return jsonify({
                "ok": True,
                "win": False,
                "message": f"挑战失败！{champion_nickname}成功守擂，当前连胜{new_wins}场！",
                "battleId": battle_id,
            })

@arena_bp.get("/battle/<int:battle_id>")
def get_arena_battle_detail(battle_id: int):
    """获取擂台战斗详情（用于详细战报页面）"""
    log = ARENA_BATTLE_REPO.get_by_id(battle_id)
    if not log:
        return jsonify({"ok": False, "error": "战报不存在"}), 404
    return jsonify({"ok": True, "battle": log.to_dict()})


@arena_bp.get("/dynamics")
def get_arena_dynamics():
    """获取擂台动态（全服 / 个人）。"""
    user_id = get_current_user_id()
    dynamic_type = request.args.get("type", "arena")  # arena | personal
    arena_type = request.args.get("arena_type", None)
    page = int(request.args.get("page", 1))  # 当前页码，默认第1页
    page_size = 10  # 每页10条
    max_pages = 5  # 最多5页
    max_records = max_pages * page_size  # 最多50条记录
    
    # 限制页码范围
    if page < 1:
        page = 1
    if page > max_pages:
        return jsonify({"ok": True, "dynamics": [], "page": page, "totalPages": 0, "hasMore": False})
    
    # 先查询总记录数（限制在50条内）
    if dynamic_type == "personal" and user_id:
        total_logs = ARENA_BATTLE_REPO.get_user_battles(user_id, limit=max_records, offset=0)
    else:
        total_logs = ARENA_BATTLE_REPO.get_recent_battles(arena_type=arena_type, limit=max_records, offset=0)
    
    total_count = len(total_logs)
    
    # 计算实际总页数
    if total_count == 0:
        total_pages = 0
    else:
        total_pages = min((total_count + page_size - 1) // page_size, max_pages)
    
    # 如果请求的页码超过实际页数，返回空
    if page > total_pages:
        return jsonify({"ok": True, "dynamics": [], "page": page, "totalPages": total_pages, "hasMore": False})
    
    # 计算当前页的数据范围
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    logs = total_logs[start_idx:end_idx]
    
    # 判断是否有下一页
    has_more = page < total_pages

    dynamics = []
    for log in logs:
        time_str = log.created_at.strftime("%Y年%m月%d日 %H:%M") if log.created_at else ""
        type_name = "普通场" if log.arena_type == "normal" else "黄金场"

        # 个人动态中，如果当前玩家是擂主，则把 ta 放在前面展示
        if dynamic_type == "personal" and user_id == log.champion_id:
            player_name = log.champion_name
            player_id = log.champion_id
            opponent_name = log.challenger_name
            opponent_id = log.challenger_id
            if log.is_challenger_win:
                action_text = f"在{type_name}被挑战失败"
            else:
                action_text = f"在{type_name}成功守擂"
        else:
            # 默认视角：挑战者在前
            player_name = log.challenger_name
            player_id = log.challenger_id
            opponent_name = log.champion_name
            opponent_id = log.champion_id
            action_text = f"在{type_name}{'战胜' if log.is_challenger_win else '惜败'}"

        dynamics.append({
            "id": log.id,
            "time": time_str,
            "player": player_name,
            "playerId": player_id,
            "opponent": opponent_name,
            "opponentId": opponent_id,
            "action": action_text,
            "extra": "",
            "hasDetail": True,
        })

    return jsonify({
        "ok": True, 
        "dynamics": dynamics, 
        "page": page, 
        "pageSize": page_size,
        "totalPages": total_pages,
        "totalCount": total_count,
        "hasMore": has_more
    })
