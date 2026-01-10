from typing import Optional, Dict, List
from pathlib import Path
import json

from domain.entities.bone import (
    BoneTemplate,
    MaterialCost,
    BoneUpgradeCost,
    BoneAdvanceCost,
)
from domain.repositories.bone_repo import IBoneTemplateRepo


class ConfigBoneTemplateRepo(IBoneTemplateRepo):
    """从 configs/bone_templates.json 读取战骨模板"""

    def __init__(self):
        self._templates: Dict[int, BoneTemplate] = {}
        self._load()

    @staticmethod
    def _parse_materials(raw_materials) -> List[MaterialCost]:
        if not isinstance(raw_materials, list):
            return []
        materials: List[MaterialCost] = []
        for m in raw_materials:
            if not isinstance(m, dict):
                continue
            try:
                item_id = int(m.get("item_id", 0))
                qty = int(m.get("quantity", 0))
            except (TypeError, ValueError):
                continue
            if item_id <= 0 or qty <= 0:
                continue
            materials.append(MaterialCost(item_id=item_id, quantity=qty))
        return materials

    def _load(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "bone_templates.json"
        with path.open("r", encoding="utf-8") as f:
            raw_list = json.load(f)

        for item in raw_list:
            template_id = int(item["id"])

            # 升级消耗（可选）
            upgrade_costs: List[BoneUpgradeCost] = []
            raw_upgrade_costs = item.get("upgrade_costs", [])
            if isinstance(raw_upgrade_costs, list):
                for c in raw_upgrade_costs:
                    if not isinstance(c, dict):
                        continue
                    try:
                        to_level = int(c.get("to_level", 0))
                    except (TypeError, ValueError):
                        continue
                    if to_level <= 1:
                        continue
                    mats = self._parse_materials(c.get("materials", []))
                    upgrade_costs.append(BoneUpgradeCost(to_level=to_level, materials=mats))

            # 进阶消耗（可选）
            advance_costs: List[BoneAdvanceCost] = []
            raw_advance_costs = item.get("advance_costs", [])
            if isinstance(raw_advance_costs, list):
                for c in raw_advance_costs:
                    if not isinstance(c, dict):
                        continue
                    try:
                        to_stage = int(c.get("to_stage", 0))
                    except (TypeError, ValueError):
                        continue
                    if to_stage <= 1:
                        continue
                    mats = self._parse_materials(c.get("materials", []))
                    advance_costs.append(BoneAdvanceCost(to_stage=to_stage, materials=mats))

            self._templates[template_id] = BoneTemplate(
                id=template_id,
                name=item.get("name", ""),
                description=item.get("description", ""),
                slot=item.get("slot", ""),
                max_level=int(item.get("max_level", 1) or 1),
                max_stage=int(item.get("max_stage", 1) or 1),
                hp_flat=int(item.get("hp_flat", 0) or 0),
                attack_flat=int(item.get("attack_flat", 0) or 0),
                physical_defense_flat=int(item.get("physical_defense_flat", 0) or 0),
                magic_defense_flat=int(item.get("magic_defense_flat", 0) or 0),
                speed_flat=int(item.get("speed_flat", 0) or 0),
                upgrade_costs=upgrade_costs,
                advance_costs=advance_costs,
            )

    def get_by_id(self, template_id: int) -> Optional[BoneTemplate]:
        return self._templates.get(template_id)

    def get_all(self) -> Dict[int, BoneTemplate]:
        return self._templates.copy()
