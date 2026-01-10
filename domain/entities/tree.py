"""
古树（每周幸运数字）实体。

约束：
- 周一至周六：每天领取 1 个红果实数字（01~100），累计最多 6 个；
- 周日：领取 1 个蓝果实数字（01~100），累计最多 1 个；
- 每周幸运数字由 6 个红果实数字 + 1 个蓝果实数字组成，并在下周一公布；
- 玩家获奖后需手动领取，奖励有效期为一周（下次公布时未领取则作废）。
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
    announce_date: date
    winning_red_numbers: List[int] = field(default_factory=list)  # 6 个
    winning_blue_number: Optional[int] = None  # 1 个


@dataclass
class TreePlayerWeek:
    """玩家在某一周的领取/领奖状态。"""

    user_id: int
    week_start: date
    red_numbers: List[int] = field(default_factory=list)  # 0~6 个
    blue_number: Optional[int] = None  # 周日领取
    last_draw_date: Optional[date] = None
    claimed_at: Optional[datetime] = None
    claim_star: int = 0
    match_count: int = 0


