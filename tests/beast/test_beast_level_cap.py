import pytest


from infrastructure.db.player_beast_repo_mysql import PlayerBeastData
from domain.entities.beast import Beast


def test_player_beast_add_exp_max_level_cap():
    # 玩家30级 => 幻兽最高35级（这里只测试 cap=35 的效果）
    b = PlayerBeastData(level=34, exp=0)
    leveled = b.add_exp(10**9, max_level=35)
    assert leveled is True
    assert b.level == 35
    assert b.exp == 0


def test_player_beast_add_exp_when_already_over_cap_clamps():
    b = PlayerBeastData(level=40, exp=123)
    leveled = b.add_exp(100, max_level=35)
    assert leveled is False
    assert b.level == 35
    assert b.exp == 0


def test_domain_beast_add_exp_max_level_cap():
    b = Beast(level=34, exp=0)
    leveled = b.add_exp(10**9, max_level=35)
    assert leveled is True
    assert b.level == 35
    assert b.exp == 0


