# game/domain/rules/signin_rules.py
from datetime import date
from domain.entities.player import Player


SIGNIN_EXP = 50
SIGNIN_GOLD = 100


def has_signed_today(player: Player, today: date | None = None) -> bool:
    """判断今天是否已经签到"""
    if today is None:
        today = date.today()
    return player.last_signin_date == today


def can_signin(player: Player, today: date | None = None) -> bool:
    """是否可以签到"""
    return not has_signed_today(player, today)


def apply_signin_reward(player: Player) -> None:
    """实际给奖励（经验 + 金币）"""
    player.add_exp(SIGNIN_EXP)
    player.gold += SIGNIN_GOLD
