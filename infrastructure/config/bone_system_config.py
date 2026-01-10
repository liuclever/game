"""战骨系统配置加载器"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class BoneSystemConfig:
    """从 configs/bone_system.json 加载战骨系统配置"""

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "bone_system.json"
        with path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    # ===================== 槽位 =====================
    def get_slots(self) -> List[str]:
        """获取所有槽位列表"""
        return self._config.get("slots", [])

    # ===================== 阶段配置 =====================
    def get_stages(self) -> List[Dict]:
        """获取所有阶段配置"""
        return self._config.get("stages", [])

    def get_stage_config(self, stage: int) -> Optional[Dict]:
        """获取指定阶段的配置"""
        for s in self.get_stages():
            if s["stage"] == stage:
                return s
        return None

    def get_stage_by_level(self, level: int) -> Optional[Dict]:
        """根据等级获取所属阶段配置"""
        for s in self.get_stages():
            if s["min_level"] <= level <= s["max_level"]:
                return s
        return None

    # ===================== 升级消耗 =====================
    def get_upgrade_rules(self) -> Dict:
        """获取升级规则配置"""
        return self._config.get("upgrade_rules", {})

    def get_upgrade_cost(self, from_level: int) -> Dict:
        """
        计算从 from_level 升到 from_level+1 的消耗
        返回: {"strengthen_stone": 数量, "gold": 铜钱}
        """
        rules = self.get_upgrade_rules()
        stone_item_id = rules.get("strengthen_stone_item_id", 9001)
        stone_per_level = rules.get("strengthen_stone_qty_per_from_level", 5)
        gold_map = rules.get("gold_cost_by_from_level", {})

        stone_qty = from_level * stone_per_level
        gold_cost = gold_map.get(str(from_level), 30 + from_level * 5)

        return {
            "strengthen_stone_item_id": stone_item_id,
            "strengthen_stone_qty": stone_qty,
            "gold": gold_cost,
        }

    def get_max_level(self) -> int:
        """获取战骨最大等级"""
        return self.get_upgrade_rules().get("max_level", 100)

    # ===================== 进阶/炼制消耗 =====================
    def get_refine_costs_config(self) -> Dict:
        """获取进阶消耗配置"""
        return self._config.get("refine_costs", {})

    def get_refine_cost(self, to_stage: int, slot: str) -> Optional[Dict]:
        """
        计算进阶到 to_stage 的消耗
        返回: {"scroll_item_id": x, "bone_soul_item_id": x, "bone_soul_qty": n,
               "primary_crystal_item_id": x, "primary_crystal_qty": n,
               "secondary_crystal_item_id": x, "secondary_crystal_qty": n}
        """
        if to_stage < 2 or to_stage > 10:
            return None

        refine_cfg = self.get_refine_costs_config()
        scroll_map = self._config.get("scroll_item_ids_by_stage", {})
        bone_soul_map = self._config.get("bone_soul_item_id_by_stage", {})

        # 卷轴
        stage_scrolls = scroll_map.get(str(to_stage), {})
        scroll_item_id = stage_scrolls.get(slot, 0)

        # 骨魂
        bone_soul_item_id = bone_soul_map.get(str(to_stage), 0)
        bone_soul_qty_map = refine_cfg.get("bone_soul_qty_by_stage", {})
        bone_soul_qty = bone_soul_qty_map.get(str(to_stage), to_stage - 1)

        # 结晶
        crystal_qty_map = refine_cfg.get("crystal_qty_by_stage", {})
        crystal_qty = crystal_qty_map.get(str(to_stage), {"primary": 6, "secondary": 3})
        slot_crystal_pairs = refine_cfg.get("slot_crystal_pairs", {})
        crystal_pair = slot_crystal_pairs.get(slot, {})

        return {
            "scroll_item_id": scroll_item_id,
            "scroll_qty": 1,
            "bone_soul_item_id": bone_soul_item_id,
            "bone_soul_qty": bone_soul_qty,
            "primary_crystal_item_id": crystal_pair.get("primary_item_id", 0),
            "primary_crystal_qty": crystal_qty.get("primary", 6),
            "secondary_crystal_item_id": crystal_pair.get("secondary_item_id", 0),
            "secondary_crystal_qty": crystal_qty.get("secondary", 3),
        }

    # ===================== 属性计算 =====================
    def get_stat_rules(self) -> Dict:
        """获取属性规则配置"""
        return self._config.get("stat_rules", {})

    def calc_bone_stats(self, stage: int, slot: str, level: int) -> Dict[str, int]:
        """
        根据阶段、槽位、等级计算战骨属性
        返回: {"hp": x, "physical_attack": x, "magic_attack": x,
               "physical_defense": x, "magic_defense": x, "speed": x}
        """
        stat_rules = self.get_stat_rules()
        stage_rules = stat_rules.get(str(stage), {})
        slot_rules = stage_rules.get(slot, {})

        if not slot_rules:
            return {
                "hp": 0,
                "physical_attack": 0,
                "magic_attack": 0,
                "physical_defense": 0,
                "magic_defense": 0,
                "speed": 0,
            }

        base = slot_rules.get("base", {})
        per_level = slot_rules.get("per_level_add", {})
        base_level = slot_rules.get("base_level", 1)

        level_diff = level - base_level

        return {
            "hp": base.get("hp", 0) + per_level.get("hp", 0) * level_diff,
            "physical_attack": base.get("physical_attack", 0)
            + per_level.get("physical_attack", 0) * level_diff,
            "magic_attack": base.get("magic_attack", 0)
            + per_level.get("magic_attack", 0) * level_diff,
            "physical_defense": base.get("physical_defense", 0)
            + per_level.get("physical_defense", 0) * level_diff,
            "magic_defense": base.get("magic_defense", 0)
            + per_level.get("magic_defense", 0) * level_diff,
            "speed": base.get("speed", 0) + per_level.get("speed", 0) * level_diff,
        }


# 全局单例
_bone_system_config: Optional[BoneSystemConfig] = None


def get_bone_system_config() -> BoneSystemConfig:
    """获取战骨系统配置单例"""
    global _bone_system_config
    if _bone_system_config is None:
        _bone_system_config = BoneSystemConfig()
    return _bone_system_config
