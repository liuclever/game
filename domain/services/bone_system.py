from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional
import json


_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def _load_bone_system_config() -> Dict[str, Any]:
    """加载 configs/bone_system.json（进程内缓存）。"""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "bone_system.json"
    with path.open("r", encoding="utf-8") as f:
        _CONFIG_CACHE = json.load(f)
    return _CONFIG_CACHE


@dataclass
class BoneBonus:
    """战骨对幻兽的固定属性加成（当前版本只做固定值）。"""

    hp_flat: int = 0
    attack_flat: int = 0
    physical_defense_flat: int = 0
    magic_defense_flat: int = 0
    speed_flat: int = 0


def calc_bone_bonus(stage: int, slot: str, level: int) -> BoneBonus:
    """根据阶段(stage)、槽位(slot)、等级(level)计算战骨固定加成。

    数据来源：configs/bone_system.json -> stat_rules

    规则：
    bonus = base + (level - base_level) * per_level_add

    注意：配置里攻击以 physical_attack / magic_attack 表示。
    当前战骨系统只有“攻击”一项，因此取两者的最大值作为 attack_flat（文档中一般两者相等）。
    """
    if stage <= 0:
        raise ValueError("invalid_stage")
    if not slot:
        raise ValueError("invalid_slot")
    if level <= 0:
        raise ValueError("invalid_level")

    config = _load_bone_system_config()

    # 校验等级范围（按阶段配置）
    stages = config.get("stages", [])
    stage_cfg = None
    if isinstance(stages, list):
        for s in stages:
            if isinstance(s, dict) and int(s.get("stage", 0)) == stage:
                stage_cfg = s
                break
    if stage_cfg is None:
        raise ValueError("stage_not_configured")

    min_level = int(stage_cfg.get("min_level", 1) or 1)
    max_level = int(stage_cfg.get("max_level", min_level) or min_level)
    if level < min_level or level > max_level:
        raise ValueError("level_out_of_stage_range")

    stat_rules = config.get("stat_rules", {})
    rule_stage = stat_rules.get(str(stage)) if isinstance(stat_rules, dict) else None
    if not isinstance(rule_stage, dict):
        raise ValueError("stat_rule_stage_not_found")

    rule = rule_stage.get(slot)
    if not isinstance(rule, dict):
        raise ValueError("stat_rule_slot_not_found")

    base_level = int(rule.get("base_level", min_level) or min_level)
    if level < base_level:
        raise ValueError("level_below_base_level")

    base = rule.get("base", {})
    per = rule.get("per_level_add", {})
    if not isinstance(base, dict) or not isinstance(per, dict):
        raise ValueError("stat_rule_invalid")

    delta = level - base_level

    hp = int(base.get("hp", 0) or 0) + delta * int(per.get("hp", 0) or 0)
    phys_atk = int(base.get("physical_attack", 0) or 0) + delta * int(per.get("physical_attack", 0) or 0)
    magic_atk = int(base.get("magic_attack", 0) or 0) + delta * int(per.get("magic_attack", 0) or 0)
    physical_def = int(base.get("physical_defense", 0) or 0) + delta * int(per.get("physical_defense", 0) or 0)
    magic_def = int(base.get("magic_defense", 0) or 0) + delta * int(per.get("magic_defense", 0) or 0)
    speed = int(base.get("speed", 0) or 0) + delta * int(per.get("speed", 0) or 0)

    return BoneBonus(
        hp_flat=hp,
        attack_flat=max(phys_atk, magic_atk),
        physical_defense_flat=physical_def,
        magic_defense_flat=magic_def,
        speed_flat=speed,
    )
