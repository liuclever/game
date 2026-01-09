"""
古树（每周幸运数字）实体。

约束：
- 一周领取 7 个数字（0~100），周日开奖并按命中数发放礼包。
- 本文件仅存放领域实体（数据结构），不依赖数据库/框架。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class TreeWeek:
    """每周开奖数据（全服共享）。"""

    week_start: date
    winning_numbers: List[int] = field(default_factory=list)


@dataclass
class TreePlayerWeek:
    """玩家在某一周的领取/领奖状态。"""

    user_id: int
    week_start: date
    my_numbers: List[int] = field(default_factory=list)
    last_draw_date: Optional[date] = None
    claimed_at: Optional[datetime] = None
    claim_star: int = 0
    match_count: int = 0


