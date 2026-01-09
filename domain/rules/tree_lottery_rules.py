"""
古树幸运数字规则（领域层，纯函数）。

规则来源：产品需求
- 每天领取 1 个数字（0~100），一周最多 7 个数字；
- 周日开奖 7 个数字；
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
from typing import Iterable, List, Tuple


def week_start_of(d: date) -> date:
    """返回所在周的周一日期（周日领奖）。"""
    # Python: Monday=0 ... Sunday=6
    return d - timedelta(days=int(d.weekday()))


def is_sunday(d: date) -> bool:
    return int(d.weekday()) == 6


def can_draw_today(last_draw_date: date | None, today: date) -> bool:
    """是否可领取今日数字（每日一次）。"""
    return last_draw_date != today


def draw_unique_number(existing: Iterable[int], rng: random.Random | None = None) -> int:
    """从 0~100 中抽取一个未出现过的数字。"""
    r = rng or random.Random()
    exist = set(int(x) for x in existing)
    if len(exist) >= 101:
        # 理论上不会发生（每周最多 7 个）
        return 0
    while True:
        n = int(r.randint(0, 100))
        if n not in exist:
            return n


def generate_winning_numbers(rng: random.Random | None = None) -> List[int]:
    """生成 7 个不重复的开奖数字（0~100）。"""
    r = rng or random.Random()
    nums = r.sample(list(range(0, 101)), 7)
    return [int(x) for x in nums]


def match_count(my_numbers: Iterable[int], winning_numbers: Iterable[int]) -> int:
    """计算命中个数（按集合匹配；本模块确保每组数字不重复）。"""
    return len(set(int(x) for x in my_numbers) & set(int(x) for x in winning_numbers))


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


