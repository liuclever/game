"""魔魂系统实体定义。

魔魂是可以装备到幻兽身上的道具，用于提升幻兽属性。
魔魂分为神魂、龙魂、天魂、地魂、玄魂、黄魂和废魂七种等级。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
from pathlib import Path
import json


# ===================== 魔魂等级枚举 =====================
class MoSoulGrade(str, Enum):
    """魔魂等级枚举"""
    GOD_SOUL = "god_soul"           # 神魂
    DRAGON_SOUL = "dragon_soul"     # 龙魂
    HEAVEN_SOUL = "heaven_soul"     # 天魂
    EARTH_SOUL = "earth_soul"       # 地魂
    DARK_SOUL = "dark_soul"         # 玄魂
    YELLOW_SOUL = "yellow_soul"     # 黄魂
    WASTE_SOUL = "waste_soul"       # 废魂

    @property
    def chinese_name(self) -> str:
        """返回中文名称"""
        names = {
            "god_soul": "神魂",
            "dragon_soul": "龙魂",
            "heaven_soul": "天魂",
            "earth_soul": "地魂",
            "dark_soul": "玄魂",
            "yellow_soul": "黄魂",
            "waste_soul": "废魂",
        }
        return names.get(self.value, "未知")

    @property
    def rarity(self) -> int:
        """返回稀有度等级（0-6）"""
        rarity_map = {
            "god_soul": 6,
            "dragon_soul": 5,
            "heaven_soul": 4,
            "earth_soul": 3,
            "dark_soul": 2,
            "yellow_soul": 1,
            "waste_soul": 0,
        }
        return rarity_map.get(self.value, 0)


# ===================== 魔魂配置加载 =====================
_mosoul_config_cache: Optional[Dict] = None


def _load_mosoul_config() -> Dict:
    """加载魔魂配置"""
    global _mosoul_config_cache
    if _mosoul_config_cache is not None:
        return _mosoul_config_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "mosoul_types.json"
    if not path.exists():
        _mosoul_config_cache = {"souls": [], "soul_grades": {}}
        return _mosoul_config_cache

    try:
        with path.open("r", encoding="utf-8") as f:
            _mosoul_config_cache = json.load(f)
    except Exception:
        _mosoul_config_cache = {"souls": [], "soul_grades": {}}

    return _mosoul_config_cache


def _load_upgrade_config() -> Dict:
    """加载升级配置"""
    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "mosoul_upgrade.json"
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ===================== 魔魂模板 =====================
@dataclass
class MoSoulTemplate:
    """魔魂模板（从配置文件加载）"""
    id: int
    name: str
    grade: MoSoulGrade
    effects: List[Dict]  # [{"attr": "hp", "percent": 0, "flat": 100}, ...]
    description: str = ""

    @classmethod
    def from_config(cls, data: Dict) -> "MoSoulTemplate":
        """从配置字典创建模板"""
        grade = MoSoulGrade(data.get("grade", "yellow_soul"))
        return cls(
            id=data["id"],
            name=data["name"],
            grade=grade,
            effects=data.get("effects", []),
            description=data.get("description", ""),
        )

    def get_effect_at_level(self, level: int) -> List[Dict]:
        """获取指定等级的效果值（每级乘以等级系数）"""
        result = []
        for eff in self.effects:
            result.append({
                "attr": eff["attr"],
                "percent": eff.get("percent", 0) * level,
                "flat": eff.get("flat", 0) * level,
            })
        return result


def get_mosoul_template(template_id: int) -> Optional[MoSoulTemplate]:
    """根据模板ID获取魔魂模板"""
    config = _load_mosoul_config()
    for soul_data in config.get("souls", []):
        if soul_data.get("id") == template_id:
            return MoSoulTemplate.from_config(soul_data)
    return None


def get_all_mosoul_templates() -> Dict[int, MoSoulTemplate]:
    """获取所有魔魂模板"""
    config = _load_mosoul_config()
    return {
        soul_data["id"]: MoSoulTemplate.from_config(soul_data)
        for soul_data in config.get("souls", [])
    }


def get_templates_by_grade(grade: MoSoulGrade) -> List[MoSoulTemplate]:
    """根据等级获取魔魂模板列表"""
    config = _load_mosoul_config()
    return [
        MoSoulTemplate.from_config(soul_data)
        for soul_data in config.get("souls", [])
        if soul_data.get("grade") == grade.value
    ]


# ===================== 魔魂实例 =====================
@dataclass
class MoSoul:
    """玩家拥有的魔魂实例"""

    id: Optional[int] = None        # 魔魂实例ID
    user_id: int = 0                # 所属玩家ID
    template_id: int = 0            # 魔魂模板ID
    level: int = 1                  # 当前等级（1-10）
    exp: int = 0                    # 当前经验值
    beast_id: Optional[int] = None  # 装备到的幻兽ID（None表示未装备）

    def get_template(self) -> Optional[MoSoulTemplate]:
        """获取对应的魔魂模板"""
        return get_mosoul_template(self.template_id)

    @property
    def grade(self) -> Optional[MoSoulGrade]:
        """获取魔魂等级"""
        template = self.get_template()
        return template.grade if template else None

    @property
    def name(self) -> str:
        """获取魔魂名称"""
        template = self.get_template()
        return template.name if template else "未知魔魂"

    def get_current_effects(self) -> List[Dict]:
        """获取当前等级的效果列表"""
        template = self.get_template()
        if not template:
            return []
        return template.get_effect_at_level(self.level)

    def exp_to_next_level(self) -> int:
        """获取升到下一级所需经验"""
        if self.level >= 10:
            return 0

        template = self.get_template()
        if not template:
            return 0

        config = _load_upgrade_config()
        grade_key = template.grade.value
        upgrade_data = config.get("upgrade_exp", {}).get(grade_key, {})
        levels = upgrade_data.get("levels", {})

        return levels.get(str(self.level), 0)

    def add_exp(self, amount: int) -> bool:
        """增加经验值，返回是否升级

        支持连续升级，溢出经验会累积到下一级。
        """
        if amount <= 0 or self.level >= 10:
            return False

        leveled_up = False
        remaining = amount

        while remaining > 0 and self.level < 10:
            required = self.exp_to_next_level()
            if required <= 0:
                break

            need = required - self.exp
            if remaining >= need:
                remaining -= need
                self.exp = 0
                self.level += 1
                leveled_up = True
            else:
                self.exp += remaining
                remaining = 0

        return leveled_up

    def get_exp_provide(self) -> int:
        """获取该魔魂作为材料时提供的经验值"""
        config = _load_upgrade_config()
        grade_exp = config.get("grade_exp_provide", {})
        template = self.get_template()
        if not template:
            return 0
        return grade_exp.get(template.grade.value, 0)

    def is_equipped(self) -> bool:
        """是否已装备到幻兽"""
        return self.beast_id is not None

    def to_dict(self) -> Dict:
        """转换为字典"""
        template = self.get_template()
        return {
            "id": self.id,
            "user_id": self.user_id,
            "template_id": self.template_id,
            "name": self.name,
            "grade": self.grade.value if self.grade else None,
            "grade_name": self.grade.chinese_name if self.grade else None,
            "level": self.level,
            "exp": self.exp,
            "exp_to_next": self.exp_to_next_level(),
            "beast_id": self.beast_id,
            "effects": self.get_current_effects(),
        }


# ===================== 储魂器 =====================
@dataclass
class SoulStorage:
    """玩家储魂器

    存放猎取到的魔魂，容量根据VIP等级确定。
    """

    user_id: int
    vip_level: int = 0
    souls: List[MoSoul] = field(default_factory=list)

    def get_capacity(self) -> int:
        """获取储魂器容量"""
        config = _load_upgrade_config()
        vip_capacity = config.get("storage_capacity", {}).get("vip_capacity", {})

        # 确保VIP等级在有效范围内
        vip_str = str(min(self.vip_level, 10))
        return vip_capacity.get(vip_str, 50)

    def get_free_slots(self) -> int:
        """获取剩余空位数"""
        return max(0, self.get_capacity() - len(self.souls))

    def is_full(self) -> bool:
        """储魂器是否已满"""
        return len(self.souls) >= self.get_capacity()

    def can_add(self, count: int = 1) -> bool:
        """是否可以添加指定数量的魔魂"""
        return self.get_free_slots() >= count

    def add_soul(self, soul: MoSoul) -> bool:
        """添加魔魂到储魂器，返回是否成功"""
        if self.is_full():
            return False
        self.souls.append(soul)
        return True

    def remove_soul(self, soul_id: int) -> Optional[MoSoul]:
        """从储魂器移除魔魂，返回被移除的魔魂"""
        for i, soul in enumerate(self.souls):
            if soul.id == soul_id:
                return self.souls.pop(i)
        return None

    def get_soul(self, soul_id: int) -> Optional[MoSoul]:
        """根据ID获取魔魂"""
        for soul in self.souls:
            if soul.id == soul_id:
                return soul
        return None

    def get_souls_by_grade(self, grade: MoSoulGrade) -> List[MoSoul]:
        """根据等级筛选魔魂"""
        return [soul for soul in self.souls if soul.grade == grade]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "vip_level": self.vip_level,
            "capacity": self.get_capacity(),
            "used": len(self.souls),
            "free": self.get_free_slots(),
            "souls": [soul.to_dict() for soul in self.souls],
        }


# ===================== 幻兽魔魂槽位 =====================
@dataclass
class BeastMoSoulSlot:
    """幻兽魔魂装备槽位"""

    beast_id: int
    beast_level: int = 1
    equipped_souls: List[MoSoul] = field(default_factory=list)

    def get_max_slots(self) -> int:
        """获取最大可装备魔魂数量

        规则：30级起每10级可装备一个魔魂
        30-39级：3个；40-49级：4个；...；100级：10个
        """
        if self.beast_level < 30:
            return 0
        return self.beast_level // 10

    def get_used_slots(self) -> int:
        """获取已使用槽位数"""
        return len(self.equipped_souls)

    def get_free_slots(self) -> int:
        """获取剩余槽位数"""
        return max(0, self.get_max_slots() - self.get_used_slots())

    def can_equip(self) -> bool:
        """是否可以装备更多魔魂"""
        return self.get_free_slots() > 0

    def equip(self, soul: MoSoul) -> bool:
        """装备魔魂，返回是否成功（不检查冲突规则）"""
        if not self.can_equip():
            return False
        soul.beast_id = self.beast_id
        self.equipped_souls.append(soul)
        return True

    def unequip(self, soul_id: int) -> Optional[MoSoul]:
        """卸下魔魂，返回被卸下的魔魂"""
        for i, soul in enumerate(self.equipped_souls):
            if soul.id == soul_id:
                removed = self.equipped_souls.pop(i)
                removed.beast_id = None
                return removed
        return None

    def get_equipped_soul(self, soul_id: int) -> Optional[MoSoul]:
        """根据ID获取已装备的魔魂"""
        for soul in self.equipped_souls:
            if soul.id == soul_id:
                return soul
        return None

    def get_total_stat_bonus(self) -> Dict[str, Dict[str, float]]:
        """计算所有装备魔魂的总属性加成

        返回格式：
        {
            "hp": {"flat": 100, "percent": 5.0},
            "physical_attack": {"flat": 50, "percent": 10.0},
            ...
        }
        """
        result: Dict[str, Dict[str, float]] = {}

        for soul in self.equipped_souls:
            effects = soul.get_current_effects()
            for eff in effects:
                attr = eff["attr"]
                if attr not in result:
                    result[attr] = {"flat": 0, "percent": 0.0}
                result[attr]["flat"] += eff.get("flat", 0)
                result[attr]["percent"] += eff.get("percent", 0.0)

        return result

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "beast_id": self.beast_id,
            "beast_level": self.beast_level,
            "max_slots": self.get_max_slots(),
            "used_slots": self.get_used_slots(),
            "free_slots": self.get_free_slots(),
            "equipped_souls": [soul.to_dict() for soul in self.equipped_souls],
            "total_bonus": self.get_total_stat_bonus(),
        }


# ===================== 猎魂状态 =====================
@dataclass
class HuntingState:
    """玩家猎魂状态

    记录当前可点击的NPC、已解锁的NPC等信息。
    """

    user_id: int
    field_type: str = "normal"  # "normal" 或 "advanced"

    # 普通场状态
    normal_available_npcs: List[str] = field(default_factory=lambda: ["amy"])
    normal_current_npc: Optional[str] = None

    # 高级场状态
    advanced_available_npcs: List[str] = field(default_factory=lambda: ["walter_adv"])
    advanced_current_npc: Optional[str] = None

    # 累计消耗统计（新增）
    soul_charm_consumed: int = 0  # 个人累计消耗追魂法宝数量
    copper_consumed: int = 0      # 个人累计消耗铜钱数量

    def reset_normal_field(self):
        """重置普通场状态（只有艾米可点击）"""
        self.normal_available_npcs = ["amy"]
        self.normal_current_npc = None

    def reset_advanced_field(self):
        """重置高级场状态（只有沃特可点击）"""
        self.advanced_available_npcs = ["walter_adv"]
        self.advanced_current_npc = None

    def unlock_npc(self, npc_id: str):
        """解锁NPC"""
        if self.field_type == "normal":
            if npc_id not in self.normal_available_npcs:
                self.normal_available_npcs.append(npc_id)
        else:
            if npc_id not in self.advanced_available_npcs:
                self.advanced_available_npcs.append(npc_id)

    def consume_npc(self, npc_id: str):
        """消耗NPC（点击后从可用列表移除，艾米和沃特除外）"""
        if self.field_type == "normal":
            if npc_id != "amy" and npc_id in self.normal_available_npcs:
                self.normal_available_npcs.remove(npc_id)
        else:
            if npc_id != "walter_adv" and npc_id in self.advanced_available_npcs:
                self.advanced_available_npcs.remove(npc_id)

    def is_npc_available(self, npc_id: str) -> bool:
        """检查NPC是否可点击"""
        if self.field_type == "normal":
            return npc_id in self.normal_available_npcs
        else:
            return npc_id in self.advanced_available_npcs

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "field_type": self.field_type,
            "normal_available_npcs": list(self.normal_available_npcs),
            "advanced_available_npcs": list(self.advanced_available_npcs),
        }


# ===================== 全服猎魂保底计数 =====================
@dataclass
class GlobalPityCounter:
    """全服保底计数器（高级场凯文）

    全服累计点击凯文30000次必出一个龙魂，之后重置。
    """

    counter_key: str = "kevin_adv_pity"
    count: int = 0
    pity_threshold: int = 40000
    soul_charm_consumed_global: int = 0  # 全服累计消耗追魂法宝数量

    def increment(self, amount: int = 1) -> bool:
        """增加计数，返回是否触发保底"""
        self.count += amount
        if self.count >= self.pity_threshold:
            self.count -= self.pity_threshold  # 溢出处理，或者直接设为0
            return True
        return False

    def add_soul_charm_global(self, amount: int) -> bool:
        """增加全服追魂法宝消耗计数，返回是否触发保底"""
        self.soul_charm_consumed_global += amount
        if self.soul_charm_consumed_global >= self.pity_threshold:
            self.soul_charm_consumed_global -= self.pity_threshold
            return True
        return False

    def get_remaining(self) -> int:
        """获取距离保底还需多少次"""
        return self.pity_threshold - self.count

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "counter_key": self.counter_key,
            "count": self.count,
            "pity_threshold": self.pity_threshold,
            "remaining": self.get_remaining(),
        }
