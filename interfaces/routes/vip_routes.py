# interfaces/routes/vip_routes.py
"""VIP特权路由"""

import json
import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update

vip_bp = Blueprint('vip', __name__, url_prefix='/api/vip')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def load_vip_privileges():
    """加载VIP配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'vip_privileges.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@vip_bp.get('/info')
def get_vip_info():
    """获取VIP信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    rows = execute_query(
        """SELECT vip_level, diamond_spent, claimed_gift_levels, daily_copper_date 
           FROM player WHERE user_id = %s""",
        (user_id,)
    )
    
    if not rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    player = rows[0]
    vip_level = player.get('vip_level', 0) or 0
    diamond_spent = player.get('diamond_spent', 0) or 0
    
    # 解析已领取的礼包等级
    claimed_str = player.get('claimed_gift_levels', '') or ''
    claimed_gift_levels = []
    if claimed_str:
        try:
            claimed_gift_levels = [int(x) for x in claimed_str.split(',') if x]
        except:
            claimed_gift_levels = []
    
    # 检查今日是否已领取铜币
    daily_copper_date = player.get('daily_copper_date')
    today = date.today()
    daily_copper_claimed = False
    if daily_copper_date and daily_copper_date == today:
        daily_copper_claimed = True
    
    return jsonify({
        'ok': True,
        'vip_level': vip_level,
        'diamond_spent': diamond_spent,
        'claimed_gift_levels': claimed_gift_levels,
        'daily_copper_claimed': daily_copper_claimed,
    })


@vip_bp.post('/claim-gift')
def claim_welcome_gift():
    """领取VIP见面礼包"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    level = data.get('level', 0)
    
    try:
        level = int(level)
    except:
        return jsonify({'ok': False, 'error': '无效的等级'}), 400
    
    if level <= 0:
        return jsonify({'ok': False, 'error': '无效的等级'}), 400
    
    # 查询玩家VIP信息
    rows = execute_query(
        "SELECT vip_level, claimed_gift_levels FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    player = rows[0]
    vip_level = player.get('vip_level', 0) or 0
    
    # 检查是否达到该等级
    if level > vip_level:
        return jsonify({'ok': False, 'error': f'您还未达到VIP{level}'}), 400
    
    # 检查是否已领取
    claimed_str = player.get('claimed_gift_levels', '') or ''
    claimed_levels = []
    if claimed_str:
        try:
            claimed_levels = [int(x) for x in claimed_str.split(',') if x]
        except:
            claimed_levels = []
    
    if level in claimed_levels:
        return jsonify({'ok': False, 'error': f'VIP{level}礼包已领取'}), 400
    
    # 获取礼包配置
    vip_config = load_vip_privileges()
    gift_data = None
    for lv in vip_config.get('vip_levels', []):
        if lv.get('level') == level:
            gift_data = lv.get('welcome_gift')
            break
    
    if not gift_data:
        return jsonify({'ok': False, 'error': '礼包配置不存在'}), 400
    
    # 发放礼包物品
    items = gift_data.get('items', [])
    for item in items:
        item_id = item.get('item_id')
        amount = item.get('amount', 0)
        
        # 根据物品类型发放
        if item_id == 'yuan_bao':
            execute_update(
                "UPDATE player SET yuanbao = yuanbao + %s WHERE user_id = %s",
                (amount, user_id)
            )
        elif item_id == 'copper':
            execute_update(
                "UPDATE player SET copper = copper + %s WHERE user_id = %s",
                (amount, user_id)
            )
        else:
            # 其他物品放入背包 (player_inventory表)
            # 物品ID映射
            item_id_map = {
                'hua_xian_dan': 6015,      # 化仙丹
                'dice_pack': 6010,          # 骰子包
                'gold_bag': 6005,           # 金袋
                'rebirth_pill': 6017,       # 重生丹
                'soul_refine_pill': 6028,   # 炼魂丹
                'earth_spirit_stone': 7101, # 土灵石
                'wash_pulp_pill': 6031,     # 洗髓丹
                'fortune_talisman': 6004,   # 招财神符
                'teleport_talisman': 6018,  # 传送符
                'condensed_spirit_incense': 6009, # 凝神香
                'fire_spirit_stone': 7102,  # 火灵石
                'water_spirit_stone': 7103, # 水灵石
                'vitality_grass': 6013,     # 活力草
                'soul_chase_treasure': 6019, # 追魂法宝
                'demon_seal_talisman': 6001, # 镇妖符
                'wood_spirit_stone': 7104,  # 木灵石
                'skill_book_pocket': 6007,  # 技能书口袋
                'gold_spirit_stone': 7105,  # 金灵石
                'magic_rebirth_pill': 6016, # 神奇重生丹
                'god_spirit_stone': 7106,   # 神灵石
            }
            
            numeric_item_id = item_id_map.get(item_id)
            if numeric_item_id:
                inv_rows = execute_query(
                    "SELECT id, quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
                    (user_id, numeric_item_id)
                )
                if inv_rows:
                    execute_update(
                        "UPDATE player_inventory SET quantity = quantity + %s WHERE id = %s",
                        (amount, inv_rows[0]['id'])
                    )
                else:
                    execute_update(
                        "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) VALUES (%s, %s, %s, 0)",
                        (user_id, numeric_item_id, amount)
                    )
    
    # 更新已领取记录
    claimed_levels.append(level)
    new_claimed_str = ','.join(str(x) for x in sorted(claimed_levels))
    execute_update(
        "UPDATE player SET claimed_gift_levels = %s WHERE user_id = %s",
        (new_claimed_str, user_id)
    )
    
    # 构建奖励列表用于显示
    rewards = []
    for item in items:
        rewards.append({
            'name': item.get('name'),
            'amount': item.get('amount')
        })
    
    # 格式化奖励文本
    reward_text = '、'.join([f"{r['name']}x{r['amount']}" for r in rewards])
    
    return jsonify({
        'ok': True,
        'message': f'领取成功！获得{reward_text}',
        'rewards': rewards,
    })


@vip_bp.post('/claim-daily-copper')
def claim_daily_copper():
    """领取每日铜币宝箱"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    # 查询玩家VIP信息
    rows = execute_query(
        "SELECT vip_level, daily_copper_date FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    player = rows[0]
    vip_level = player.get('vip_level', 0) or 0
    
    if vip_level <= 0:
        return jsonify({'ok': False, 'error': '您还不是VIP'}), 400
    
    # 检查今日是否已领取
    daily_copper_date = player.get('daily_copper_date')
    today = date.today()
    if daily_copper_date and daily_copper_date == today:
        return jsonify({'ok': False, 'error': '今日已领取'}), 400
    
    # 获取VIP配置
    vip_config = load_vip_privileges()
    copper_amount = 0
    for lv in vip_config.get('vip_levels', []):
        if lv.get('level') == vip_level:
            copper_amount = lv.get('privileges', {}).get('daily_copper_chest', 0)
            break
    
    if copper_amount <= 0:
        return jsonify({'ok': False, 'error': '无可领取的铜币'}), 400
    
    # 发放铜币
    execute_update(
        "UPDATE player SET copper = copper + %s, daily_copper_date = %s WHERE user_id = %s",
        (copper_amount, today, user_id)
    )
    
    # 格式化显示
    if copper_amount >= 10000:
        display = f"{copper_amount // 10000}万"
    else:
        display = str(copper_amount)
    
    return jsonify({
        'ok': True,
        'message': f'领取成功！获得铜币x{display}',
        'rewards': [{'name': '铜币', 'amount': copper_amount}],
        'copper': copper_amount,
    })
