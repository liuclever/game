"""战灵系统配置加载器（configs/spirit_system.json）"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json


class SpiritSystemConfig:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "spirit_system.json"
        with path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    # ===================== 基础 =====================
    def get_warehouse_capacity(self) -> int:
        return int(self._config.get("warehouse_capacity", 100) or 100)

    def get_elements(self) -> List[Dict[str, str]]:
        return list(self._config.get("elements", []) or [])

    def get_element_name(self, element_key: str) -> str:
        for e in self.get_elements():
            if e.get("key") == element_key:
                return str(e.get("name") or "")
        return ""

    def is_valid_element(self, element_key: str) -> bool:
        return any(e.get("key") == element_key for e in self.get_elements())

    def get_default_unlocked_elements(self) -> List[str]:
        return list(self._config.get("default_unlocked_elements", []) or [])

    # ===================== 解锁规则 =====================
    def get_unlock_requirement(self, element_key: str) -> Optional[Dict[str, Any]]:
        mp = self._config.get("unlock_requirements_by_element", {}) or {}
        req = mp.get(element_key)
        return req if isinstance(req, dict) else None

    # ===================== 物品 =====================
    def get_spirit_key_item_id(self) -> int:
        items = self._config.get("items", {}) or {}
        return int(items.get("spirit_key_item_id", 0) or 0)

    def get_unopened_stone_item_id(self, element_key: str) -> int:
        items = self._config.get("items", {}) or {}
        mp = items.get("unopened_stone_item_ids_by_element", {}) or {}
        return int(mp.get(element_key, 0) or 0)

    # ===================== 开启灵石（随机生成） =====================
    def get_race_weights(self, element_key: str = "earth") -> Dict[str, int]:
        """ 获取指定元素的种族权重 """
        rules = self._config.get("open_stone_rules", {}) or {}
        weights_by_element = rules.get("race_weights_by_element", {}) or {}
        weights = weights_by_element.get(element_key, weights_by_element.get("earth", {})) or {}
        return {str(k): int(v) for k, v in weights.items()}

    def get_line_count(self) -> int:
        rules = self._config.get("open_stone_rules", {}) or {}
        return int(rules.get("line_count", 3) or 3)

    def get_initial_unlocked_lines(self) -> int:
        rules = self._config.get("open_stone_rules", {}) or {}
        return int(rules.get("initial_unlocked_lines", 1) or 1)

    def get_attr_pool(self) -> List[Dict[str, Any]]:
        rules = self._config.get("open_stone_rules", {}) or {}
        return list(rules.get("attr_pool", []) or [])

    def get_value_range_bp(self, element_key: str, attr_key: str = "") -> Tuple[int, int]:
        """ 获取指定元素的属性值范围 (basis points) """
        rules = self._config.get("open_stone_rules", {}) or {}
        ranges = rules.get("value_ranges_bp_by_element", {}) or {}
        r = ranges.get(element_key, {}) or {}
        mn = int(r.get("min", 0) or 0)
        mx = int(r.get("max", 0) or 0)
        if mx < mn:
            mx = mn
        return mn, mx

    def get_quality_tiers(self, element_key: str = "earth") -> List[Dict[str, Any]]:
        """ 获取指定元素的品质等级配置 """
        rules = self._config.get("open_stone_rules", {}) or {}
        tiers_by_element = rules.get("quality_tiers_by_element", {}) or {}
        return list(tiers_by_element.get(element_key, []) or [])

    def get_quality_name(self, element_key: str, value_bp: int) -> str:
        """ 根据元素和属性值获取品质名称 """
        tiers = self.get_quality_tiers(element_key)
        for tier in tiers:
            if tier.get("min", 0) <= value_bp < tier.get("max", 0):
                return tier.get("name", "普通")
        # 如果值等于最大值，返回最高品质
        if tiers and value_bp >= tiers[-1].get("min", 0):
            return tiers[-1].get("name", "传奇")
        return "普通"

    # ===================== 词条解锁 =====================
    def get_line_unlock_cost(self, line_index: int) -> Optional[Dict[str, Any]]:
        mp = self._config.get("line_unlock_costs", {}) or {}
        cost = mp.get(str(line_index))
        return cost if isinstance(cost, dict) else None

    # ===================== 洗练 =====================
    def get_refine_cost_by_element_and_locked(self, element_key: str, locked_count: int) -> int:
        """ 根据元素和锁定词条数获取洗练消耗 """
        rules = self._config.get("refine_rules", {}) or {}
        mp = rules.get("spirit_power_cost_by_element_and_locked", {}) or {}
        element_costs = mp.get(element_key, mp.get("earth", {})) or {}
        return int(element_costs.get(str(locked_count), element_costs.get("0", 1)) or 1)

    def get_vip_free_refines_per_day(self, vip: int) -> int:
        rules = self._config.get("refine_rules", {}) or {}
        mp = rules.get("vip_free_refines_per_day", {}) or {}
        return int(mp.get(str(vip), mp.get("0", 0)) or 0)

    # ===================== 出售回收 =====================
    def get_sell_spirit_power(self, element_key: str) -> int:
        mp = self._config.get("sell_spirit_power_by_element", {}) or {}
        return int(mp.get(element_key, 0) or 0)


_spirit_system_config: Optional[SpiritSystemConfig] = None


def get_spirit_system_config() -> SpiritSystemConfig:
    global _spirit_system_config
    if _spirit_system_config is None:
        _spirit_system_config = SpiritSystemConfig()
    return _spirit_system_config
