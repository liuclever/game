from __future__ import annotations

from typing import Optional


BEAST_LEVEL_PLAYER_OFFSET_LIMIT = 5


def calc_beast_max_level(
    player_level: int,
    global_max_level: Optional[int] = None,
    offset: int = BEAST_LEVEL_PLAYER_OFFSET_LIMIT,
) -> int:
    """计算幻兽允许达到的最高等级：不超过(玩家等级 + offset)，且不超过全局等级上限（若提供）。

    规则示例：玩家30级，offset=5 => 幻兽最高35级。
    """
    try:
        pl = int(player_level or 1)
    except (TypeError, ValueError):
        pl = 1
    if pl < 1:
        pl = 1

    try:
        off = int(offset)
    except (TypeError, ValueError):
        off = BEAST_LEVEL_PLAYER_OFFSET_LIMIT
    if off < 0:
        off = 0

    cap = pl + off

    if global_max_level is not None:
        try:
            gmax = int(global_max_level)
        except (TypeError, ValueError):
            gmax = None
        if gmax is not None and gmax > 0:
            cap = min(cap, gmax)

    return max(1, cap)


