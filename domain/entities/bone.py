from dataclasses import dataclass, field
from typing import Optional, List


# 战骨槽位（共 7 个）
BONE_SLOTS: List[str] = [
    "头骨",
    "胸骨",
    "臂骨",
    "手骨",
    "腿骨",
    "尾骨",
    "元魂",
]


@dataclass
class MaterialCost:
    """材料消耗（用于战骨升级/进阶）"""

    item_id: int
    quantity: int


@dataclass
class BoneUpgradeCost:
    """升级消耗：升到 to_level 需要的材料。"""

    to_level: int
    materials: List[MaterialCost] = field(default_factory=list)


@dataclass
class BoneAdvanceCost:
    """进阶消耗：进阶到 to_stage 需要的材料。"""

    to_stage: int
    materials: List[MaterialCost] = field(default_factory=list)


@dataclass
class BoneTemplate:
    """战骨模板（从 configs/bone_templates.json 加载）"""

    # 基础信息
    id: int
    name: str = ""
    description: str = ""

    # 种类/槽位：头骨/胸骨/臂骨/手骨/腿骨/尾骨/元魂
    slot: str = ""

    # 成长上限（后续可用于限制升级/进阶）
    max_level: int = 1
    max_stage: int = 1

    # 当前版本：只做固定值加成（不做百分比）
    hp_flat: int = 0
    attack_flat: int = 0
    physical_defense_flat: int = 0
    magic_defense_flat: int = 0
    speed_flat: int = 0

    # 升级 / 进阶的材料配置（先作为模板数据承载，具体逻辑后续再实现）
    upgrade_costs: List[BoneUpgradeCost] = field(default_factory=list)
    advance_costs: List[BoneAdvanceCost] = field(default_factory=list)


@dataclass
class BeastBone:
    """玩家拥有的战骨实例（可装备到某只幻兽上）"""

    # 基础标识
    id: Optional[int] = None
    user_id: int = 0

    # 当前装备到的幻兽（未装备时为 None）
    beast_id: Optional[int] = None

    # 对应的战骨模板
    template_id: int = 0

    # 槽位：头骨/胸骨/臂骨/手骨/腿骨/尾骨/元魂
    slot: str = ""

    # 养成信息
    level: int = 1
    stage: int = 1

    # 当前加成属性（固定值）。
    # 说明：这些数值可以视为“缓存字段”，未来可以由配置按 (template_id, stage, level) 计算后回写。
    hp_flat: int = 0
    attack_flat: int = 0
    physical_defense_flat: int = 0
    magic_defense_flat: int = 0
    speed_flat: int = 0
