# game/domain/rules/signin_rules.py
from datetime import date, datetime, timedelta
from domain.entities.player import Player


def get_signin_base_gold(level: int) -> int:
    """根据玩家等级获取签到基础铜钱"""
    if level <= 9:
        return 5024
    elif level <= 19:
        return 10050
    elif level <= 29:
        return 15120
    elif level <= 39:
        return 20350
    elif level <= 49:
        return 25345
    elif level <= 59:
        return 30230
    elif level <= 69:
        return 35210
    elif level <= 79:
        return 40170
    elif level <= 89:
        return 45280
    else:  # 90-100级
        return 50120


def has_signed_today(player: Player, today: date | None = None) -> bool:
    """判断今天是否已经签到"""
    if today is None:
        today = date.today()
    
    # 处理 last_signin_date 可能是 datetime 或 date 类型
    last_signin = player.last_signin_date
    if isinstance(last_signin, datetime):
        last_signin = last_signin.date()
    
    return last_signin == today if last_signin else False


def can_signin(player: Player, today: date | None = None) -> bool:
    """是否可以签到"""
    return not has_signed_today(player, today)


def calculate_consecutive_days(player: Player, today: date | None = None) -> int:
    """
    计算连续签到天数
    - 如果上次签到是昨天：连续天数+1
    - 否则：连续天数重置为1
    """
    if today is None:
        today = date.today()
    
    # 处理 last_signin_date 可能是 datetime 或 date 类型
    last_signin = player.last_signin_date
    if isinstance(last_signin, datetime):
        last_signin = last_signin.date()
    
    if last_signin is None:
        # 第一次签到
        return 1
    
    yesterday = today - timedelta(days=1)
    if last_signin == yesterday:
        # 连续签到
        current_days = getattr(player, 'signin_streak', 0) or 0
        return current_days + 1
    else:
        # 中断了，重新开始
        return 1


def apply_signin_reward(player: Player, today: date | None = None) -> dict:
    """
    实际给奖励（铜钱）
    返回奖励信息
    """
    if today is None:
        today = date.today()
    
    # 计算连续签到天数
    consecutive_days = calculate_consecutive_days(player, today)
    
    # 获取基础铜钱
    base_gold = get_signin_base_gold(player.level)
    
    # 连续签到5天及以上，奖励翻倍
    is_doubled = consecutive_days >= 5
    actual_gold = base_gold * 2 if is_doubled else base_gold
    
    # 发放铜钱（使用 gold 字段）
    player.gold += actual_gold
    
    # 更新签到记录
    player.last_signin_date = today
    player.signin_streak = consecutive_days
    
    return {
        'base_gold': base_gold,
        'actual_gold': actual_gold,
        'consecutive_days': consecutive_days,
        'is_doubled': is_doubled
    }
