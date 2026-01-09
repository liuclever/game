# interfaces/routes/king_routes.py
"""召唤之王挑战赛路由"""

from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update

king_bp = Blueprint('king', __name__, url_prefix='/api/king')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


KING_DAILY_MAX_CHALLENGES = 15
KING_WIN_REWARD = 20000
KING_LOSE_REWARD = 2000

# 正赛奖励配置
# 物品ID: 5001=强力草, 5002=追魂法宝, 5003=技能书口袋
KING_FINAL_REWARDS = {
    "champion": {
        "name": "冠军", "min": 1, "max": 1, "gold": 450000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 12}, {"id": 5003, "name": "技能书口袋", "qty": 2}]
    },
    "runner_up": {
        "name": "亚军", "min": 2, "max": 2, "gold": 400000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 10}, {"id": 5003, "name": "技能书口袋", "qty": 1}]
    },
    "top4": {
        "name": "四强", "min": 3, "max": 4, "gold": 350000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 8}]
    },
    "top8": {
        "name": "八强", "min": 5, "max": 8, "gold": 300000,
        "items": [{"id": 5001, "name": "强力草", "qty": 7}, {"id": 5002, "name": "追魂法宝", "qty": 6}]
    },
    "top16": {
        "name": "十六强", "min": 9, "max": 16, "gold": 250000,
        "items": [{"id": 5001, "name": "强力草", "qty": 5}, {"id": 5002, "name": "追魂法宝", "qty": 4}]
    },
    "top32": {
        "name": "三十二强", "min": 17, "max": 32, "gold": 200000,
        "items": [{"id": 5001, "name": "强力草", "qty": 3}, {"id": 5002, "name": "追魂法宝", "qty": 2}]
    },
}


def ensure_king_rank(user_id):
    """确保玩家有挑战赛排名记录"""
    rows = execute_query("SELECT * FROM king_challenge_rank WHERE user_id = %s", (user_id,))
    if rows:
        return rows[0]
    
    total_rows = execute_query("SELECT COUNT(*) AS total FROM player")
    total = total_rows[0].get('total', 0) if total_rows else 0
    
    idx_rows = execute_query("SELECT COUNT(*) AS idx FROM player WHERE user_id <= %s", (user_id,))
    my_index = idx_rows[0].get('idx', 1) if idx_rows else 1
    
    half = (total + 1) // 2
    area_index = 1 if my_index <= half else 2
    
    max_rank_rows = execute_query(
        "SELECT COALESCE(MAX(rank_position), 0) AS max_rank FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )
    new_rank = (max_rank_rows[0].get('max_rank', 0) if max_rank_rows else 0) + 1
    
    execute_update(
        """INSERT INTO king_challenge_rank (user_id, area_index, rank_position, today_challenges, last_challenge_date)
           VALUES (%s, %s, %s, 0, CURDATE())""",
        (user_id, area_index, new_rank)
    )
    
    return {
        'user_id': user_id,
        'area_index': area_index,
        'rank_position': new_rank,
        'win_streak': 0,
        'total_wins': 0,
        'total_losses': 0,
        'today_challenges': 0
    }


@king_bp.get("/info")
def get_king_info():
    """获取召唤之王挑战赛信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    my_rank_info = ensure_king_rank(user_id)
    area_index = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    win_streak = my_rank_info['win_streak']
    
    today_challenges = my_rank_info['today_challenges']
    last_date = my_rank_info.get('last_challenge_date')
    from datetime import date
    if last_date and str(last_date) != str(date.today()):
        today_challenges = 0
    
    area_name = '一赛区' if area_index == 1 else '二赛区'
    
    challengers = []
    if my_rank > 1:
        challenger_rows = execute_query(
            """SELECT k.user_id, k.rank_position, p.nickname 
               FROM king_challenge_rank k 
               JOIN player p ON k.user_id = p.user_id
               WHERE k.area_index = %s AND k.rank_position < %s
               ORDER BY k.rank_position DESC
               LIMIT 3""",
            (area_index, my_rank)
        )
        for row in challenger_rows:
            challengers.append({
                "userId": row['user_id'],
                "nickname": row['nickname'],
                "rank": row['rank_position']
            })
    
    total_rows = execute_query("SELECT COUNT(*) AS total FROM player")
    total_players = total_rows[0].get('total', 0) if total_rows else 0

    return jsonify({
        "ok": True,
        "phase": "pre",
        "totalPlayers": total_players,
        "areaIndex": area_index,
        "areaName": area_name,
        "myRank": my_rank,
        "winStreak": win_streak,
        "todayChallenges": today_challenges,
        "todayMax": KING_DAILY_MAX_CHALLENGES,
        "challengers": challengers,
    })


@king_bp.post("/challenge")
def king_challenge():
    """发起挑战"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    target_user_id = data.get('targetUserId')
    if not target_user_id:
        return jsonify({"ok": False, "error": "请选择挑战对象"})
    
    from datetime import date
    import random
    
    my_rank_info = ensure_king_rank(user_id)
    my_area = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    
    today_challenges = my_rank_info['today_challenges']
    last_date = my_rank_info.get('last_challenge_date')
    if last_date and str(last_date) != str(date.today()):
        today_challenges = 0
    
    if today_challenges >= KING_DAILY_MAX_CHALLENGES:
        return jsonify({"ok": False, "error": "今日挑战次数已用完"})
    
    target_rows = execute_query(
        "SELECT k.*, p.nickname FROM king_challenge_rank k JOIN player p ON k.user_id = p.user_id WHERE k.user_id = %s",
        (target_user_id,)
    )
    if not target_rows:
        return jsonify({"ok": False, "error": "对手不存在"})
    
    target_info = target_rows[0]
    target_rank = target_info['rank_position']
    target_nickname = target_info['nickname']
    target_area = target_info['area_index']
    
    if target_area != my_area:
        return jsonify({"ok": False, "error": "只能挑战同赛区的玩家"})
    
    if target_rank >= my_rank:
        return jsonify({"ok": False, "error": "只能挑战排名比自己高的玩家"})
    
    challenger_wins = random.choice([True, False])
    reward = KING_WIN_REWARD if challenger_wins else KING_LOSE_REWARD
    
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward, user_id)
    )
    
    execute_update(
        """UPDATE king_challenge_rank 
           SET today_challenges = %s, last_challenge_date = CURDATE()
           WHERE user_id = %s""",
        (today_challenges + 1, user_id)
    )
    
    if challenger_wins:
        execute_update(
            "UPDATE king_challenge_rank SET rank_position = %s, win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
            (target_rank, user_id)
        )
        execute_update(
            "UPDATE king_challenge_rank SET rank_position = %s, win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
            (my_rank, target_user_id)
        )
        
        return jsonify({
            "ok": True,
            "win": True,
            "message": f"恭喜！你击败了{target_nickname}，排名上升至第{target_rank}名！获得{KING_WIN_REWARD}铜钱",
            "newRank": target_rank,
            "reward": KING_WIN_REWARD
        })
    else:
        execute_update(
            "UPDATE king_challenge_rank SET win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
            (user_id,)
        )
        execute_update(
            "UPDATE king_challenge_rank SET win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
            (target_user_id,)
        )
        
        return jsonify({
            "ok": True,
            "win": False,
            "message": f"挑战失败！{target_nickname}成功防守，排名保持第{my_rank}名。获得{KING_LOSE_REWARD}铜钱",
            "newRank": my_rank,
            "reward": KING_LOSE_REWARD
        })


@king_bp.get("/reward_info")
def get_king_reward_info():
    """获取正赛奖励信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    rank_rows = execute_query(
        "SELECT rank_position, area_index FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    if not rank_rows:
        return jsonify({"ok": True, "myRank": 0, "rewardTier": None, "canClaim": False})
    
    my_rank = rank_rows[0]['rank_position']
    
    reward_tier = None
    for key, cfg in KING_FINAL_REWARDS.items():
        if cfg['min'] <= my_rank <= cfg['max']:
            reward_tier = {
                "key": key,
                "name": cfg['name'],
                "gold": cfg['gold'],
                "items": cfg['items'],
            }
            break
    
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = 1",
        (user_id,)
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
    
    rank_rows = execute_query(
        "SELECT rank_position FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    if not rank_rows:
        return jsonify({"ok": False, "error": "你还没有参加挑战赛"})
    
    my_rank = rank_rows[0]['rank_position']
    
    reward_cfg = None
    for key, cfg in KING_FINAL_REWARDS.items():
        if cfg['min'] <= my_rank <= cfg['max']:
            reward_cfg = cfg
            break
    
    if not reward_cfg:
        return jsonify({"ok": False, "error": "你的排名不在奖励范围内"})
    
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = 1",
        (user_id,)
    )
    if claimed_rows:
        return jsonify({"ok": False, "error": "你已经领取过本赛季奖励了"})
    
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward_cfg['gold'], user_id)
    )
    
    items_msg = []
    for item in reward_cfg.get('items', []):
        execute_update(
            """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
               VALUES (%s, %s, %s, 0)
               ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
            (user_id, item['id'], item['qty'], item['qty'])
        )
        items_msg.append(f"{item['name']}x{item['qty']}")
    
    execute_update(
        "INSERT INTO king_reward_claimed (user_id, season, reward_tier, claimed_at) VALUES (%s, 1, %s, NOW())",
        (user_id, reward_cfg['name'])
    )
    
    msg = f"恭喜获得{reward_cfg['name']}奖励！铜钱+{reward_cfg['gold']}"
    if items_msg:
        msg += "，" + "、".join(items_msg)
    
    return jsonify({
        "ok": True,
        "message": msg,
        "gold": reward_cfg['gold'],
        "items": reward_cfg.get('items', [])
    })
