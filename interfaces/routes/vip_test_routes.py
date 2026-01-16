# interfaces/routes/vip_test_routes.py
"""VIP测试路由 - 仅用于开发测试"""

from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update

vip_test_bp = Blueprint('vip_test', __name__, url_prefix='/api/vip-test')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@vip_test_bp.post('/set-vip')
def set_vip_level():
    """设置VIP等级和消耗宝石数"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    vip_level = data.get('vip_level', 0)
    diamond_spent = data.get('diamond_spent', 0)
    
    # 如果只设置了消耗宝石数，自动计算等级
    if diamond_spent > 0 and vip_level == 0:
        vip_level = calc_vip_level_from_diamond(diamond_spent)
    
    execute_update(
        "UPDATE player SET vip_level = %s, diamond_spent = %s WHERE user_id = %s",
        (vip_level, diamond_spent, user_id)
    )
    
    return jsonify({
        'ok': True,
        'message': f'已设置VIP等级为{vip_level}，消耗宝石数为{diamond_spent}',
    })


@vip_test_bp.post('/set-level')
def set_player_level():
    """设置角色等级和经验"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    level = data.get('level', 1)
    exp = data.get('exp', 0)
    
    execute_update(
        "UPDATE player SET level = %s, exp = %s WHERE user_id = %s",
        (level, exp, user_id)
    )
    
    return jsonify({
        'ok': True,
        'message': f'已设置角色等级为{level}级，经验为{exp}',
    })


def calc_vip_level_from_diamond(diamond_spent: int) -> int:
    """根据消耗宝石数计算VIP等级"""
    import json
    from pathlib import Path
    try:
        config_path = Path(__file__).resolve().parents[2] / "configs" / "vip_privileges.json"
        with config_path.open("r", encoding="utf-8") as f:
            vip_config = json.load(f)
        vip_level = 0
        for lv in vip_config.get('vip_levels', []):
            if diamond_spent >= lv.get('required_diamond', 0):
                vip_level = lv.get('level', 0)
        return vip_level
    except Exception:
        return 0


@vip_test_bp.post('/reset-daily')
def reset_daily():
    """重置每日领取状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    # 重置每日铜币
    execute_update(
        "UPDATE player SET daily_copper_date = NULL WHERE user_id = %s",
        (user_id,)
    )
    
    # 重置招财神符使用次数
    execute_update(
        # 已取消招财神符“每日使用次数”逻辑（限购由商城 daily_limit 控制），保留 SQL 为兼容旧库：
        "DELETE FROM fortune_talisman_daily WHERE user_id = %s",
        (user_id,)
    )
    
    # 重置擂台挑战次数
    execute_update(
        "DELETE FROM arena_daily_challenge WHERE user_id = %s",
        (user_id,)
    )
    
    return jsonify({
        'ok': True,
        'message': '已重置所有每日状态',
    })


@vip_test_bp.post('/reset-gifts')
def reset_gifts():
    """重置见面礼包领取状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    execute_update(
        "UPDATE player SET claimed_gift_levels = '' WHERE user_id = %s",
        (user_id,)
    )
    
    return jsonify({
        'ok': True,
        'message': '已重置见面礼包领取状态',
    })


@vip_test_bp.post('/reset-player')
def reset_player():
    """重置玩家所有数据"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    # 重置玩家基础数据
    execute_update(
        """UPDATE player SET 
           level = 1, exp = 0, gold = 0, yuanbao = 0, silver_diamond = 0,
           copper = 0, energy = 100, prestige = 0, vip_level = 0, diamond_spent = 0,
           claimed_gift_levels = '', daily_copper_date = NULL,
           first_recharge_claimed = 0, debug_skip_days = 0
           WHERE user_id = %s""",
        (user_id,)
    )
    
    # 清空背包
    execute_update("DELETE FROM player_inventory WHERE user_id = %s", (user_id,))
    
    # 清空幻兽
    execute_update("DELETE FROM player_beast WHERE user_id = %s", (user_id,))
    
    # 清空每日状态
    # 已取消招财神符“每日使用次数”逻辑（限购由商城 daily_limit 控制）
    try:
        execute_update("DELETE FROM fortune_talisman_daily WHERE user_id = %s", (user_id,))
    except Exception:
        pass
    execute_update("DELETE FROM arena_daily_challenge WHERE user_id = %s", (user_id,))
    
    # 清空月卡
    execute_update("DELETE FROM player_month_card WHERE user_id = %s", (user_id,))
    
    return jsonify({
        'ok': True,
        'message': '已重置玩家所有数据',
    })


@vip_test_bp.post('/add-item')
def add_item():
    """添加物品到背包"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    item_id = data.get('item_id', 0)
    quantity = data.get('quantity', 1)
    
    if not item_id:
        return jsonify({'ok': False, 'error': '请指定物品ID'}), 400
    
    # 检查是否已有该物品
    rows = execute_query(
        "SELECT id, quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, item_id)
    )
    
    if rows:
        execute_update(
            "UPDATE player_inventory SET quantity = quantity + %s WHERE id = %s",
            (quantity, rows[0]['id'])
        )
    else:
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) VALUES (%s, %s, %s, 0)",
            (user_id, item_id, quantity)
        )
    
    return jsonify({
        'ok': True,
        'message': f'已添加物品{item_id} x{quantity}',
    })


@vip_test_bp.post('/add-currency')
def add_currency():
    """添加货币"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    yuanbao = data.get('yuanbao', 0)
    copper = data.get('copper', 0)
    diamond = data.get('diamond', 0)
    
    if yuanbao:
        execute_update(
            "UPDATE player SET yuanbao = yuanbao + %s WHERE user_id = %s",
            (yuanbao, user_id)
        )
    if copper:
        execute_update(
            "UPDATE player SET copper = copper + %s WHERE user_id = %s",
            (copper, user_id)
        )
    if diamond:
        execute_update(
            "UPDATE player SET silver_diamond = silver_diamond + %s WHERE user_id = %s",
            (diamond, user_id)
        )
    
    return jsonify({
        'ok': True,
        'message': f'已添加：元宝+{yuanbao}，铜币+{copper}，宝石+{diamond}',
    })


@vip_test_bp.get('/status')
def get_test_status():
    """获取测试状态信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    # 获取玩家信息
    rows = execute_query(
        """SELECT level, exp, vip_level, diamond_spent, yuanbao, copper, silver_diamond, 
                  claimed_gift_levels, daily_copper_date, debug_skip_days
           FROM player WHERE user_id = %s""",
        (user_id,)
    )
    
    if not rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    player = rows[0]
    
    # 获取招财神符今日使用次数
    ft_rows = execute_query(
        # 已取消招财神符“每日使用次数”逻辑（限购由商城 daily_limit 控制）
        "SELECT use_count FROM fortune_talisman_daily WHERE user_id = %s AND use_date = CURDATE()",
        (user_id,)
    )
    fortune_used = ft_rows[0]['use_count'] if ft_rows else 0
    
    # 获取擂台今日挑战次数
    arena_rows = execute_query(
        "SELECT challenge_count FROM arena_daily_challenge WHERE user_id = %s AND challenge_date = CURDATE()",
        (user_id,)
    )
    arena_used = arena_rows[0]['challenge_count'] if arena_rows else 0
    
    # 计算游戏日期
    from datetime import datetime, timedelta
    skip_days = player.get('debug_skip_days') or 0
    game_date = (datetime.now() + timedelta(days=skip_days)).strftime('%Y-%m-%d')
    
    return jsonify({
        'ok': True,
        'level': player.get('level', 1),
        'exp': player.get('exp', 0),
        'vip_level': player.get('vip_level', 0),
        'diamond_spent': player.get('diamond_spent', 0),
        'yuanbao': player.get('yuanbao', 0),
        'copper': player.get('copper', 0),
        'diamond': player.get('silver_diamond', 0),
        'claimed_gift_levels': player.get('claimed_gift_levels', ''),
        'daily_copper_claimed': player.get('daily_copper_date') is not None,
        'fortune_talisman_used': fortune_used,
        'arena_challenge_used': arena_used,
        'skip_days': skip_days,
        'game_date': game_date,
    })


@vip_test_bp.post('/mock-recharge')
def mock_recharge():
    """模拟充值（跳过支付，直接到账）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'ok': False, 'error': '请选择充值商品'}), 400
    
    # 加载商品配置
    import json
    from pathlib import Path
    config_path = Path(__file__).resolve().parents[2] / "configs" / "recharge_products.json"
    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        return jsonify({'ok': False, 'error': '加载商品配置失败'}), 500
    
    # 查找商品
    product = None
    for p in config.get('products', []):
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return jsonify({'ok': False, 'error': '商品不存在'}), 400
    
    # 获取玩家当前数据
    player_rows = execute_query(
        "SELECT first_recharge_claimed FROM player WHERE user_id = %s",
        (user_id,)
    )
    if not player_rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    first_recharge_claimed = player_rows[0].get('first_recharge_claimed', 0) or 0
    
    # 计算宝石（VIP等级在消耗宝石时计算）
    diamond = product.get('diamond', 0)
    
    # 首充双倍
    bonus = 0
    if first_recharge_claimed == 0 and product.get('first_bonus'):
        bonus = product.get('first_bonus', 0)
    
    total_diamond = diamond + bonus
    
    # 更新玩家数据（只增加宝石）
    if first_recharge_claimed == 0 and bonus > 0:
        execute_update(
            """UPDATE player SET 
               silver_diamond = silver_diamond + %s, 
               first_recharge_claimed = 1
               WHERE user_id = %s""",
            (total_diamond, user_id)
        )
    else:
        execute_update(
            """UPDATE player SET 
               silver_diamond = silver_diamond + %s
               WHERE user_id = %s""",
            (total_diamond, user_id)
        )
    
    return jsonify({
        'ok': True,
        'message': f'模拟充值成功！获得{total_diamond}宝石' + (f'（含首充奖励{bonus}）' if bonus > 0 else ''),
        'diamond': total_diamond,
        'bonus': bonus,
    })


@vip_test_bp.post('/skip-day')
def skip_day():
    """跳转到第二天 - 真正往后跳一天（月卡end_date减1天，模拟时间流逝）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    # 增加跳转天数计数
    execute_update(
        "UPDATE player SET debug_skip_days = COALESCE(debug_skip_days, 0) + 1 WHERE user_id = %s",
        (user_id,)
    )
    
    # 月卡end_date减1天（模拟时间往后走一天）
    execute_update(
        "UPDATE player_month_card SET end_date = DATE_SUB(end_date, INTERVAL 1 DAY), last_claim_date = NULL WHERE user_id = %s",
        (user_id,)
    )
    
    # 同时重置每日状态
    execute_update(
        "UPDATE player SET daily_copper_date = NULL WHERE user_id = %s",
        (user_id,)
    )
    execute_update(
        # 已取消招财神符“每日使用次数”逻辑（限购由商城 daily_limit 控制），保留 SQL 为兼容旧库：
        "DELETE FROM fortune_talisman_daily WHERE user_id = %s",
        (user_id,)
    )
    execute_update(
        "DELETE FROM arena_daily_challenge WHERE user_id = %s",
        (user_id,)
    )
    
    # 获取当前月卡剩余天数和跳转天数
    rows = execute_query(
        "SELECT DATEDIFF(end_date, CURDATE()) + 1 as days_left FROM player_month_card WHERE user_id = %s",
        (user_id,)
    )
    days_left = rows[0]['days_left'] if rows else 0
    
    skip_rows = execute_query(
        "SELECT debug_skip_days FROM player WHERE user_id = %s",
        (user_id,)
    )
    skip_days = skip_rows[0]['debug_skip_days'] if skip_rows else 0
    
    return jsonify({
        'ok': True,
        'message': f'已跳转到第二天，月卡剩余{days_left}天',
        'skip_days': skip_days,
    })


@vip_test_bp.post('/batch-month-card')
def batch_month_card():
    """批量购买月卡（走正常购买流程，需要有足够宝石）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    count = data.get('count', 1)
    
    try:
        count = int(count)
    except:
        return jsonify({'ok': False, 'error': '无效的数量'}), 400
    
    if count <= 0 or count > 100:
        return jsonify({'ok': False, 'error': '数量必须在1-100之间'}), 400
    
    # 检查宝石是否足够
    cost_per_card = 30
    total_cost = cost_per_card * count
    rows = execute_query(
        "SELECT silver_diamond FROM player WHERE user_id = %s",
        (user_id,)
    )
    current_diamond = rows[0].get('silver_diamond', 0) if rows else 0
    if current_diamond < total_cost:
        return jsonify({'ok': False, 'error': f'宝石不足，需要{total_cost}颗宝石，当前只有{current_diamond}颗'}), 400
    
    from application.services.month_card_service import MonthCardService
    service = MonthCardService()
    
    # 循环购买月卡（走正常流程，会扣宝石、累加diamond_spent）
    for i in range(count):
        try:
            service.purchase(user_id)
        except Exception as e:
            return jsonify({'ok': False, 'error': f'第{i+1}次购买失败: {str(e)}'}), 500
    
    return jsonify({
        'ok': True,
        'message': f'成功购买{count}张月卡，消耗{total_cost}宝石，共{count * 30}天',
    })
