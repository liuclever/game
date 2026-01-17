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
    refresh_seconds = 0  # 默认可以立即刷新
    if last_refresh:
        elapsed = (datetime.now() - last_refresh).total_seconds()
        refresh_seconds = max(0, 300 - int(elapsed))  # 5分钟冷却
    
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
    
    # 计算活力消耗：6连胜之前消耗100活力，之后消耗15活力
    current_streak = record['current_streak']
    vitality_cost = 15 if current_streak >= 6 else 100
    
    try:
        # 使用真实的PVP战斗引擎
        from interfaces.web_api.bootstrap import services
        from domain.services.pvp_battle_engine import PvpPlayer, run_pvp_battle
        
        # 获取双方玩家信息
        attacker = services.player_repo.get_by_id(user_id)
        defender = services.player_repo.get_by_id(opponent_id)
        
        if not attacker or not defender:
            return jsonify({"ok": False, "error": "玩家不存在"})
        
        # 检查活力是否足够
        if attacker.vitality < vitality_cost:
            return jsonify({"ok": False, "error": f"活力不足（需要{vitality_cost}活力）"})
        
        # 扣除活力
        attacker.vitality -= vitality_cost
        services.player_repo.save(attacker)
        
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
    
    # 奖励配置（物品ID需要根据实际配置）
    rewards_config = {
        1: {
            "copper": 1000, 
            "items": [
                (6001, 1),  # 双倍卡×1
                # 结晶随机1个（从7101-7106中随机）
            ],
            "random_crystal": 1
        },
        2: {
            "copper": 5000, 
            "items": [
                (4003, 1),  # 强力捕捉球×1
            ],
            "random_crystal": 1
        },
        3: {
            "copper": 10000, 
            "items": [
                (6016, 1),  # 化仙丹×1
            ],
            "random_crystal": 1
        },
        4: {
            "copper": 50000, 
            "items": [
                (6018, 1),  # 活力草×1
            ],
            "random_crystal": 1
        },
        5: {
            "copper": 100000, 
            "items": [
                (6018, 2),  # 活力草×2
                (6003, 2),  # 小喇叭×2
            ]
        },
        6: {
            "copper": 150000, 
            "items": [
                (6017, 2),  # 重生丹×2
                (3011, 5),  # 神·逆鳞碎片×5
            ]
        }
    }
    
    reward = rewards_config.get(streak_level)
    if not reward:
        return jsonify({"ok": False, "error": "无效的奖励等级"})
    
    from interfaces.web_api.bootstrap import services
    
    # 发放铜钱
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward['copper'], user_id)
    )
    
    # 发放物品到背包
    for item_id, quantity in reward.get('items', []):
        try:
            services.inventory_service.add_item(user_id, item_id, quantity)
        except Exception as e:
            print(f"发放物品失败 item_id={item_id}: {e}")
    
    # 发放随机结晶
    if reward.get('random_crystal', 0) > 0:
        crystal_ids = [7101, 7102, 7103, 7104, 7105, 7106]  # 七种结晶
        for _ in range(reward['random_crystal']):
            crystal_id = random.choice(crystal_ids)
            try:
                services.inventory_service.add_item(user_id, crystal_id, 1)
            except Exception as e:
                print(f"发放结晶失败 crystal_id={crystal_id}: {e}")
    
    # 记录已领取
    claimed = record['claimed_rewards']
    claimed.append(streak_level)
    today = datetime.now().date()
    execute_update(
        "UPDATE arena_streak SET claimed_rewards = %s WHERE user_id = %s AND record_date = %s",
        (json.dumps(claimed), user_id, today)
    )
    
    # 构建奖励描述
    item_desc = []
    for item_id, quantity in reward.get('items', []):
        item_info = services.item_repo.get_by_id(item_id)
        item_name = item_info.name if item_info else f"物品{item_id}"
        item_desc.append(f"{item_name}×{quantity}")
    
    if reward.get('random_crystal', 0) > 0:
        item_desc.append(f"结晶×{reward['random_crystal']}")
    
    return jsonify({
        "ok": True,
        "message": f"领取成功！获得铜钱×{reward['copper']}、{' + '.join(item_desc)}"
    })

@arena_streak_bp.post('/claim-grand-prize')
def claim_grand_prize():
    """领取连胜大奖（当天连胜王专属）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    today = datetime.now().date()
    record = get_today_record(user_id)
    
    # 检查是否已领取
    if record.get('claimed_grand_prize', 0) == 1:
        return jsonify({"ok": False, "error": "今日已领取过大奖"})
    
    # 检查是否是当天连胜王（最高连胜且至少10连胜）
    if record['max_streak_today'] < 10:
        return jsonify({"ok": False, "error": "需要达到10连胜才能领取大奖"})
    
    # 查询当天最高连胜
    top_streak = execute_query(
        """SELECT MAX(max_streak_today) as top_streak 
           FROM arena_streak 
           WHERE record_date = %s""",
        (today,)
    )
    
    if not top_streak or record['max_streak_today'] < top_streak[0]['top_streak']:
        return jsonify({"ok": False, "error": "只有当天连胜王才能领取大奖"})
    
    # 大奖配置（固定奖励）
    # 铜钱60万、追魂法宝1个、金袋5个、招财神符1个
    copper_reward = 600000
    
    # 发放铜钱
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (copper_reward, user_id)
    )
    
    # 发放物品到背包
    from interfaces.web_api.bootstrap import services
    
    # 追魂法宝 (6019) x1
    services.inventory_service.add_item(user_id, 6019, 1)
    
    # 金袋 (6005) x5
    services.inventory_service.add_item(user_id, 6005, 5)
    
    # 招财神符 (6004) x1
    services.inventory_service.add_item(user_id, 6004, 1)
    
    # 标记已领取
    execute_update(
        "UPDATE arena_streak SET claimed_grand_prize = 1 WHERE user_id = %s AND record_date = %s",
        (user_id, today)
    )
    
    return jsonify({
        "ok": True,
        "message": f"恭喜！领取连胜大奖成功！\n获得铜钱×{copper_reward}、追魂法宝×1、金袋×5、招财神符×1"
    })

@arena_streak_bp.get('/grand-prize-status')
def get_grand_prize_status():
    """获取连胜大奖状态"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    today = datetime.now().date()
    record = get_today_record(user_id)
    
    # 查询当天最高连胜
    top_streak = execute_query(
        """SELECT MAX(max_streak_today) as top_streak 
           FROM arena_streak 
           WHERE record_date = %s""",
        (today,)
    )
    
    top_streak_value = top_streak[0]['top_streak'] if top_streak else 0
    is_streak_king = (record['max_streak_today'] >= 10 and 
                      record['max_streak_today'] >= top_streak_value)
    
    return jsonify({
        "ok": True,
        "can_claim": is_streak_king and record.get('claimed_grand_prize', 0) == 0,
        "claimed": record.get('claimed_grand_prize', 0) == 1,
        "current_streak": record['max_streak_today'],
        "top_streak": top_streak_value,
        "is_streak_king": is_streak_king
    })
