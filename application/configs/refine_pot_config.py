"""
炼妖壶配置：资质字段映射、成本、增量区间等
"""

from dataclasses import dataclass
from typing import Dict, Tuple


# 炼魂丹物品 ID（参考 configs/shop.json 中 item_id=6028）
REFINE_PILL_ITEM_ID = 6028

# 资质字段映射（与 player_beast 表字段保持一致）
ATTR_FIELD_MAP: Dict[str, str] = {
    "hp": "hp_aptitude",
    "hp_aptitude": "hp_aptitude",
    "speed": "speed_aptitude",
    "speed_aptitude": "speed_aptitude",
    "physical": "physical_atk_aptitude",
    "physical_atk_aptitude": "physical_atk_aptitude",
    "physical_defense": "physical_def_aptitude",
    "physicalDefense": "physical_def_aptitude",
    "physical_def_aptitude": "physical_def_aptitude",
    "magic": "magic_atk_aptitude",
    "magic_atk_aptitude": "magic_atk_aptitude",
    "magic_defense": "magic_def_aptitude",
    "magicDefense": "magic_def_aptitude",
    "magic_def_aptitude": "magic_def_aptitude",
}

# 成本配置（铜钱/炼魂丹数量）
BASE_COSTS = {
    "hp": {"gold": 50000, "pill": 1},
    "speed": {"gold": 50000, "pill": 1},
    "physical": {"gold": 100000, "pill": 2},
    "physical_defense": {"gold": 50000, "pill": 1},
    "magic": {"gold": 100000, "pill": 2},
    "magic_defense": {"gold": 50000, "pill": 1},
}

REFINE_COSTS: Dict[str, Dict[str, int]] = {
    "hp": BASE_COSTS["hp"],
    "hp_aptitude": BASE_COSTS["hp"],
    "speed": BASE_COSTS["speed"],
    "speed_aptitude": BASE_COSTS["speed"],
    "physical": BASE_COSTS["physical"],
    "physical_atk_aptitude": BASE_COSTS["physical"],
    "physical_defense": BASE_COSTS["physical_defense"],
    "physicalDefense": BASE_COSTS["physical_defense"],
    "physical_def_aptitude": BASE_COSTS["physical_defense"],
    "magic": BASE_COSTS["magic"],
    "magic_atk_aptitude": BASE_COSTS["magic"],
    "magic_defense": BASE_COSTS["magic_defense"],
    "magicDefense": BASE_COSTS["magic_defense"],
    "magic_def_aptitude": BASE_COSTS["magic_defense"],
}


@dataclass(frozen=True)
class DiffRangeConfig:
    """差值区间配置"""

    min_diff: int
    max_diff: int | None
    delta_range: Tuple[int, int]


DIFF_RANGE_CONFIGS = [
    DiffRangeConfig(min_diff=0, max_diff=20, delta_range=(-5, 2)),
    DiffRangeConfig(min_diff=20, max_diff=60, delta_range=(3, 5)),
    DiffRangeConfig(min_diff=60, max_diff=100, delta_range=(6, 9)),
    DiffRangeConfig(min_diff=100, max_diff=None, delta_range=(10, 15)),
]


def get_attr_field(attr_type: str) -> str:
    if attr_type not in ATTR_FIELD_MAP:
        raise KeyError(f"未知的资质类型: {attr_type}")
    return ATTR_FIELD_MAP[attr_type]


def get_refine_cost(attr_type: str) -> Dict[str, int]:
    if attr_type not in REFINE_COSTS:
        raise KeyError(f"未知的资质成本配置: {attr_type}")
    return REFINE_COSTS[attr_type]
