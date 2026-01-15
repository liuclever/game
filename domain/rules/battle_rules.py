from dataclasses import dataclass
from typing import Tuple
from domain.entities.player import Player
from domain.entities.monster import Monster


@dataclass
class BattleResult:
    win: bool
    exp_gain: int
    gold_gain: int
    energy_cost: int = 5


def calc_battle(player: Player, monster: Monster) -> BattleResult:
    """最简单的战斗计算：按等级+一点随机"""
    player_power = player.level * 10
    monster_power = monster.level * 8

    win = player_power >= monster_power
    if win:
        return BattleResult(
            win=True,
            exp_gain=monster.base_exp,
            gold_gain=monster.base_gold,
            energy_cost=5,
        )
    else:
        return BattleResult(
            win=False,
            exp_gain=0,
            gold_gain=0,
            energy_cost=5,
        )
