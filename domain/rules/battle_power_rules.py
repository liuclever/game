# game/domain/rules/battle_power_rules.py
from domain.entities.player import Player


def calc_player_battle_power(player: Player) -> int:
    """
    计算玩家战力总值。
    先用一个非常简单的公式，后面再根据战骨/幻兽等慢慢加权。
    """
    level_score = player.level * 100
    exp_score = player.exp
    prestige_score = player.prestige * 50
    spirit_stone_score = player.spirit_stone * 10

    # 你可以自己调权重，这里只是占位
    return level_score + exp_score + prestige_score + spirit_stone_score
