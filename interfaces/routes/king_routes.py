"""召唤之王挑战赛路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from infrastructure.db.connection import execute_query, execute_update, get_connection
from interfaces.routes.auth_routes import get_current_user_id
from domain.services.pvp_battle_engine import run_pvp_battle, PvpPlayer
from interfaces.web_api.bootstrap import services
import random
import json

king_bp = Blueprint('king', __name__, url_prefix='/api/king')

# 常量配置
KING_DAILY_MAX_CHALLENGES = 15  # 每日最大挑战次数
KING_CHALLENGE_COOLDOWN = 60  # 挑战冷却时间（秒）
KING_WIN_REWARD = 20000  # 胜利奖励
KING_LOSE_REWARD = 2000  # 失败奖励

# 正赛奖励配置
KING_FINAL_REWARDS = {
    "champion": {"name": "冠军", "gold": 450000, "items": [(5001, 50), (5002, 30)]},
    "runner_up": {"name": "亚军", "gold": 350000, "items": [(5001, 40), (5002, 25)]},
    "top_4": {"name": "4强", "gold": 250000, "items": [(5001, 30), (5002, 20)]},
    "top_8": {"name": "8强", "gold": 150000, "items": [(5001, 20), (5002, 15)]},
    "top_16": {"name": "16强", "gold": 100000, "items": [(5001, 15), (5002, 10)]},
    "top_32": {"name": "32强", "gold": 50000, "items": [(5001, 10), (5002, 5)]},
}


def get_current_season():
    """获取当前赛季编号"""
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    return year * 100 + week


def ensure_king_rank(user_id):
    """确保玩家有挑战赛排名记录，没有则初始化"""
    rows = execute_query("SELECT * FROM king_challenge_rank WHERE user_id = %s", (user_id,))
    if rows:
        return rows[0]
    
    # 新玩家：分配赛区（保证两个赛区人数一致）
    area_1_count = execute_query(
        "SELECT COUNT(*) as count FROM king_challenge_rank WHERE area_index = 1"
    )[0]['count']
    area_2_count = execute_query(
        "SELECT COUNT(*) as count FROM king_challenge_rank WHERE area_index = 2"
    )[0]['count']
    
    area_index = 1 if area_1_count <= area_2_count else 2
    
    max_rank_rows = execute_query(
        "SELECT COALESCE(MAX(rank_position), 0) AS max_rank FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )
    new_rank = max_rank_rows[0]['max_rank'] + 1
    
    execute_update(
        """INSERT INTO king_challenge_rank (user_id, area_index, rank_position, today_challenges, last_challenge_date)
           VALUES (%s, %s, %s, 0, CURDATE())""",
        (user_id, area_index, new_rank)
    )
    
    rows = execute_query("SELECT * FROM king_challenge_rank WHERE user_id = %s", (user_id,))
    return rows[0] if rows else None


@king_bp.get("/info")
def get_king_info():
    """返回召唤之王挑战赛信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    my_rank_info = ensure_king_rank(user_id)
    area_index = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    win_streak = my_rank_info['win_streak']
    
    today = date.today()
    last_date = my_rank_info.get('last_challenge_date')
    if last_date and last_date < today:
        execute_update(
            "UPDATE king_challenge_rank SET today_challenges = 0, last_challenge_date = %s WHERE user_id = %s",
            (today, user_id)
        )
        today_challenges = 0
    else:
        today_challenges = my_rank_info.get('today_challenges', 0)
    
    total_players = execute_query(
        "SELECT COUNT(*) as count FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )[0]['count']
    
    challengers = []
    if my_rank > 1:
        challenger_rows = execute_query(
            """SELECT k.user_id, k.rank_position, p.nickname 
               FROM king_challenge_rank k 
               JOIN player p ON k.user_id = p.user_id
               WHERE k.area_index = %s AND k.rank_position < %s
               ORDER BY k.rank_position DESC
               LIMIT 5""",
            (area_index, my_rank)
        )
        challengers = [
            {"userId": row['user_id'], "rank": row['rank_position'], "nickname": row['nickname']}
            for row in challenger_rows
        ]
    
    cooldown_remaining = 0
    if my_rank_info.get('last_challenge_time'):
        last_time = my_rank_info['last_challenge_time']
        if isinstance(last_time, str):
            last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        elapsed = (datetime.now() - last_time).total_seconds()
        if elapsed < KING_CHALLENGE_COOLDOWN:
            cooldown_remaining = int(KING_CHALLENGE_COOLDOWN - elapsed)
    
    # 查询当前召唤之王（正赛冠军）
    king_rows = execute_query(
        "SELECT user_id, nickname FROM player WHERE is_summon_king = 1 LIMIT 1"
    )
    summon_king_name = king_rows[0]['nickname'] if king_rows else None
    summon_king_id = king_rows[0]['user_id'] if king_rows else None
    
    return jsonify({
        "ok": True,
        "areaName": f"{area_index}赛区",
        "totalPlayers": total_players,
        "myRank": my_rank,
        "winStreak": win_streak,
        "todayChallenges": today_challenges,
        "todayMax": KING_DAILY_MAX_CHALLENGES,
        "challengers": challengers,
        "cooldownRemaining": cooldown_remaining,
        "isRegistered": my_rank_info.get('is_registered', 0) == 1,
        "summonKingName": summon_king_name,
        "summonKingId": summon_king_id,
    })


@king_bp.post("/challenge")
def king_challenge():
    """发起挑战（带并发控制和冷却检查）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 检查等级限制
    player = services.player_repo.get_by_id(user_id)
    if not player or player.level < 20:
        return jsonify({"ok": False, "error": "需要达到20级才能参加挑战赛"})
    
    # 检查是否已报名
    rank_info = ensure_king_rank(user_id)
    if not rank_info.get('is_registered'):
        return jsonify({"ok": False, "error": "请先报名参加本周挑战赛"})
    
    data = request.get_json() or {}
    target_user_id = data.get("targetUserId")
    if not target_user_id:
        return jsonify({"ok": False, "error": "缺少目标玩家ID"})
    
    target_user_id = int(target_user_id)
    if target_user_id == user_id:
        return jsonify({"ok": False, "error": "不能挑战自己"})
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        conn.begin()
        
        cursor.execute("SELECT * FROM king_challenge_rank WHERE user_id = %s FOR UPDATE", (user_id,))
        my_rank_info = cursor.fetchone()
        
        if not my_rank_info:
            conn.rollback()
            return jsonify({"ok": False, "error": "玩家排名记录不存在"})
        
        cursor.execute("SELECT * FROM king_challenge_rank WHERE user_id = %s FOR UPDATE", (target_user_id,))
        target_rank_info = cursor.fetchone()
        
        if not target_rank_info:
            conn.rollback()
            return jsonify({"ok": False, "error": "目标玩家排名记录不存在"})
        
        if my_rank_info['area_index'] != target_rank_info['area_index']:
            conn.rollback()
            return jsonify({"ok": False, "error": "不能挑战其他赛区的玩家"})
        
        my_rank = my_rank_info['rank_position']
        target_rank = target_rank_info['rank_position']
        if target_rank >= my_rank:
            conn.rollback()
            return jsonify({"ok": False, "error": "只能挑战排名比你高的玩家"})
        
        today = date.today()
        last_date = my_rank_info.get('last_challenge_date')
        if last_date and last_date < today:
            today_challenges = 0
        else:
            today_challenges = my_rank_info.get('today_challenges', 0)
        
        if today_challenges >= KING_DAILY_MAX_CHALLENGES:
            conn.rollback()
            return jsonify({"ok": False, "error": "今日挑战次数已用完"})
        
        if my_rank_info.get('last_challenge_time'):
            last_time = my_rank_info['last_challenge_time']
            if isinstance(last_time, str):
                last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < KING_CHALLENGE_COOLDOWN:
                remaining = int(KING_CHALLENGE_COOLDOWN - elapsed)
                conn.rollback()
                return jsonify({"ok": False, "error": f"冷却中，还需等待{remaining}秒"})
        
        attacker = services.player_repo.get_by_id(user_id)
        defender = services.player_repo.get_by_id(target_user_id)
        
        if not attacker or not defender:
            conn.rollback()
            return jsonify({"ok": False, "error": "玩家信息不存在"})
        
        attacker_beasts = services.player_beast_repo.get_team_beasts(user_id)
        defender_beasts = services.player_beast_repo.get_team_beasts(target_user_id)
        
        if not attacker_beasts:
            conn.rollback()
            return jsonify({"ok": False, "error": "你没有出战幻兽"})
        
        # 允许挑战没有出战幻兽的对手（视为对手弃权，挑战者自动获胜）
        if not defender_beasts:
            # 对手没有幻兽，挑战者自动获胜
            reward = KING_WIN_REWARD
            cursor.execute("UPDATE player SET gold = gold + %s WHERE user_id = %s", (reward, user_id))
            
            cursor.execute(
                """UPDATE king_challenge_rank 
                   SET today_challenges = %s, last_challenge_date = CURDATE(), last_challenge_time = NOW()
                   WHERE user_id = %s""",
                (today_challenges + 1, user_id)
            )
            
            cursor.execute(
                "UPDATE king_challenge_rank SET rank_position = %s, win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
                (target_rank, user_id)
            )
            cursor.execute(
                "UPDATE king_challenge_rank SET rank_position = %s, win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
                (my_rank, target_user_id)
            )
            
            message = f"对手未出战，你不战而胜！排名上升至第{target_rank}名！获得{KING_WIN_REWARD}铜钱"
            
            # 记录战报（简化版）
            battle_report_data = {
                "winner": user_id,
                "message": "对手未出战，挑战者不战而胜",
                "current_streak": my_rank_info.get('win_streak', 0) + 1
            }
            battle_report_json = json.dumps(battle_report_data, ensure_ascii=False)
            
            try:
                cursor.execute(
                    """INSERT INTO king_challenge_logs 
                       (challenger_id, challenger_name, defender_id, defender_name, 
                        challenger_wins, challenger_rank_before, challenger_rank_after,
                        defender_rank_before, defender_rank_after, area_index, battle_report)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_id, attacker.nickname or f"玩家{user_id}", 
                     target_user_id, defender.nickname or f"玩家{target_user_id}",
                     True, my_rank, target_rank, 
                     target_rank, my_rank,
                     my_rank_info['area_index'], battle_report_json)
                )
            except Exception as e:
                print(f"保存战报失败: {e}")
            
            conn.commit()
            
            return jsonify({
                "ok": True, "win": True, "message": message,
                "newRank": target_rank, "reward": reward, "battleReport": battle_report_data
            })
        
        attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(attacker_beasts)
        defender_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(defender_beasts)
        
        attacker_player = PvpPlayer(
            player_id=user_id, level=attacker.level,
            beasts=attacker_pvp_beasts, name=attacker.nickname,
        )
        defender_player = PvpPlayer(
            player_id=target_user_id, level=defender.level,
            beasts=defender_pvp_beasts, name=defender.nickname,
        )
        
        pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
        challenger_wins = pvp_result.winner_player_id == user_id
        
        from interfaces.routes.player_routes import _build_spar_battle_data
        battle_report_data = _build_spar_battle_data(
            pvp_result, attacker_player, defender_player,
            attacker_beasts, defender_beasts
        )
        battle_report_data['current_streak'] = my_rank_info.get('win_streak', 0) + (1 if challenger_wins else 0)
        
        reward = KING_WIN_REWARD if challenger_wins else KING_LOSE_REWARD
        cursor.execute("UPDATE player SET gold = gold + %s WHERE user_id = %s", (reward, user_id))
        
        cursor.execute(
            """UPDATE king_challenge_rank 
               SET today_challenges = %s, last_challenge_date = CURDATE(), last_challenge_time = NOW()
               WHERE user_id = %s""",
            (today_challenges + 1, user_id)
        )
        
        if challenger_wins:
            cursor.execute(
                "UPDATE king_challenge_rank SET rank_position = %s, win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
                (target_rank, user_id)
            )
            cursor.execute(
                "UPDATE king_challenge_rank SET rank_position = %s, win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
                (my_rank, target_user_id)
            )
            message = f"恭喜！你击败了{defender.nickname}，排名上升至第{target_rank}名！获得{KING_WIN_REWARD}铜钱"
            new_rank = target_rank
        else:
            cursor.execute(
                "UPDATE king_challenge_rank SET win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
                (user_id,)
            )
            cursor.execute(
                "UPDATE king_challenge_rank SET win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
                (target_user_id,)
            )
            message = f"挑战失败！{defender.nickname}成功防守，排名保持第{my_rank}名。获得{KING_LOSE_REWARD}铜钱"
            new_rank = my_rank
        
        battle_report_json = json.dumps(battle_report_data, ensure_ascii=False)
        
        try:
            cursor.execute(
                """INSERT INTO king_challenge_logs 
                   (challenger_id, challenger_name, defender_id, defender_name, 
                    challenger_wins, challenger_rank_before, challenger_rank_after,
                    defender_rank_before, defender_rank_after, area_index, battle_report)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, attacker.nickname or f"玩家{user_id}", 
                 target_user_id, defender.nickname or f"玩家{target_user_id}",
                 challenger_wins, my_rank, new_rank, 
                 target_rank, my_rank if challenger_wins else target_rank,
                 my_rank_info['area_index'], battle_report_json)
            )
        except Exception as e:
            print(f"保存战报失败，使用旧版本: {e}")
            cursor.execute(
                """INSERT INTO king_challenge_logs 
                   (challenger_id, challenger_name, defender_id, defender_name, 
                    challenger_wins, challenger_rank_before, challenger_rank_after,
                    defender_rank_before, defender_rank_after, area_index)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, attacker.nickname or f"玩家{user_id}", 
                 target_user_id, defender.nickname or f"玩家{target_user_id}",
                 challenger_wins, my_rank, new_rank, 
                 target_rank, my_rank if challenger_wins else target_rank,
                 my_rank_info['area_index'])
            )
        
        conn.commit()
        
        return jsonify({
            "ok": True, "win": challenger_wins, "message": message,
            "newRank": new_rank, "reward": reward, "battleReport": battle_report_data
        })
        
    except Exception as e:
        conn.rollback()
        print(f"挑战失败: {e}")
        return jsonify({"ok": False, "error": str(e)})
    finally:
        cursor.close()


@king_bp.post("/register")
def king_register():
    """报名参加本周挑战赛"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 检查等级限制
    player = services.player_repo.get_by_id(user_id)
    if not player or player.level < 20:
        return jsonify({"ok": False, "error": "需要达到20级才能参加挑战赛"})
    
    today = datetime.now()
    if today.weekday() != 0:
        return jsonify({"ok": False, "error": "只能在星期一报名"})
    
    rank_info = ensure_king_rank(user_id)
    
    if rank_info['is_registered']:
        return jsonify({"ok": False, "error": "本周已报名"})
    
    execute_update(
        "UPDATE king_challenge_rank SET is_registered = 1 WHERE user_id = %s",
        (user_id,)
    )
    
    return jsonify({"ok": True, "message": "报名成功！预选赛将于周二开始"})


@king_bp.get("/ranking")
def get_king_ranking():
    """获取赛区排名"""
    area = request.args.get('area', 1, type=int)
    
    rankings = execute_query(
        """SELECT k.rank_position, p.nickname, k.win_streak, k.total_wins, k.total_losses
           FROM king_challenge_rank k
           JOIN player p ON k.user_id = p.user_id
           WHERE k.area_index = %s
           ORDER BY k.rank_position ASC""",
        (area,)
    )
    
    return jsonify({
        "ok": True,
        "rankings": [
            {"rank": r['rank_position'], "nickname": r['nickname'], "winStreak": r['win_streak'],
             "totalWins": r['total_wins'], "totalLosses": r['total_losses']}
            for r in rankings
        ]
    })


@king_bp.get("/reward_info")
def get_king_reward_info():
    """获取正赛奖励信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    season = get_current_season()
    
    # 查询玩家在正赛中的最佳成绩
    my_stages = execute_query(
        """SELECT stage FROM king_final_stage 
           WHERE season = %s AND user_id = %s 
           ORDER BY 
             CASE stage 
               WHEN 'champion' THEN 7
               WHEN '2' THEN 6
               WHEN '4' THEN 5
               WHEN '8' THEN 4
               WHEN '16' THEN 3
               WHEN '32' THEN 2
               ELSE 1
             END DESC
           LIMIT 1""",
        (season, user_id)
    )
    
    # 如果没有正赛记录，说明未参加正赛，不能领取奖励
    if not my_stages:
        return jsonify({
            "ok": True,
            "myRank": 0,
            "rewardTier": None,
            "canClaim": False,
            "alreadyClaimed": False,
            "message": "未参加正赛，无法领取奖励",
            "allRewards": [{"key": k, **v} for k, v in KING_FINAL_REWARDS.items()]
        })
    
    best_stage = my_stages[0]['stage']
    
    # 根据正赛成绩判定奖励等级
    reward_tier = None
    my_rank = 0
    
    if best_stage == 'champion':
        # 检查是否真的是冠军（is_winner=1）
        champion_check = execute_query(
            """SELECT is_winner FROM king_final_stage 
               WHERE season = %s AND user_id = %s AND stage = 'champion'""",
            (season, user_id)
        )
        if champion_check and champion_check[0]['is_winner'] == 1:
            reward_tier = {"key": "champion", **KING_FINAL_REWARDS["champion"]}
            my_rank = 1
        else:
            # 进入决赛但失败，是亚军
            reward_tier = {"key": "runner_up", **KING_FINAL_REWARDS["runner_up"]}
            my_rank = 2
    elif best_stage == '2':
        # 进入半决赛，至少是4强
        reward_tier = {"key": "top_4", **KING_FINAL_REWARDS["top_4"]}
        my_rank = 4
    elif best_stage == '4':
        # 进入8进4，至少是8强
        reward_tier = {"key": "top_8", **KING_FINAL_REWARDS["top_8"]}
        my_rank = 8
    elif best_stage == '8':
        # 进入16进8，至少是16强
        reward_tier = {"key": "top_16", **KING_FINAL_REWARDS["top_16"]}
        my_rank = 16
    elif best_stage == '16':
        # 进入32进16，至少是32强
        reward_tier = {"key": "top_32", **KING_FINAL_REWARDS["top_32"]}
        my_rank = 32
    elif best_stage == '32':
        # 只进入32强
        reward_tier = {"key": "top_32", **KING_FINAL_REWARDS["top_32"]}
        my_rank = 32
    
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = %s",
        (user_id, season)
    )
    already_claimed = len(claimed_rows) > 0
    
    return jsonify({
        "ok": True, "myRank": my_rank, "rewardTier": reward_tier,
        "canClaim": reward_tier is not None and not already_claimed,
        "alreadyClaimed": already_claimed,
        "allRewards": [{"key": k, **v} for k, v in KING_FINAL_REWARDS.items()]
    })


@king_bp.post("/claim_reward")
def claim_king_reward():
    """领取正赛奖励"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    season = get_current_season()
    
    # 查询玩家在正赛中的最佳成绩
    my_stages = execute_query(
        """SELECT stage, is_winner FROM king_final_stage 
           WHERE season = %s AND user_id = %s 
           ORDER BY 
             CASE stage 
               WHEN 'champion' THEN 7
               WHEN '2' THEN 6
               WHEN '4' THEN 5
               WHEN '8' THEN 4
               WHEN '16' THEN 3
               WHEN '32' THEN 2
               ELSE 1
             END DESC
           LIMIT 1""",
        (season, user_id)
    )
    
    # 如果没有正赛记录，不能领取奖励
    if not my_stages:
        return jsonify({"ok": False, "error": "未参加正赛，无法领取奖励"})
    
    best_stage = my_stages[0]['stage']
    is_winner = my_stages[0].get('is_winner')
    
    # 根据正赛成绩判定奖励
    reward_cfg = None
    if best_stage == 'champion' and is_winner == 1:
        reward_cfg = KING_FINAL_REWARDS["champion"]
    elif best_stage == 'champion' and is_winner == 0:
        reward_cfg = KING_FINAL_REWARDS["runner_up"]
    elif best_stage == '2':
        reward_cfg = KING_FINAL_REWARDS["top_4"]
    elif best_stage == '4':
        reward_cfg = KING_FINAL_REWARDS["top_8"]
    elif best_stage == '8':
        reward_cfg = KING_FINAL_REWARDS["top_16"]
    elif best_stage in ['16', '32']:
        reward_cfg = KING_FINAL_REWARDS["top_32"]
    
    if not reward_cfg:
        return jsonify({"ok": False, "error": "未获得正赛奖励"})
    
    # 检查是否已领取
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = %s",
        (user_id, season)
    )
    
    if claimed_rows:
        return jsonify({"ok": False, "error": "本周奖励已领取"})
    
    # 发放奖励
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward_cfg['gold'], user_id)
    )
    
    for item_id, count in reward_cfg.get('items', []):
        try:
            services.inventory_service.add_item(user_id, item_id, count)
        except Exception as e:
            print(f"发放物品失败: {e}")
    
    execute_update(
        "INSERT INTO king_reward_claimed (user_id, season, reward_tier, claimed_at) VALUES (%s, %s, %s, NOW())",
        (user_id, season, reward_cfg['name'])
    )
    
    return jsonify({
        "ok": True,
        "message": f"领取成功！获得{reward_cfg['gold']}铜钱和其他奖励"
    })


@king_bp.get("/dynamics")
def get_king_dynamics():
    """获取预选赛动态（最近的挑战记录）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    rank_info = ensure_king_rank(user_id)
    area_index = rank_info['area_index']
    
    logs = execute_query(
        """SELECT 
            id, challenger_id, challenger_name, defender_id, defender_name,
            challenger_wins, challenger_rank_before, challenger_rank_after,
            defender_rank_before, defender_rank_after, challenge_time
           FROM king_challenge_logs
           WHERE area_index = %s
           ORDER BY challenge_time DESC
           LIMIT 20""",
        (area_index,)
    )
    
    dynamics = []
    for log in logs:
        time_str = log['challenge_time'].strftime('%m-%d %H:%M')
        
        if log['challenger_wins']:
            if log['challenger_rank_after'] < log['challenger_rank_before']:
                text = f"{log['challenger_name']} 挑战 {log['defender_name']}，大胜而归，排名从第{log['challenger_rank_before']}名上升至第{log['challenger_rank_after']}名"
            else:
                text = f"{log['challenger_name']} 挑战 {log['defender_name']}，大胜而归，排名保持第{log['challenger_rank_after']}名"
        else:
            text = f"{log['challenger_name']} 挑战 {log['defender_name']}，惜败，排名保持第{log['challenger_rank_after']}名"
        
        is_related = (log['challenger_id'] == user_id or log['defender_id'] == user_id)
        
        dynamics.append({
            "time": time_str, "text": text, "canView": is_related, "logId": log['id'],
            "challengerId": log['challenger_id'], "defenderId": log['defender_id']
        })
    
    return jsonify({"ok": True, "dynamics": dynamics})


@king_bp.get("/battle-report/<int:log_id>")
def get_battle_report(log_id):
    """获取指定挑战记录的战报"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    logs = execute_query(
        """SELECT challenger_id, defender_id, battle_report, challenger_name, defender_name
           FROM king_challenge_logs WHERE id = %s""",
        (log_id,)
    )
    
    if not logs:
        return jsonify({"ok": False, "error": "战报不存在"})
    
    log = logs[0]
    
    if log['challenger_id'] != user_id and log['defender_id'] != user_id:
        return jsonify({"ok": False, "error": "无权查看此战报"})
    
    if not log['battle_report']:
        return jsonify({"ok": False, "error": "战报数据不存在"})
    
    try:
        battle_data = json.loads(log['battle_report'])
        return jsonify({"ok": True, "battleReport": battle_data})
    except Exception as e:
        print(f"解析战报失败: {e}")
        return jsonify({"ok": False, "error": f"战报数据格式错误: {str(e)}"})


@king_bp.get("/final_stage_info")
def get_final_stage_info_route():
    """获取正赛对阵信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    season = get_current_season()
    from domain.services.king_final_service import get_final_stage_info
    
    stage_info = get_final_stage_info(season)
    
    # 查询玩家的最佳成绩
    my_stages = execute_query(
        """SELECT stage FROM king_final_stage 
           WHERE season = %s AND user_id = %s 
           ORDER BY 
             CASE stage 
               WHEN 'champion' THEN 7
               WHEN '2' THEN 6
               WHEN '4' THEN 5
               WHEN '8' THEN 4
               WHEN '16' THEN 3
               WHEN '32' THEN 2
               ELSE 1
             END DESC
           LIMIT 1""",
        (season, user_id)
    )
    
    my_best_stage = my_stages[0]['stage'] if my_stages else None
    
    stage_name_map = {
        '32': '32强',
        '16': '16强',
        '8': '8强',
        '4': '4强',
        '2': '亚军',
        'champion': '冠军'
    }
    
    my_achievement = stage_name_map.get(my_best_stage, '未参加正赛')
    
    return jsonify({
        "ok": True,
        "stages": stage_info,
        "myAchievement": my_achievement,
        "myBestStage": my_best_stage,
        "stageStatus": {}
    })
