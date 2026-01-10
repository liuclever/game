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
    # 简化：使用年份+周数作为赛季编号
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    return year * 100 + week


def ensure_king_rank(user_id):
    """确保玩家有挑战赛排名记录，没有则初始化"""
    # 检查是否已有排名
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
    
    # 在该赛区获取当前最大排名，新玩家排在最后
    max_rank_rows = execute_query(
        "SELECT COALESCE(MAX(rank_position), 0) AS max_rank FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )
    new_rank = max_rank_rows[0]['max_rank'] + 1
    
    # 插入新记录
    execute_update(
        """INSERT INTO king_challenge_rank (user_id, area_index, rank_position, today_challenges, last_challenge_date)
           VALUES (%s, %s, %s, 0, CURDATE())""",
        (user_id, area_index, new_rank)
    )
    
    # 返回新记录
    rows = execute_query("SELECT * FROM king_challenge_rank WHERE user_id = %s", (user_id,))
    return rows[0] if rows else None


@king_bp.get("/info")
def get_king_info():
    """返回召唤之王挑战赛信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 确保玩家有排名记录
    my_rank_info = ensure_king_rank(user_id)
    area_index = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    win_streak = my_rank_info['win_streak']
    
    # 检查今日挑战次数
    today = date.today()
    last_date = my_rank_info.get('last_challenge_date')
    if last_date and last_date < today:
        # 新的一天，重置挑战次数
        execute_update(
            "UPDATE king_challenge_rank SET today_challenges = 0, last_challenge_date = %s WHERE user_id = %s",
            (today, user_id)
        )
        today_challenges = 0
    else:
        today_challenges = my_rank_info.get('today_challenges', 0)
    
    # 获取赛区总人数
    total_players = execute_query(
        "SELECT COUNT(*) as count FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )[0]['count']
    
    # 获取可挑战的玩家（排名比我高的前5名）
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
            {
                "userId": row['user_id'],
                "rank": row['rank_position'],
                "nickname": row['nickname']
            }
            for row in challenger_rows
        ]
    
    # 检查冷却时间
    cooldown_remaining = 0
    if my_rank_info.get('last_challenge_time'):
        last_time = my_rank_info['last_challenge_time']
        if isinstance(last_time, str):
            last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        elapsed = (datetime.now() - last_time).total_seconds()
        if elapsed < KING_CHALLENGE_COOLDOWN:
            cooldown_remaining = int(KING_CHALLENGE_COOLDOWN - elapsed)
    
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
    })


@king_bp.post("/challenge")
def king_challenge():
    """发起挑战（带并发控制和冷却检查）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    target_user_id = data.get("targetUserId")
    if not target_user_id:
        return jsonify({"ok": False, "error": "缺少目标玩家ID"})
    
    target_user_id = int(target_user_id)
    if target_user_id == user_id:
        return jsonify({"ok": False, "error": "不能挑战自己"})
    
    # 使用数据库事务和行锁
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 开启事务
        conn.begin()
        
        # 锁定挑战者和防守者的记录（FOR UPDATE）
        cursor.execute(
            "SELECT * FROM king_challenge_rank WHERE user_id = %s FOR UPDATE",
            (user_id,)
        )
        my_rank_info = cursor.fetchone()
        
        if not my_rank_info:
            conn.rollback()
            return jsonify({"ok": False, "error": "玩家排名记录不存在"})
        
        cursor.execute(
            "SELECT * FROM king_challenge_rank WHERE user_id = %s FOR UPDATE",
            (target_user_id,)
        )
        target_rank_info = cursor.fetchone()
        
        if not target_rank_info:
            conn.rollback()
            return jsonify({"ok": False, "error": "目标玩家排名记录不存在"})
        
        # 检查是否同一赛区
        if my_rank_info['area_index'] != target_rank_info['area_index']:
            conn.rollback()
            return jsonify({"ok": False, "error": "不能挑战其他赛区的玩家"})
        
        # 检查排名（只能挑战排名更高的）
        my_rank = my_rank_info['rank_position']
        target_rank = target_rank_info['rank_position']
        if target_rank >= my_rank:
            conn.rollback()
            return jsonify({"ok": False, "error": "只能挑战排名比你高的玩家"})
        
        # 检查今日挑战次数
        today = date.today()
        last_date = my_rank_info.get('last_challenge_date')
        if last_date and last_date < today:
            today_challenges = 0
        else:
            today_challenges = my_rank_info.get('today_challenges', 0)
        
        if today_challenges >= KING_DAILY_MAX_CHALLENGES:
            conn.rollback()
            return jsonify({"ok": False, "error": "今日挑战次数已用完"})
        
        # 检查冷却时间
        if my_rank_info.get('last_challenge_time'):
            last_time = my_rank_info['last_challenge_time']
            if isinstance(last_time, str):
                last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < KING_CHALLENGE_COOLDOWN:
                remaining = int(KING_CHALLENGE_COOLDOWN - elapsed)
                conn.rollback()
                return jsonify({"ok": False, "error": f"冷却中，还需等待{remaining}秒"})
        
        # 获取双方玩家信息
        attacker = services.player_repo.get_by_id(user_id)
        defender = services.player_repo.get_by_id(target_user_id)
        
        if not attacker or not defender:
            conn.rollback()
            return jsonify({"ok": False, "error": "玩家信息不存在"})
        
        # 获取双方幻兽
        attacker_beasts = services.player_beast_repo.get_team_beasts(user_id)
        defender_beasts = services.player_beast_repo.get_team_beasts(target_user_id)
        
        if not attacker_beasts:
            conn.rollback()
            return jsonify({"ok": False, "error": "你没有出战幻兽"})
        if not defender_beasts:
            conn.rollback()
            return jsonify({"ok": False, "error": "对方没有出战幻兽"})
        
        # 转换为PVP幻兽
        attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(attacker_beasts)
        defender_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(defender_beasts)
        
        attacker_player = PvpPlayer(
            player_id=user_id,
            level=attacker.level,
            beasts=attacker_pvp_beasts,
            name=attacker.nickname,
        )
        defender_player = PvpPlayer(
            player_id=target_user_id,
            level=defender.level,
            beasts=defender_pvp_beasts,
            name=defender.nickname,
        )
        
        # 执行战斗
        pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
        challenger_wins = pvp_result.winner_player_id == user_id
        
        # 使用与切磋相同的战报构建函数
        from interfaces.routes.player_routes import _build_spar_battle_data
        battle_report_data = _build_spar_battle_data(
            pvp_result, attacker_player, defender_player,
            attacker_beasts, defender_beasts
        )
        
        # 添加召唤之王特有的字段
        battle_report_data['current_streak'] = my_rank_info.get('win_streak', 0) + (1 if challenger_wins else 0)
        
        # 发放奖励
        reward = KING_WIN_REWARD if challenger_wins else KING_LOSE_REWARD
        cursor.execute(
            "UPDATE player SET gold = gold + %s WHERE user_id = %s",
            (reward, user_id)
        )
        
        # 更新今日挑战次数和挑战时间
        cursor.execute(
            """UPDATE king_challenge_rank 
               SET today_challenges = %s, last_challenge_date = CURDATE(), last_challenge_time = NOW()
               WHERE user_id = %s""",
            (today_challenges + 1, user_id)
        )
        
        # 更新排名和战绩
        if challenger_wins:
            # 挑战者获胜：交换排名
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
            # 挑战者失败：排名不变，连胜清零
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
        
        # 保存挑战记录（用于显示动态）
        # 将完整战报数据序列化保存
        battle_report_json = json.dumps(battle_report_data, ensure_ascii=False)
        
        # 尝试保存战报，如果字段不存在则跳过
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
            # 如果battle_report字段不存在，使用旧版本的INSERT（不包含战报）
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
        
        # 提交事务
        conn.commit()
        
        return jsonify({
            "ok": True,
            "win": challenger_wins,
            "message": message,
            "newRank": new_rank,
            "reward": reward,
            "battleReport": battle_report_data
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
    
    # 检查是否是星期一
    today = datetime.now()
    if today.weekday() != 0:  # 0 = 星期一
        return jsonify({"ok": False, "error": "只能在星期一报名"})
    
    # 确保玩家有排名记录
    rank_info = ensure_king_rank(user_id)
    
    if rank_info['is_registered']:
        return jsonify({"ok": False, "error": "本周已报名"})
    
    # 更新报名状态
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
            {
                "rank": r['rank_position'],
                "nickname": r['nickname'],
                "winStreak": r['win_streak'],
                "totalWins": r['total_wins'],
                "totalLosses": r['total_losses']
            }
            for r in rankings
        ]
    })


@king_bp.get("/reward_info")
def get_king_reward_info():
    """获取正赛奖励信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取玩家排名
    rank_rows = execute_query(
        "SELECT rank_position, area_index FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    
    if not rank_rows:
        return jsonify({"ok": False, "error": "未找到排名记录"})
    
    my_rank = rank_rows[0]['rank_position']
    
    # 确定奖励档位（简化：按排名）
    reward_tier = None
    if my_rank == 1:
        reward_tier = {"key": "champion", **KING_FINAL_REWARDS["champion"]}
    elif my_rank == 2:
        reward_tier = {"key": "runner_up", **KING_FINAL_REWARDS["runner_up"]}
    elif my_rank <= 4:
        reward_tier = {"key": "top_4", **KING_FINAL_REWARDS["top_4"]}
    elif my_rank <= 8:
        reward_tier = {"key": "top_8", **KING_FINAL_REWARDS["top_8"]}
    elif my_rank <= 16:
        reward_tier = {"key": "top_16", **KING_FINAL_REWARDS["top_16"]}
    elif my_rank <= 32:
        reward_tier = {"key": "top_32", **KING_FINAL_REWARDS["top_32"]}
    
    # 检查是否已领取
    season = get_current_season()
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = %s",
        (user_id, season)
    )
    already_claimed = len(claimed_rows) > 0
    
    return jsonify({
        "ok": True,
        "myRank": my_rank,
        "rewardTier": reward_tier,
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
    
    # 获取玩家排名
    rank_rows = execute_query(
        "SELECT rank_position FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    
    if not rank_rows:
        return jsonify({"ok": False, "error": "未找到排名记录"})
    
    my_rank = rank_rows[0]['rank_position']
    
    # 确定奖励档位
    reward_cfg = None
    if my_rank == 1:
        reward_cfg = KING_FINAL_REWARDS["champion"]
    elif my_rank == 2:
        reward_cfg = KING_FINAL_REWARDS["runner_up"]
    elif my_rank <= 4:
        reward_cfg = KING_FINAL_REWARDS["top_4"]
    elif my_rank <= 8:
        reward_cfg = KING_FINAL_REWARDS["top_8"]
    elif my_rank <= 16:
        reward_cfg = KING_FINAL_REWARDS["top_16"]
    elif my_rank <= 32:
        reward_cfg = KING_FINAL_REWARDS["top_32"]
    
    if not reward_cfg:
        return jsonify({"ok": False, "error": "排名不在奖励范围内"})
    
    # 检查是否已领取
    season = get_current_season()
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = %s",
        (user_id, season)
    )
    
    if claimed_rows:
        return jsonify({"ok": False, "error": "本周奖励已领取"})
    
    # 发放铜钱
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward_cfg['gold'], user_id)
    )
    
    # 发放物品（简化：直接加到背包）
    for item_id, count in reward_cfg.get('items', []):
        try:
            services.inventory_service.add_item(user_id, item_id, count)
        except Exception as e:
            print(f"发放物品失败: {e}")
    
    # 记录已领取
    execute_update(
        "INSERT INTO king_reward_claimed (user_id, season, reward_tier, claimed_at) VALUES (%s, %s, %s, NOW())",
        (user_id, season, reward_cfg['name'])
    )
    
    return jsonify({
        "ok": True,
        "message": f"领取成功！获得{reward_cfg['gold']}铜钱和其他奖励"
    })


@king_bp.get("/final_stage_info")
def get_final_stage_info():
    """获取正赛对阵信息和玩家战绩"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from domain.services.king_final_service import get_final_stage_info as get_info, get_current_season
    
    season = get_current_season()
    stages_info = get_info(season)
    
    # 获取玩家在正赛中的最高成绩
    player_best_stage = None
    player_stage_status = {}  # 各阶段的状态
    
    for stage in ['32', '16', '8', '4', '2']:
        stage_data = stages_info.get(stage, [])
        for match in stage_data:
            if match['userId'] == user_id:
                player_stage_status[stage] = {
                    'participated': True,
                    'won': match['isWinner'] == 1,
                    'isBye': match['isBye'] == 1,
                    'opponentNickname': match['opponentNickname']
                }
                if match['isWinner'] == 1:
                    player_best_stage = stage
                break
    
    # 检查是否是冠军
    champion_data = stages_info.get('champion', [])
    is_champion = any(m['userId'] == user_id for m in champion_data)
    if is_champion:
        player_best_stage = 'champion'
    
    # 格式化战绩文本
    stage_name_map = {
        '32': '32强',
        '16': '16强',
        '8': '8强',
        '4': '4强',
        '2': '亚军',
        'champion': '冠军'
    }
    
    my_achievement = '未参加正赛'
    if player_best_stage:
        if player_best_stage == 'champion':
            my_achievement = '冠军'
        elif player_best_stage == '2':
            my_achievement = '止步半决赛'
        else:
            my_achievement = f'止步{stage_name_map.get(player_best_stage, player_best_stage)}'
    
    return jsonify({
        "ok": True,
        "season": season,
        "stages": stages_info,
        "myAchievement": my_achievement,
        "myBestStage": player_best_stage,
        "stageStatus": player_stage_status
    })


@king_bp.get("/dynamics")
def get_king_dynamics():
    """获取预选赛动态（最近的挑战记录）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取玩家的赛区
    rank_info = ensure_king_rank(user_id)
    area_index = rank_info['area_index']
    
    # 获取该赛区最近20条挑战记录
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
    
    # 格式化动态文本
    dynamics = []
    for log in logs:
        time_str = log['challenge_time'].strftime('%m-%d %H:%M')
        
        if log['challenger_wins']:
            # 挑战者胜利
            if log['challenger_rank_after'] < log['challenger_rank_before']:
                # 排名上升
                text = f"{log['challenger_name']} 挑战 {log['defender_name']}，大胜而归，排名从第{log['challenger_rank_before']}名上升至第{log['challenger_rank_after']}名"
            else:
                text = f"{log['challenger_name']} 挑战 {log['defender_name']}，大胜而归，排名保持第{log['challenger_rank_after']}名"
        else:
            # 防守者胜利
            text = f"{log['challenger_name']} 挑战 {log['defender_name']}，惜败，排名保持第{log['challenger_rank_after']}名"
        
        # 判断是否与当前玩家相关
        is_related = (log['challenger_id'] == user_id or log['defender_id'] == user_id)
        
        dynamics.append({
            "time": time_str,
            "text": text,
            "canView": is_related,  # 只有相关的战斗才能查看战报
            "logId": log['id'],  # 战报ID
            "challengerId": log['challenger_id'],
            "defenderId": log['defender_id']
        })
    
    return jsonify({
        "ok": True,
        "dynamics": dynamics
    })


@king_bp.get("/battle-report/<int:log_id>")
def get_battle_report(log_id):
    """获取指定挑战记录的战报（完整格式，包含幻兽信息）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取挑战记录
    logs = execute_query(
        """SELECT challenger_id, defender_id, battle_report, challenger_name, defender_name
           FROM king_challenge_logs
           WHERE id = %s""",
        (log_id,)
    )
    
    if not logs:
        return jsonify({"ok": False, "error": "战报不存在"})
    
    log = logs[0]
    
    # 检查是否与当前玩家相关
    if log['challenger_id'] != user_id and log['defender_id'] != user_id:
        return jsonify({"ok": False, "error": "无权查看此战报"})
    
    # 解析战报数据
    if not log['battle_report']:
        return jsonify({"ok": False, "error": "战报数据不存在"})
    
    try:
        battle_data = json.loads(log['battle_report'])
        
        # 获取双方幻兽信息
        attacker_beasts = services.player_beast_repo.get_team_beasts(log['challenger_id'])
        defender_beasts = services.player_beast_repo.get_team_beasts(log['defender_id'])
        
        # 格式化幻兽信息
        def format_beasts(beasts):
            result = []
            realm_names = ['', '凡界', '人界', '地界', '天界', '神界']
            for beast in beasts:
                # realm可能是数字或中文名称
                realm_str = str(beast.realm) if beast.realm else ''
                
                # 如果是数字，转换为名称
                if realm_str.isdigit():
                    realm_idx = int(realm_str)
                    realm_name = realm_names[realm_idx] if realm_idx < len(realm_names) else ''
                else:
                    # 已经是名称，直接使用
                    realm_name = realm_str
                
                # 获取幻兽模板信息（用于图片）
                template_id = beast.template_id
                image_url = f"/static/images/beasts/{template_id}.png"  # 幻兽图片路径
                
                result.append({
                    'name': beast.name,
                    'realm': realm_name,
                    'exp_gain': 0,  # 召唤之王不给经验
                    'image': image_url,
                    'template_id': template_id
                })
            return result
        
        attacker_beasts_formatted = format_beasts(attacker_beasts)
        defender_beasts_formatted = format_beasts(defender_beasts)
        
        # 获取战绩统计
        attacker_stats = execute_query(
            """SELECT 
                SUM(CASE WHEN challenger_wins = 1 THEN 1 ELSE 0 END) as wins,
                COUNT(*) as total
               FROM king_challenge_logs
               WHERE challenger_id = %s OR defender_id = %s""",
            (log['challenger_id'], log['challenger_id'])
        )
        
        attacker_wins = attacker_stats[0]['wins'] if attacker_stats else 0
        attacker_total = attacker_stats[0]['total'] if attacker_stats else 0
        attacker_win_rate = (attacker_wins / attacker_total * 100) if attacker_total > 0 else 0
        
        # 构建完整战报数据（参考切磋格式）
        is_attacker = (log['challenger_id'] == user_id)
        
        # 从战报中提取战斗过程
        battles = []
        battle_logs = battle_data.get('battleLogs', [])
        for idx, log_text in enumerate(battle_logs):
            battles.append({
                'battle_num': idx + 1,
                'summary': log_text
            })
        
        # 构建结果文本和符号
        victory = battle_data.get('victory', False)
        if is_attacker:
            result_text = '胜利' if victory else '失败'
        else:
            result_text = '胜利' if not victory else '失败'
            victory = not victory  # 调整视角
        
        # 生成结果符号（简化版）
        win_count = sum(1 for b in battles if '胜' in b['summary'])
        lose_count = len(battles) - win_count
        result_symbol = f"({'⚬' * win_count}:{'×' * lose_count})"
        
        complete_data = {
            'incense_bonus': '无',
            'attacker_name': log['challenger_name'] if is_attacker else log['defender_name'],
            'defender_name': log['defender_name'] if is_attacker else log['challenger_name'],
            'attacker_beasts': attacker_beasts_formatted if is_attacker else defender_beasts_formatted,
            'defender_beasts': defender_beasts_formatted if is_attacker else attacker_beasts_formatted,
            'result': f"{result_text}{result_symbol}",
            'energy_cost': 0,  # 召唤之王不消耗活力
            'battles': battles,
            'spar_wins': attacker_wins,
            'spar_total': attacker_total,
            'spar_win_rate': f"{attacker_win_rate:.2f}"
        }
        
        return jsonify({
            "ok": True,
            "battleReport": complete_data
        })
    except Exception as e:
        print(f"解析战报失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"战报数据格式错误: {str(e)}"})
