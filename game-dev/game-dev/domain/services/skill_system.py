"""技能系统模块

实现幻兽技能的判定、触发和效果计算。

技能分类：
1. 主动技能：攻击时触发，替代普攻，每回合最多触发1个
2. 被动技能：被攻击时触发，每回合最多触发1个
3. 增益技能：永久生效，加成裸属性
4. 负面技能：永久生效，减少裸属性
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.services.pvp_battle_engine import PvpBeast


# 加载技能配置
_SKILL_CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "skills.json"
_SKILL_CONFIG: Dict = {}


def _load_skill_config() -> Dict:
    """加载技能配置文件"""
    global _SKILL_CONFIG
    if not _SKILL_CONFIG:
        with open(_SKILL_CONFIG_PATH, "r", encoding="utf-8") as f:
            _SKILL_CONFIG = json.load(f)
    return _SKILL_CONFIG


def get_skill_config() -> Dict:
    """获取技能配置"""
    return _load_skill_config()


@dataclass
class SkillEffect:
    """技能效果"""
    effect_type: str  # poison, physical_defense_down, magic_defense_down, speed_down, etc.
    value: float      # 效果数值（百分比）
    duration: int     # 持续回合数（0表示即时效果）
    source_skill: str = ""  # 来源技能名


@dataclass
class SkillTriggerResult:
    """技能触发结果"""
    triggered: bool = False
    skill_name: str = ""
    damage_multiplier: float = 1.0
    effects: List[SkillEffect] = field(default_factory=list)
    is_critical: bool = False  # 是否是必杀类技能
    lifesteal_ratio: float = 0.0  # 吸血比例


@dataclass
class PassiveSkillResult:
    """被动技能触发结果"""
    triggered: bool = False
    skill_name: str = ""
    effect_type: str = ""  # dodge, reflect, counter
    effect_value: float = 0.0  # 反震/反击比例


def get_skill_info(skill_name: str) -> Optional[Dict]:
    """获取技能详细信息"""
    config = get_skill_config()
    
    # 搜索主动技能
    for tier in ["advanced", "normal"]:
        if skill_name in config["active_skills"].get(tier, {}):
            info = config["active_skills"][tier][skill_name].copy()
            info["category"] = "active"
            info["tier"] = tier
            return info
    
    # 搜索被动技能
    for tier in ["advanced", "normal"]:
        if skill_name in config["passive_skills"].get(tier, {}):
            info = config["passive_skills"][tier][skill_name].copy()
            info["category"] = "passive"
            info["tier"] = tier
            return info
    
    # 搜索增益技能
    for tier in ["advanced", "normal"]:
        if skill_name in config["buff_skills"].get(tier, {}):
            info = config["buff_skills"][tier][skill_name].copy()
            info["category"] = "buff"
            info["tier"] = tier
            return info
    
    # 搜索负面技能
    if skill_name in config["debuff_skills"]:
        info = config["debuff_skills"][skill_name].copy()
        info["category"] = "debuff"
        return info
    
    return None


def classify_skills(skills: List[str]) -> Dict[str, List[str]]:
    """将技能列表分类"""
    result = {
        "active": [],
        "passive": [],
        "buff": [],
        "debuff": [],
    }
    
    for skill_name in skills:
        info = get_skill_info(skill_name)
        if info:
            category = info.get("category", "")
            if category in result:
                result[category].append(skill_name)
    
    return result


def apply_buff_debuff_skills(
    skills: List[str],
    attack_type: str,
    raw_hp: int,
    raw_physical_attack: int,
    raw_magic_attack: int,
    raw_physical_defense: int,
    raw_magic_defense: int,
    raw_speed: int,
) -> Tuple[int, int, int, int, int, int, Dict]:
    """
    应用增益和负面技能到裸属性，返回最终属性和特殊效果标记
    
    Args:
        skills: 技能列表
        attack_type: 攻击类型 "physical" 或 "magic"
        raw_xxx: 裸属性值
    
    Returns:
        (hp, physical_attack, magic_attack, physical_defense, magic_defense, speed, special_effects)
    """
    config = get_skill_config()
    
    # 属性修正系数（累加）
    modifiers = {
        "hp": 0.0,
        "physical_attack": 0.0,
        "magic_attack": 0.0,
        "physical_defense": 0.0,
        "magic_defense": 0.0,
        "speed": 0.0,
    }
    
    # 特殊效果
    special_effects = {
        "poison_enhance": 0.0,      # 毒攻强化
        "critical_resist": 0.0,      # 必杀抗性
        "immune_counter": False,     # 免疫反击/反震
        "poison_resist": 0.0,        # 毒抗
    }
    
    for skill_name in skills:
        # 检查增益技能
        for tier in ["advanced", "normal"]:
            if skill_name in config["buff_skills"].get(tier, {}):
                buff = config["buff_skills"][tier][skill_name]
                if "stat" in buff:
                    stat = buff["stat"]
                    if stat in modifiers:
                        modifiers[stat] += buff["modifier"]
                elif "special" in buff:
                    special = buff["special"]
                    if special in special_effects:
                        if isinstance(special_effects[special], bool):
                            special_effects[special] = buff["value"]
                        else:
                            special_effects[special] += buff["value"]
        
        # 检查负面技能
        if skill_name in config["debuff_skills"]:
            debuff = config["debuff_skills"][skill_name]
            stat = debuff["stat"]
            if stat == "attack":
                # 根据攻击类型决定减哪个
                if attack_type == "magic":
                    modifiers["magic_attack"] += debuff["modifier"]
                else:
                    modifiers["physical_attack"] += debuff["modifier"]
            elif stat in modifiers:
                modifiers[stat] += debuff["modifier"]
    
    # 计算最终属性
    final_hp = int(raw_hp * (1 + modifiers["hp"]))
    final_physical_attack = int(raw_physical_attack * (1 + modifiers["physical_attack"]))
    final_magic_attack = int(raw_magic_attack * (1 + modifiers["magic_attack"]))
    final_physical_defense = int(raw_physical_defense * (1 + modifiers["physical_defense"]))
    final_magic_defense = int(raw_magic_defense * (1 + modifiers["magic_defense"]))
    final_speed = int(raw_speed * (1 + modifiers["speed"]))
    
    return (
        final_hp,
        final_physical_attack,
        final_magic_attack,
        final_physical_defense,
        final_magic_defense,
        final_speed,
        special_effects,
    )


def try_trigger_active_skill(
    attacker_skills: List[str],
    attack_type: str,
    defender_critical_resist: float = 0.0,
    attacker_poison_enhance: float = 0.0,
) -> SkillTriggerResult:
    """
    尝试触发主动技能
    
    Args:
        attacker_skills: 攻击者的技能列表
        attack_type: 攻击者的攻击类型 "physical" 或 "magic"
        defender_critical_resist: 防御者的必杀抗性（减少必杀触发概率）
        attacker_poison_enhance: 攻击者的毒攻强化（增加毒攻触发概率）
    
    Returns:
        SkillTriggerResult
    """
    config = get_skill_config()
    
    # 收集所有主动技能
    active_skills = []
    for skill_name in attacker_skills:
        for tier in ["advanced", "normal"]:
            if skill_name in config["active_skills"].get(tier, {}):
                skill_info = config["active_skills"][tier][skill_name]
                # 检查攻击类型限制
                skill_attack_type = skill_info.get("attack_type", "all")
                if skill_attack_type == "all" or skill_attack_type == attack_type:
                    active_skills.append((skill_name, skill_info))
    
    if not active_skills:
        return SkillTriggerResult()
    
    # 随机打乱顺序，依次判定
    random.shuffle(active_skills)
    
    for skill_name, skill_info in active_skills:
        trigger_rate = skill_info["trigger_rate"]
        
        # 毒攻强化
        if "毒攻" in skill_name and attacker_poison_enhance > 0:
            trigger_rate += attacker_poison_enhance
        
        # 必杀类技能受幸运影响
        is_critical = skill_info.get("is_critical", False)
        if is_critical and defender_critical_resist > 0:
            trigger_rate *= (1 - defender_critical_resist)
        
        # 判定是否触发
        if random.random() < trigger_rate:
            # 解析技能效果
            effects = []
            lifesteal_ratio = 0.0
            
            for eff in skill_info.get("effects", []):
                if eff["type"] == "lifesteal":
                    lifesteal_ratio = eff["value"]
                else:
                    effects.append(SkillEffect(
                        effect_type=eff["type"],
                        value=eff["value"],
                        duration=eff.get("duration", 0),
                        source_skill=skill_name,
                    ))
            
            return SkillTriggerResult(
                triggered=True,
                skill_name=skill_name,
                damage_multiplier=skill_info["damage_multiplier"],
                effects=effects,
                is_critical=is_critical,
                lifesteal_ratio=lifesteal_ratio,
            )
    
    return SkillTriggerResult()


def try_trigger_passive_skill(
    defender_skills: List[str],
    is_normal_attack: bool,
    attacker_immune_counter: bool = False,
) -> PassiveSkillResult:
    """
    尝试触发被动技能
    
    Args:
        defender_skills: 防御者的技能列表
        is_normal_attack: 是否是普通攻击（闪避只对普攻有效）
        attacker_immune_counter: 攻击者是否免疫反击/反震
    
    Returns:
        PassiveSkillResult
    """
    config = get_skill_config()
    
    # 收集所有被动技能
    passive_skills = []
    for skill_name in defender_skills:
        for tier in ["advanced", "normal"]:
            if skill_name in config["passive_skills"].get(tier, {}):
                skill_info = config["passive_skills"][tier][skill_name]
                passive_skills.append((skill_name, skill_info))
    
    if not passive_skills:
        return PassiveSkillResult()
    
    # 随机打乱顺序，依次判定（每回合只能触发一个）
    random.shuffle(passive_skills)
    
    for skill_name, skill_info in passive_skills:
        effect_type = skill_info["effect_type"]
        
        # 闪避只对普攻有效
        if effect_type == "dodge" and not is_normal_attack:
            continue
        
        # 反击/反震受偷袭技能影响
        if effect_type in ("reflect", "counter") and attacker_immune_counter:
            continue
        
        trigger_rate = skill_info["trigger_rate"]
        
        # 判定是否触发
        if random.random() < trigger_rate:
            effect_value = 0.0
            if effect_type == "reflect":
                effect_value = skill_info.get("reflect_ratio", 0.44)
            elif effect_type == "counter":
                effect_value = skill_info.get("counter_ratio", 0.75)
            
            return PassiveSkillResult(
                triggered=True,
                skill_name=skill_name,
                effect_type=effect_type,
                effect_value=effect_value,
            )
    
    return PassiveSkillResult()


def check_poison_resist(defender_skills: List[str]) -> bool:
    """
    检查是否免疫毒攻（抗性增强技能50%概率免疫）
    
    Returns:
        True 表示免疫，不会中毒
    """
    config = get_skill_config()
    
    for skill_name in defender_skills:
        for tier in ["advanced", "normal"]:
            if skill_name in config["buff_skills"].get(tier, {}):
                buff = config["buff_skills"][tier][skill_name]
                if buff.get("special") == "poison_resist":
                    resist_rate = buff["value"]
                    if random.random() < resist_rate:
                        return True
    
    return False
