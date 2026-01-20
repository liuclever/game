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
    
    # 匹配对手（同等级段位，且有出战幻兽）
    tier_start = get_level_tier(player_level)
    tier_end = tier_start + 9
    
    opponents = execute_query(
        """SELECT DISTINCT p.user_id, p.nickname, p.level 
           FROM player p
           INNER JOIN player_beast pb ON p.user_id = pb.user_id
           WHERE p.user_id != %s 
           AND p.level BETWEEN %s AND %s 
           AND pb.in_team = 1
           ORDER BY RAND() 
           LIMIT 2""",
        (user_id, tier_start, tier_end)
    )
    
    # 如果没有对手，向下兼容（仍然要求有出战幻兽）
    if len(opponents) < 2:
        opponents = execute_query(
            """SELECT DISTINCT p.user_id, p.nickname, p.level 
               FROM player p
               INNER JOIN player_beast pb ON p.user_id = pb.user_id
               WHERE p.user_id != %s 
               AND p.level < %s 
               AND pb.in_team = 1
               ORDER BY p.level DESC 
               LIMIT 2""",
            (user_id, player_level)
        )
    
    # 计算刷新倒计时
    last_refresh = record.get('last_refresh_time')
    refresh_seconds = 300  # 5分钟
    if last_refresh:
        elapsed = (datetime.now() - last_refresh).total_seconds()
        refresh_seconds = max(0, 300 - int(elapsed))
        
        # 如果倒计时已到0（超过5分钟），自动更新刷新时间
        if refresh_seconds == 0:
            today = datetime.now().date()
            execute_update(
                "UPDATE arena_streak SET last_refresh_time = NOW() WHERE user_id = %s AND record_date = %s",
                (user_id, today)
            )
            refresh_seconds = 300
    else:
        # 首次进入，设置刷新时间
        today = datetime.now().date()
        execute_update(
            "UPDATE arena_streak SET last_refresh_time = NOW() WHERE user_id = %s AND record_date = %s",
            (user_id, today)
        )
        refresh_seconds = 300
    
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
        "claimed_rewards": record['claimed_rewards'],
        "claimed_grand_prize": record.get('claimed_grand_prize', 0)
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
        
        # 检查活力消耗
        # 规则：未达成6连胜之前消耗100活力，达成6连胜之后消耗15活力
        max_streak = record.get('max_streak_today', 0)
        energy_cost = 15 if max_streak >= 6 else 100
        
        current_energy = getattr(attacker, 'energy', 0) or 0
        if current_energy < energy_cost:
            return jsonify({
                "ok": False, 
                "error": f"活力不足，需要{energy_cost}点活力（当前{current_energy}点）"
            })
        
        # 获取双方幻兽队伍
        attacker_beasts = services.player_beast_repo.get_team_beasts(user_id)
        defender_beasts = services.player_beast_repo.get_team_beasts(opponent_id)
        
        if not attacker_beasts:
            return jsonify({"ok": False, "error": "你没有出战幻兽"})
        if not defender_beasts:
            return jsonify({"ok": False, "error": "对方没有出战幻兽，无法切磋"})
        
        # 所有检查通过后，才扣除活力
        attacker.energy = current_energy - energy_cost
        services.player_repo.save(attacker)
        
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
            battle_data['message'] = f"胜利！当前连胜{new_streak}次（消耗活力{energy_cost}点）"
            
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
            battle_data['message'] = f"失败！连胜归零（消耗活力{energy_cost}点）"
            
            return jsonify({
                "ok": True,
                "victory": False,
                "battle": battle_data
            })
    
    except Exception as e:
        # 记录错误日志
        import traceback
        print(f"连胜竞技场战斗错误: {e}")
    
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
    
    # 七种结晶 (item_id: 1001-1007)
    CRYSTAL_POOL = [1001, 1002, 1003, 1004, 1005, 1006, 1007]
    
    # 奖励配置（包含铜钱和道具）
    rewards_config = {
        1: {
            "copper": 1000,
            "items": [
                {"id": 6024, "name": "双倍卡", "quantity": 1},  # 双倍卡
                {"id": "random_crystal", "name": "结晶", "quantity": 1}  # 随机结晶
            ]
        },
        2: {
            "copper": 5000,
            "items": [
                {"id": 4003, "name": "强力捕捉球", "quantity": 1},  # 强力捕捉球
                {"id": "random_crystal", "name": "结晶", "quantity": 1}  # 随机结晶
            ]
        },
        3: {
            "copper": 10000,
            "items": [
                {"id": 6015, "name": "化仙丹", "quantity": 1},  # 化仙丹
                {"id": "random_crystal", "name": "结晶", "quantity": 1}  # 随机结晶
            ]
        },
        4: {
            "copper": 50000,
            "items": [
                {"id": 4001, "name": "活力草", "quantity": 1},  # 活力草
                {"id": "random_crystal", "name": "结晶", "quantity": 1}  # 随机结晶
            ]
        },
        5: {
            "copper": 100000,
            "items": [
                {"id": 4001, "name": "活力草", "quantity": 2},  # 活力草x2
                {"id": 6012, "name": "小喇叭", "quantity": 2}  # 小喇叭x2
            ]
        },
        6: {
            "copper": 150000,
            "items": [
                {"id": 6017, "name": "重生丹", "quantity": 2},  # 重生丹x2
                {"id": 3011, "name": "神·逆鳞碎片", "quantity": 5}  # 神·逆鳞碎片x5
            ]
        }
    }
    
    reward = rewards_config.get(streak_level)
    if not reward:
        return jsonify({"ok": False, "error": "无效的奖励等级"})
    
    try:
        from interfaces.web_api.bootstrap import services
        
        # 1. 发放铜钱
        execute_update(
            "UPDATE player SET gold = gold + %s WHERE user_id = %s",
            (reward['copper'], user_id)
        )
        
        # 2. 发放道具到背包
        reward_items = []
        for item_cfg in reward['items']:
            item_id = item_cfg['id']
            quantity = item_cfg['quantity']
            
            # 处理随机结晶
            if item_id == "random_crystal":
                item_id = random.choice(CRYSTAL_POOL)
                # 获取结晶名称
                from infrastructure.config.item_repo_from_config import ConfigItemRepo
                item_repo = ConfigItemRepo()
                crystal_item = item_repo.get_by_id(item_id)
                item_name = crystal_item.name if crystal_item else f"结晶{item_id}"
            else:
                item_name = item_cfg['name']
            
            # 添加到背包
            services.inventory_service.add_item(user_id, item_id, quantity)
            reward_items.append(f"{item_name}×{quantity}")
        
        # 3. 记录已领取
        claimed = record['claimed_rewards']
        claimed.append(streak_level)
        today = datetime.now().date()
        execute_update(
            "UPDATE arena_streak SET claimed_rewards = %s WHERE user_id = %s AND record_date = %s",
            (json.dumps(claimed), user_id, today)
        )
        
        # 构建奖励文本
        items_text = "、".join(reward_items)
        message = f"领取成功！获得铜钱×{reward['copper']}、{items_text}"
        
        return jsonify({
            "ok": True,
            "message": message
        })
    
    except Exception as e:
        import traceback
        print(f"领取连胜奖励失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": f"领取失败：{str(e)}"})


@arena_streak_bp.post('/claim-grand-prize')
def claim_grand_prize():
    """领取连胜大奖（每天只有全服连胜次数最多的玩家可以领取一次）
    
    奖励内容：
    - 铜钱×600,000
    - 追魂法宝×1 (item_id: 6019)
    - 金袋×5 (item_id: 6005)
    - 招财神符×1 (item_id: 6004)
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取今日记录
    record = get_today_record(user_id)
    
    # 检查是否已领取
    if record.get('claimed_grand_prize'):
        return jsonify({"ok": False, "error": "今日已领取过连胜大奖"})
    
    # 获取今日全服连胜王
    today = datetime.now().date()
    streak_king = execute_query(
        """SELECT user_id, max_streak_today 
           FROM arena_streak 
           WHERE record_date = %s 
           ORDER BY max_streak_today DESC LIMIT 1""",
        (today,)
    )
    
    if not streak_king:
        return jsonify({"ok": False, "error": "今日暂无连胜记录"})
    
    king_user_id = streak_king[0]['user_id']
    king_streak = streak_king[0]['max_streak_today']
    
    # 检查是否是连胜王
    if king_user_id != user_id:
        return jsonify({"ok": False, "error": "只有全服连胜次数最多的玩家才能领取大奖"})
    
    # 检查连胜次数是否大于0
    if king_streak <= 0:
        return jsonify({"ok": False, "error": "连胜次数不足，无法领取大奖"})
    
    # 发放奖励
    try:
        from interfaces.web_api.bootstrap import services
        
        # 1. 发放铜钱
        execute_update(
            "UPDATE player SET gold = gold + 600000 WHERE user_id = %s",
            (user_id,)
        )
        
        # 2. 发放道具到背包
        # 追魂法宝×1 (item_id: 6019)
        services.inventory_service.add_item(user_id, 6019, 1)
        
        # 金袋×5 (item_id: 6005)
        services.inventory_service.add_item(user_id, 6005, 5)
        
        # 招财神符×1 (item_id: 6004)
        services.inventory_service.add_item(user_id, 6004, 1)
        
        # 3. 标记已领取
        execute_update(
            "UPDATE arena_streak SET claimed_grand_prize = 1 WHERE user_id = %s AND record_date = %s",
            (user_id, today)
        )
        
        return jsonify({
            "ok": True,
            "message": f"恭喜！领取连胜大奖成功！\n获得：铜钱×600,000、追魂法宝×1、金袋×5、招财神符×1",
            "rewards": {
                "铜钱": 600000,
                "追魂法宝": 1,
                "金袋": 5,
                "招财神符": 1
            }
        })
    
    except Exception as e:
        import traceback
        print(f"领取连胜大奖失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": f"领取失败：{str(e)}"})
