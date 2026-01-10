"""
龙宫之谜：纯规则（不依赖数据库/HTTP）。
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional
import random

# 探索礼包（龙宫宝箱）掉落
EVOLVE_HERB_ITEM_ID = 3012       # 进化神草
EVOLVE_CRYSTAL_ITEM_ID = 3014    # 进化圣水晶
EVOLVE_FRAGMENT_ITEM_ID = 3013   # 进化碎片


def is_dragonpalace_open(now: datetime, start: time | None = None, end: time | None = None) -> bool:
    """
    是否在开放时间内。
    约定：10:00-24:00（24:00 视为次日 00:00，不含）
    """
    if start is None:
        start = time(10, 0, 0)
    if end is None:
        end = time(0, 0, 0)

    t = now.time()
    if end == time(0, 0, 0):
        # 10:00 <= t < 24:00
        return t >= start
    return start <= t < end


def pick_dragonpalace_reward_item_id(rng: Optional[random.Random] = None) -> int:
    """
    龙宫宝箱掉落（概率：进化神草20 / 进化圣水晶10 / 进化碎片70）。
    """
    if rng is None:
        rng = random.Random()
    roll = rng.randint(1, 100)
    if roll <= 20:
        return EVOLVE_HERB_ITEM_ID
    if roll <= 30:
        return EVOLVE_CRYSTAL_ITEM_ID
    return EVOLVE_FRAGMENT_ITEM_ID


