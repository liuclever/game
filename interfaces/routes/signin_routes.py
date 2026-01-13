"""
签到相关路由
"""
from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update
from datetime import datetime, date, timedelta
import calendar

signin_bp = Blueprint('signin', __name__, url_prefix='/api/signin')

def get_current_user_id():
    return session.get('user_id')

@signin_bp.get('/info')
def get_signin_info():
    """获取签到信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        # 获取玩家签到信息
        player = execute_query(
            "SELECT last_signin_date, consecutive_signin_days FROM player WHERE user_id = %s",
            (user_id,)
        )
        
        if not player:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
        today = date.today()
        consecutive_days = int(player[0]['consecutive_signin_days'] or 0)
        
        # 从签到记录表中查询本月已签到的日期
        first_day = date(today.year, today.month, 1)
        records = execute_query(
            """SELECT DAY(signin_date) as day FROM player_signin_records 
               WHERE user_id = %s AND signin_date >= %s AND signin_date <= %s
               ORDER BY signin_date""",
            (user_id, first_day, today)
        )
        
        signin_days = [r['day'] for r in records]
        has_signed = today.day in signin_days
        
        return jsonify({
            "ok": True,
            "hasSigned": has_signed,
            "consecutiveDays": consecutive_days,
            "currentMonth": today.month,
            "currentYear": today.year,
            "signinDays": signin_days
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@signin_bp.post('')
def do_signin():
    """执行签到"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        today = date.today()
        
        # 检查今天是否已签到（从记录表查询）
        existing = execute_query(
            "SELECT id FROM player_signin_records WHERE user_id = %s AND signin_date = %s",
            (user_id, today)
        )
        
        if existing:
            return jsonify({"ok": False, "error": "今日已签到"}), 400
        
        # 获取玩家信息
        player = execute_query(
            "SELECT last_signin_date, consecutive_signin_days FROM player WHERE user_id = %s",
            (user_id,)
        )
        
        if not player:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
        last_signin = player[0]['last_signin_date']
        
        # 处理 last_signin_date 可能是 datetime 或 date 类型
        if isinstance(last_signin, datetime):
            last_signin = last_signin.date()
        
        # 计算连续签到天数
        consecutive_days = int(player[0]['consecutive_signin_days'] or 0)
        yesterday = today - timedelta(days=1)
        
        if last_signin == yesterday:
            # 连续签到
            consecutive_days += 1
        else:
            # 中断了，重新开始
            consecutive_days = 1
        
        # 更新签到信息
        execute_update(
            """UPDATE player 
               SET last_signin_date = %s, consecutive_signin_days = %s 
               WHERE user_id = %s""",
            (today, consecutive_days, user_id)
        )
        
        # 发放签到奖励（简化版：每次签到给1000铜钱）
        reward_copper = 1000
        execute_update(
            "UPDATE player SET gold = gold + %s WHERE user_id = %s",
            (reward_copper, user_id)
        )
        
        # 记录签到
        execute_update(
            """INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
               VALUES (%s, %s, 0, %s)""",
            (user_id, today, reward_copper)
        )
        
        return jsonify({
            "ok": True,
            "message": f"签到成功！获得铜钱{reward_copper}",
            "consecutiveDays": consecutive_days,
            "reward": {
                "copper": reward_copper,
                "multiplier": 1
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@signin_bp.get('/makeup/info')
def get_makeup_info():
    """获取补签信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        # 查询本月已签到的日期
        records = execute_query(
            """SELECT DAY(signin_date) as day FROM player_signin_records 
               WHERE user_id = %s AND signin_date >= %s AND signin_date < %s
               ORDER BY signin_date""",
            (user_id, first_day, today)
        )
        
        signed_days = set(r['day'] for r in records)
        
        # 计算本月未签到的日期（不包括今天）
        missed_days = []
        current_day = first_day
        while current_day < today:
            if current_day.day not in signed_days:
                missed_days.append(current_day.day)
            current_day += timedelta(days=1)
        
        # 检查补签卡数量（物品ID: 6027）
        cards = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = 6027",
            (user_id,)
        )
        current_cards = cards[0]['quantity'] if cards else 0
        
        return jsonify({
            "ok": True,
            "availableMakeups": min(current_cards, len(missed_days)),  # 有多少卡就能补多少天
            "maxMakeups": len(missed_days),  # 最多能补的天数
            "currentCards": current_cards,
            "missedDays": missed_days,  # 所有未签到的日期
            "signedDays": sorted(list(signed_days)),  # 已签到的日期
            "currentMonth": today.month,
            "currentYear": today.year
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@signin_bp.post('/makeup')
def do_makeup():
    """执行补签"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    day = data.get('day')  # 要补签的日期（几号）
    
    if not day:
        return jsonify({"ok": False, "error": "请选择要补签的日期"}), 400
    
    try:
        today = date.today()
        makeup_date = date(today.year, today.month, day)
        
        # 验证补签日期
        if makeup_date >= today:
            return jsonify({"ok": False, "error": "不能补签今天或未来的日期"}), 400
        
        if makeup_date.month != today.month:
            return jsonify({"ok": False, "error": "只能补签本月的日期"}), 400
        
        # 检查该日期是否已签到
        existing = execute_query(
            "SELECT id FROM player_signin_records WHERE user_id = %s AND signin_date = %s",
            (user_id, makeup_date)
        )
        
        if existing:
            return jsonify({"ok": False, "error": "该日期已签到，无需补签"}), 400
        
        # 检查补签卡（物品ID: 6027）
        cards = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = 6027",
            (user_id,)
        )
        
        if not cards or cards[0]['quantity'] < 1:
            return jsonify({"ok": False, "error": "补签卡不足"}), 400
        
        # 扣除补签卡
        execute_update(
            "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = 6027",
            (user_id,)
        )
        
        # 发放补签奖励
        reward_copper = 1000
        execute_update(
            "UPDATE player SET gold = gold + %s WHERE user_id = %s",
            (reward_copper, user_id)
        )
        
        # 记录补签
        execute_update(
            """INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
               VALUES (%s, %s, 1, %s)""",
            (user_id, makeup_date, reward_copper)
        )
        
        return jsonify({
            "ok": True,
            "message": f"补签成功！获得铜钱{reward_copper}",
            "reward": {
                "copper": reward_copper
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
