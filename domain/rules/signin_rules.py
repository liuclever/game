# game/domain/rules/signin_rules.py
from datetime import date
from domain.entities.player import Player


def has_signed_today(player: Player, today: date | None = None) -> bool:
    """判断今天是否已经签到"""
    if today is None:
        today = date.today()
    return player.last_signin_date == today


def can_signin(player: Player, today: date | None = None) -> bool:
    """是否可以签到"""
    return not has_signed_today(player, today)


def apply_signin_reward(player: Player, exp_gain: int, copper_gain: int) -> None:
    """实际给奖励（经验 + 铜钱）。

    应用层将 exp_gain / copper_gain 注入进来。
    """
    if exp_gain > 0:
        player.add_exp(exp_gain)
    if copper_gain > 0:
        player.copper += copper_gain
