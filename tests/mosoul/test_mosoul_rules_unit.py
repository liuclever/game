"""
魔魂装备规则单元测试（无需启动HTTP服务 / 无需数据库）

运行方式（项目根目录）：
    python -m pytest tests/mosoul/test_mosoul_rules_unit.py -vv -s
"""

import sys
import pytest

sys.path.insert(0, ".")

from domain.entities.mosoul import MoSoul, BeastMoSoulSlot
from domain.rules.mosoul_rules import check_equip_conflict


def _mk_soul(soul_id: int, user_id: int, template_id: int, beast_id: int | None) -> MoSoul:
    return MoSoul(
        id=soul_id,
        user_id=user_id,
        template_id=template_id,
        level=1,
        exp=0,
        beast_id=beast_id,
    )


def test_same_name_only_one_on_same_beast():
    # 同一模板 => 同名
    equipped = _mk_soul(1, 1, 203, beast_id=100)  # 天魂·天绝地灭（法攻%）
    new_one = _mk_soul(2, 1, 203, beast_id=None)
    slot = BeastMoSoulSlot(beast_id=100, beast_level=80, equipped_souls=[equipped])

    conflict = check_equip_conflict(new_one, slot)
    assert conflict.has_conflict is True
    assert conflict.conflict_type == "same_name"


def test_four_souls_same_attr_percent_conflict():
    # 天魂·天绝地灭（法攻%） vs 地魂·死亡吻（法攻%）
    equipped = _mk_soul(1, 1, 203, beast_id=100)
    new_one = _mk_soul(2, 1, 303, beast_id=None)
    slot = BeastMoSoulSlot(beast_id=100, beast_level=80, equipped_souls=[equipped])

    conflict = check_equip_conflict(new_one, slot)
    assert conflict.has_conflict is True
    assert conflict.conflict_type == "same_percent"


def test_four_souls_same_attr_flat_conflict():
    # 天魂·守护之魂（气血+） vs 地魂·光明术（气血+）
    equipped = _mk_soul(1, 1, 202, beast_id=100)
    new_one = _mk_soul(2, 1, 309, beast_id=None)
    slot = BeastMoSoulSlot(beast_id=100, beast_level=80, equipped_souls=[equipped])

    conflict = check_equip_conflict(new_one, slot)
    assert conflict.has_conflict is True
    assert conflict.conflict_type == "same_flat"


def test_dragon_percent_blocks_other_percent_same_attr():
    # 龙魂·谁与争锋（速度%） vs 天魂·流星赶月（速度%）
    equipped = _mk_soul(1, 1, 103, beast_id=100)
    new_one = _mk_soul(2, 1, 212, beast_id=None)
    slot = BeastMoSoulSlot(beast_id=100, beast_level=80, equipped_souls=[equipped])

    conflict = check_equip_conflict(new_one, slot)
    assert conflict.has_conflict is True
    assert conflict.conflict_type == "dragon_percent"


def test_dragon_percent_does_not_block_flat_same_attr():
    # 龙魂·谁与争锋（速度%） vs 天魂·摄影逐日（速度+）
    equipped = _mk_soul(1, 1, 103, beast_id=100)
    new_one = _mk_soul(2, 1, 211, beast_id=None)
    slot = BeastMoSoulSlot(beast_id=100, beast_level=80, equipped_souls=[equipped])

    conflict = check_equip_conflict(new_one, slot)
    assert conflict.has_conflict is False


