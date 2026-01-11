"""签到奖励相关规则（领域层，纯函数）。

规则来源：产品需求（按玩家等级段决定基础铜钱；连续签到>=5天时基础铜钱×2；中断则重置）。
该文件不依赖数据库/框架，便于单测与复用。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional, Tuple


def base_copper_by_level(level: int) -> int:
    """根据玩家等级计算签到基础铜钱。"""
    lv = int(level or 0)
    if 1 <= lv <= 9:
        return 5024
    if 10 <= lv <= 19:
        return 10050
    if 20 <= lv <= 29:
        return 15120
    if 30 <= lv <= 39:
        return 20350
    if 40 <= lv <= 49:
        return 25345
    if 50 <= lv <= 59:
        return 30230
    if 60 <= lv <= 69:
        return 35210
    if 70 <= lv <= 79:
        return 40170
    if 80 <= lv <= 89:
        return 45280
    if 90 <= lv <= 100:
        return 50120
    # 兜底：异常等级不给奖励（避免发放错误）
    return 0


def calc_next_signin_streak(
    last_signin_date: Optional[date],
    prev_streak: int,
    today: date,
) -> int:
    """计算本次签到后的连续签到天数（不处理"今日已签"的校验）。

    - 若昨天已签到：streak+1
    - 若中断/首次：streak=1
    """
    if last_signin_date is None:
        return 1
    
    # 处理 last_signin_date 可能是 datetime 类型
    if isinstance(last_signin_date, datetime):
        last_signin_date = last_signin_date.date()
    
    if last_signin_date == today - timedelta(days=1):
        return max(1, int(prev_streak or 0) + 1)
    return 1


def calc_signin_copper(level: int, streak_after_signin: int) -> Tuple[int, int]:
    """返回 (base_copper, final_copper)。"""
    base = base_copper_by_level(level)
    multi = 2 if int(streak_after_signin or 0) >= 5 else 1
    return base, int(base * multi)
