"""
古树幸运数字规则（领域层，纯函数）。

规则来源：产品需求
- 周一至周六：每天领取 1 个红果实幸运数字，数字范围 01~100；
- 周日：领取 1 个蓝果实幸运数字，数字范围 01~100；
- 每周从 100 个红果实数字球中随机选出 6 个数字，从 100 个蓝果实数字球中随机选出 1 个数字，组合为当周幸运数字；
- 当周幸运数字在下周一统一公布；
- 玩家获奖后需手动领取，奖励有效期为一周（下次公布时未领取则作废）；
- 命中数 >=5：5星礼包；命中 4：4星；... 命中 1：1星；0：未中奖；
- 礼包内容：
  1星：10000 铜钱
  2星：30000 铜钱
  3星：50000 铜钱 + 重生丹×1
  4星：100000 铜钱 + 重生丹×1
  5星：150000 铜钱 + 重生丹×1

注意：本文件不依赖数据库/框架，便于单测与复用。
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Iterable, List, Optional, Tuple


def week_start_of(d: date) -> date:
    """返回所在周的周一日期。"""
    # Python: Monday=0 ... Sunday=6
    return d - timedelta(days=int(d.weekday()))


def is_sunday(d: date) -> bool:
    return int(d.weekday()) == 6


def announce_date_of(week_start: date) -> date:
    """当周幸运数字公布时间：下周一。"""
    return week_start + timedelta(days=7)


def week_index(week_start: date, epoch: date = date(2024, 12, 30)) -> int:
    """显示用周数（与站点类似的累计周数）。

    说明：以 2024-12-30（周一）作为第 1 周起点，这样 2026 年初会落在 50+ 周，贴近示例格式。
    """
    ws = week_start
    if ws < epoch:
        return 1
    return int((ws - epoch).days // 7) + 1


def can_draw_today(last_draw_date: date | None, today: date) -> bool:
    """是否可领取今日数字（每日一次）。"""
    return last_draw_date != today


def draw_red_number(rng: random.Random | None = None) -> int:
    """领取红果实幸运数字（01~100，可重复）。"""
    r = rng or random.Random()
    return int(r.randint(1, 100))


def draw_blue_number(rng: random.Random | None = None) -> int:
    """领取蓝果实幸运数字（01~100，可重复）。"""
    r = rng or random.Random()
    return int(r.randint(1, 100))


def generate_winning_numbers(rng: random.Random | None = None) -> Tuple[List[int], int]:
    """生成 (6个红果实数字, 1个蓝果实数字)。"""
    r = rng or random.Random()
    red = [int(x) for x in r.sample(list(range(1, 101)), 6)]
    blue = int(r.randint(1, 100))
    return red, blue


def match_count(
    my_red_numbers: Iterable[int],
    my_blue_number: Optional[int],
    winning_red_numbers: Iterable[int],
    winning_blue_number: Optional[int],
) -> int:
    """计算命中个数（红果实按集合匹配 + 蓝果实按相等匹配）。"""
    red_hit = len(set(int(x) for x in my_red_numbers) & set(int(x) for x in winning_red_numbers))
    blue_hit = 1 if (my_blue_number is not None and winning_blue_number is not None and int(my_blue_number) == int(winning_blue_number)) else 0
    return int(red_hit + blue_hit)


def calc_star_by_match(cnt: int) -> int:
    """命中数转换为礼包星级（0~5）。"""
    c = int(cnt or 0)
    if c <= 0:
        return 0
    return min(5, c)


def reward_by_star(star: int) -> Tuple[int, int]:
    """返回 (copper_gain, rebirth_pill_count)。"""
    s = int(star or 0)
    if s <= 0:
        return 0, 0
    if s == 1:
        return 10_000, 0
    if s == 2:
        return 30_000, 0
    if s == 3:
        return 50_000, 1
    if s == 4:
        return 100_000, 1
    return 150_000, 1


