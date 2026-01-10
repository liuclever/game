"""化仙系统配置加载器（configs/immortalize.json）"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json


class ImmortalizeConfig:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "immortalize.json"
        with path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    # ===================== 化仙丹 =====================
    def get_dan_exp(self, level: int) -> int:
        for item in self._config.get("dan_exp", []):
            if item.get("level") == level:
                return int(item.get("exp", 0) or 0)
        return 0

    def get_all_dan_exp(self) -> List[Dict[str, Any]]:
        return list(self._config.get("dan_exp", []) or [])

    # ===================== 化仙池 =====================
    def get_pool_capacity(self, level: int) -> int:
        pool_map = self._config.get("pool_capacity", {}) or {}
        return int(pool_map.get(str(level), 0) or 0)

    def get_pool_max_level(self) -> int:
        pool_map = self._config.get("pool_capacity", {}) or {}
        levels = [int(k) for k in pool_map.keys() if str(k).isdigit()]
        return max(levels) if levels else 0

    def get_all_pool_capacity(self) -> Dict[str, int]:
        return dict(self._config.get("pool_capacity", {}) or {})

    # ===================== 化仙阵 =====================
    def get_formation_duration_hours(self) -> int:
        formation = self._config.get("formation", {}) or {}
        return int(formation.get("duration_hours", 4) or 4)

    def get_formation_hourly_exp(self, level: int) -> int:
        formation = self._config.get("formation", {}) or {}
        hourly_map = formation.get("hourly_exp", {}) or {}
        return int(hourly_map.get(str(level), 0) or 0)

    def get_all_formation_hourly_exp(self) -> Dict[str, int]:
        formation = self._config.get("formation", {}) or {}
        return dict(formation.get("hourly_exp", {}) or {})

    # ===================== 幻兽化仙比例 =====================
    def get_beast_ratio(self, pool_level: int) -> float:
        ratio_map = self._config.get("beast_ratio", {}) or {}
        return float(ratio_map.get(str(pool_level), 0))

    def get_all_beast_ratio(self) -> Dict[str, float]:
        return dict(self._config.get("beast_ratio", {}) or {})

    # ===================== 化仙池升级 =====================
    def get_pool_upgrade_requirement(self, from_level: int) -> Optional[Dict[str, Any]]:
        for req in self._config.get("pool_upgrade", []) or []:
            if req.get("from_level") == from_level:
                return req
        return None

    def get_all_pool_upgrade_requirements(self) -> List[Dict[str, Any]]:
        return list(self._config.get("pool_upgrade", []) or [])
