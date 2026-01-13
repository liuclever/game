"""
连胜竞技场路由
"""
from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update
from datetime import datetime, timedelta
import json
import random

arena_streak_bp = Blueprint('arena_streak', __name__, url_prefix='/api/arena-streak')

# 开放时间：8:00-23:00
def is_open_time():
    now = datetime.now()
    hour = now.hour
    return 8 <= hour < 23

# 获取等级段位
def get_level_tier(level):
    return (level - 1) // 10 * 10 + 1  # 1-10, 11-20, 21-30...

# 获取今日记录
def get_today_record(user_id):
    today = datetime.now().date()
    rows = execute_query(
        "SELECT * FROM arena_streak WHERE user_id = %s AND record_date = %s",
        (user_id, today)
    )
    if rows:
        record = rows[0]
        record['claimed_rewards'] = json.loads(record.get('claimed_rewards') or '[]')
        return record
    
    # 创建今日记录
    execute_update(
        """INSERT INTO arena_streak (user_id, record_date, claimed_rewards) 
           VALUES (%s, %s, '[]')""",
        (user_id, today)
    )
    return {
        'user_id': user_id,
        'current_streak': 0,
        'max_streak_today': 0,
        'total_battles_today': 0,
        'claimed_rewards': [],
        'claimed_grand_prize': 0,
        'last_refresh_time': None
    }

@arena_streak_bp.get('/info')
def get_info():
    """获取竞技场信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    if not is_open_time():
        return jsonify({"ok": False, "error": "连胜竞技场开放时间为每天8:00-23:00"})
    
    # 获取玩家信息
    player = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (user_id,))
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = player[0]['level']
    player_nickname = player[0]['nickname'] or f"玩家{user_id}"
    
    # 获取今日记录
    record = get_today_record(user_id)
    
    # 匹配对手（同等级段位）
    tier_start = get_level_tier(player_level)
    tier_end = tier_start + 9
    
    opponents = execute_query(
        """SELECT user_id, nickname, level FROM player 
           WHERE user_id != %s AND level BETWEEN %s AND %s 
           ORDER BY RAND() LIMIT 2""",
        (user_id, tier_start, tier_end)
    )
    
    # 如果没有对手，向下兼容
    if len(opponents) < 2:
        opponents = execute_query(
            """SELECT user_id, nickname, level FROM player 
               WHERE user_id != %s AND level < %s 
               ORDER BY level DESC LIMIT 2""",
            (user_id, player_level)
        )
    
    # 计算刷新倒计时
    last_refresh = record.get('last_refresh_time')
    refresh_seconds = 300  # 5分钟
    if last_refresh:
        elapsed = (datetime.now() - last_refresh).total_seconds()
        refresh_seconds = max(0, 300 - int(elapsed))
    
    # 获取当前连胜王
    today = datetime.now().date()
    streak_king = execute_query(
        """SELECT p.user_id, p.nickname, a.max_streak_today 
           FROM arena_streak a 
           JOIN player p ON a.user_id = p.user_id 
           WHERE a.record_date = %s 
           ORDER BY a.max_streak_today DESC LIMIT 1""",
        (today,)
    )
    
    return jsonify({
        "ok": True,
        "current_streak": record['current_streak'],
        "max_streak_today": record['max_streak_today'],
        "opponents": [
            {
                "user_id": opp['user_id'],
                "nickname": opp['nickname'] or f"玩家{opp['user_id']}",
                "level": opp['level']
            } for opp in opponents
        ],
        "refresh_seconds": refresh_seconds,
        "streak_king": {
            "user_id": streak_king[0]['user_id'] if streak_king else None,
            "nickname": streak_king[0]['nickname'] if streak_king else "暂无",
            "streak": streak_king[0]['max_streak_today'] if streak_king else 0
        },
        "claimed_rewards": record['claimed_rewards']
    })

@arena_streak_bp.post('/refresh')
def refresh_opponents():
    """刷新对手（消耗50元宝）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 检查元宝
    player = execute_query("SELECT yuanbao FROM player WHERE user_id = %s", (user_id,))
    if not player or player[0]['yuanbao'] < 50:
        return jsonify({"ok": False, "error": "元宝不足（需要50元宝）"})
    
    # 扣除元宝
    execute_update("UPDATE player SET yuanbao = yuanbao - 50 WHERE user_id = %s", (user_id,))
    
    # 更新刷新时间
    today = datetime.now().date()
    execute_update(
        "UPDATE arena_streak SET last_refresh_time = NOW() WHERE user_id = %s AND record_date = %s",
        (user_id, today)
    )
    
    return jsonify({"ok": True, "message": "刷新成功，消耗50元宝"})

@arena_streak_bp.post('/battle')
def battle():
    """开始切磋（使用真实PVP战斗引擎）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    opponent_id = data.get('opponent_id')
    
    if not opponent_id:
        return jsonify({"ok": False, "error": "请选择对手"})
    
    # 获取今日记录
    record = get_today_record(user_id)
    
    try:
        # 使用真实的PVP战斗引擎
        from interfaces.web_api.bootstrap import services
        from domain.services.pvp_battle_engine import PvpPlayer, run_pvp_battle
        
        # 获取双方玩家信息
        attacker = services.player_repo.get_by_id(user_id)
        defender = services.player_repo.get_by_id(opponent_id)
        
        if not attacker or not defender:
            return jsonify({"ok": False, "error": "玩家不存在"})
        
        # 获取双方幻兽队伍
        attacker_beasts = services.player_beast_repo.get_team_beasts(user_id)
        defender_beasts = services.player_beast_repo.get_team_beasts(opponent_id)
        
        if not attacker_beasts:
            return jsonify({"ok": False, "error": "你没有出战幻兽"})
        if not defender_beasts:
            return jsonify({"ok": False, "error": "对方没有出战幻兽"})
        
        # 转换为PVP战斗快照
        attacker_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(attacker_beasts)
        defender_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(defender_beasts)
        
        attacker_player = PvpPlayer(
            player_id=user_id,
            level=attacker.level,
            beasts=attacker_pvp_beasts,
            name=attacker.nickname or f"玩家{user_id}",
        )
        defender_player = PvpPlayer(
            player_id=opponent_id,
            level=defender.level,
            beasts=defender_pvp_beasts,
            name=defender.nickname or f"玩家{opponent_id}",
        )
        
        # 执行真实战斗
        pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
        is_victory = pvp_result.winner_player_id == user_id
        
        # 使用与切磋相同的战报构建函数
        from interfaces.routes.player_routes import _build_spar_battle_data
        battle_data = _build_spar_battle_data(pvp_result, attacker_player, defender_player, 
                                              attacker_beasts, defender_beasts)
        
        # 更新连胜记录
        today = datetime.now().date()
        
        if is_victory:
            new_streak = record['current_streak'] + 1
            new_max = max(new_streak, record['max_streak_today'])
            
            execute_update(
                """UPDATE arena_streak 
                   SET current_streak = %s, max_streak_today = %s, 
                       total_battles_today = total_battles_today + 1,
                       last_battle_time = NOW()
                   WHERE user_id = %s AND record_date = %s""",
                (new_streak, new_max, user_id, today)
            )
            
            battle_data['current_streak'] = new_streak
            battle_data['message'] = f"胜利！当前连胜{new_streak}次"
            
            return jsonify({
                "ok": True,
                "victory": True,
                "battle": battle_data
            })
        else:
            execute_update(
                """UPDATE arena_streak 
                   SET current_streak = 0, 
                       total_battles_today = total_battles_today + 1,
                       last_battle_time = NOW()
                   WHERE user_id = %s AND record_date = %s""",
                (user_id, today)
            )
            
            battle_data['current_streak'] = 0
            battle_data['message'] = "失败！连胜归零"
            
            return jsonify({
                "ok": True,
                "victory": False,
                "battle": battle_data
            })
    
    except Exception as e:
        # 记录错误日志
        import traceback
        print(f"连胜竞技场战斗错误: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": f"战斗系统错误: {str(e)}"})

@arena_streak_bp.get('/ranking')
def get_ranking():
    """获取今日连胜榜"""
    today = datetime.now().date()
    ranking = execute_query(
        """SELECT p.user_id, p.nickname, a.max_streak_today 
           FROM arena_streak a 
           JOIN player p ON a.user_id = p.user_id 
           WHERE a.record_date = %s 
           ORDER BY a.max_streak_today DESC LIMIT 10""",
        (today,)
    )
    
    return jsonify({
        "ok": True,
        "ranking": [
            {
                "user_id": r['user_id'],
                "nickname": r['nickname'] or f"玩家{r['user_id']}",
                "streak": r['max_streak_today']
            } for r in ranking
        ]
    })

@arena_streak_bp.get('/history')
def get_history():
    """获取历届连胜王（近30天）"""
    history = execute_query(
        """SELECT user_id, nickname, max_streak, record_date 
           FROM arena_streak_history 
           ORDER BY record_date DESC LIMIT 30"""
    )
    
    return jsonify({
        "ok": True,
        "history": [
            {
                "user_id": h['user_id'],
                "nickname": h['nickname'],
                "streak": h['max_streak'],
                "date": h['record_date'].strftime('%Y-%m-%d')
            } for h in history
        ]
    })

@arena_streak_bp.post('/claim-reward')
def claim_reward():
    """领取连胜奖励"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    streak_level = data.get('streak_level')  # 1-6
    
    record = get_today_record(user_id)
    
    # 检查是否已领取
    if streak_level in record['claimed_rewards']:
        return jsonify({"ok": False, "error": "已领取过该奖励"})
    
    # 检查连胜次数
    if record['max_streak_today'] < streak_level:
        return jsonify({"ok": False, "error": f"需要达到{streak_level}连胜"})
    
    # 奖励配置
    rewards_config = {
        1: {"copper": 1000, "items": "双倍卡x1+结晶x1"},
        2: {"copper": 5000, "items": "强力捕捉球x1+结晶x1"},
        3: {"copper": 10000, "items": "化仙丹x1+结晶x1"},
        4: {"copper": 50000, "items": "活力草x1+结晶x1"},
        5: {"copper": 100000, "items": "活力草x2+小喇叭x2"},
        6: {"copper": 150000, "items": "重生丹x2+神·逆鳞碎片x1"}
    }
    
    reward = rewards_config.get(streak_level)
    if not reward:
        return jsonify({"ok": False, "error": "无效的奖励等级"})
    
    # 发放奖励
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward['copper'], user_id)
    )
    
    # 记录已领取
    claimed = record['claimed_rewards']
    claimed.append(streak_level)
    today = datetime.now().date()
    execute_update(
        "UPDATE arena_streak SET claimed_rewards = %s WHERE user_id = %s AND record_date = %s",
        (json.dumps(claimed), user_id, today)
    )
    
    return jsonify({
        "ok": True,
        "message": f"领取成功！获得铜钱{reward['copper']}+{reward['items']}"
    })
