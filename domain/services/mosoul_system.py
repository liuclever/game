"""魔魂系统服务。

提供魔魂猎取、升级、装备等核心功能。
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

from domain.entities.mosoul import (
    MoSoul,
    MoSoulGrade,
    MoSoulTemplate,
    SoulStorage,
    BeastMoSoulSlot,
    HuntingState,
    GlobalPityCounter,
    get_mosoul_template,
    get_templates_by_grade,
)
from domain.rules.mosoul_rules import validate_equip, check_equip_conflict
from domain.services.beast_stats import StatBonus


# ===================== 配置加载 =====================
_hunting_config_cache: Optional[Dict] = None


def _load_hunting_config() -> Dict:
    """加载猎魂配置"""
    global _hunting_config_cache
    if _hunting_config_cache is not None:
        return _hunting_config_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "mosoul_hunting.json"
    if not path.exists():
        _hunting_config_cache = {}
        return _hunting_config_cache

    try:
        with path.open("r", encoding="utf-8") as f:
            _hunting_config_cache = json.load(f)
    except Exception:
        _hunting_config_cache = {}

    return _hunting_config_cache


# ===================== 猎魂结果 =====================
@dataclass
class HuntingResult:
    """猎魂结果"""
    success: bool
    soul: Optional[MoSoul] = None
    is_waste: bool = False
    copper_gained: int = 0
    next_npc_unlocked: Optional[str] = None
    message: str = ""
    cost: int = 0
    cost_type: str = "copper"

    @staticmethod
    def failure(message: str) -> "HuntingResult":
        return HuntingResult(success=False, message=message)

    @staticmethod
    def waste_soul(copper: int) -> "HuntingResult":
        return HuntingResult(
            success=True,
            is_waste=True,
            copper_gained=copper,
            message=f"猎取到废魂，已自动售卖获得{copper}铜钱",
        )


# ===================== 猎魂服务 =====================
class MoSoulHuntingService:
    """猎魂服务

    实现普通场和高级场的猎魂逻辑。
    """

    def __init__(self):
        self.config = _load_hunting_config()

    def get_npc_info(self, npc_id: str, field_type: str = "normal") -> Optional[Dict]:
        """获取NPC信息"""
        field_key = "normal_field" if field_type == "normal" else "advanced_field"
        field_config = self.config.get(field_key, {})
        npcs = field_config.get("npcs", [])

        for npc in npcs:
            if npc.get("id") == npc_id:
                return npc
        return None

    def get_available_npcs(self, state: HuntingState) -> List[Dict]:
        """获取当前可点击的NPC列表"""
        field_type = state.field_type
        field_key = "normal_field" if field_type == "normal" else "advanced_field"
        field_config = self.config.get(field_key, {})
        all_npcs = field_config.get("npcs", [])

        available_ids = (
            state.normal_available_npcs
            if field_type == "normal"
            else state.advanced_available_npcs
        )

        return [npc for npc in all_npcs if npc.get("id") in available_ids]

    def _roll_soul_grade(self, drop_rates: Dict[str, float]) -> MoSoulGrade:
        """根据概率表随机抽取魔魂等级
        
        注：龙魂不再通过自然概率产生，仅通过保底规则产生
        """
        roll = random.random() * 100
        cumulative = 0

        # 过滤掉 dragon_soul 概率
        rates = {k: v for k, v in drop_rates.items() if k != "dragon_soul"}
        total_rate = sum(rates.values())
        
        if total_rate == 0:
            return MoSoulGrade.YELLOW_SOUL

        for grade_key, rate in rates.items():
            cumulative += (rate / total_rate) * 100
            if roll < cumulative:
                try:
                    return MoSoulGrade(grade_key)
                except ValueError:
                    continue

        # 默认返回黄魂
        return MoSoulGrade.YELLOW_SOUL

    def _roll_specific_soul(
        self, grade: MoSoulGrade, npc_config: Optional[Dict] = None
    ) -> int:
        """随机抽取指定等级的具体魔魂模板ID"""
        templates = get_templates_by_grade(grade)
        if not templates:
            return 0

        # 龙魂特殊处理：考虑单个龙魂概率
        if grade == MoSoulGrade.DRAGON_SOUL and npc_config:
            individual_rate = npc_config.get("dragon_soul_individual_rate", 0)
            if individual_rate > 0:
                # 根据单个概率随机选择
                dragon_templates = templates
                roll = random.random() * 100
                cumulative = 0
                for t in dragon_templates:
                    cumulative += individual_rate
                    if roll < cumulative:
                        return t.id
                # 如果没抽中，随机选一个
                return random.choice(dragon_templates).id

        return random.choice(templates).id

    def hunt(
        self,
        user_id: int,
        state: HuntingState,
        npc_id: str,
        storage: SoulStorage,
        pity_counter: Optional[GlobalPityCounter] = None,
    ) -> Tuple[HuntingResult, HuntingState]:
        """执行猎魂

        Args:
            user_id: 玩家ID
            state: 玩家猎魂状态
            npc_id: 点击的NPC ID
            storage: 玩家储魂器
            pity_counter: 全服保底计数器（高级场凯文用）

        Returns:
            (猎魂结果, 更新后的状态)
        """
        # 检查NPC是否可点击
        if not state.is_npc_available(npc_id):
            return HuntingResult.failure(f"NPC[{npc_id}]当前不可点击"), state

        # 获取NPC配置
        npc_config = self.get_npc_info(npc_id, state.field_type)
        if not npc_config:
            return HuntingResult.failure(f"NPC[{npc_id}]不存在"), state

        cost = npc_config.get("cost", 0)
        cost_type = npc_config.get("cost_type", "copper")
        drop_rates = npc_config.get("drop_rates", {})

        # --- 龙魂保底逻辑开始 ---
        triggered_pity_msg = ""
        is_dragon_pity = False

        # 1. 个人铜钱消耗保底 (10亿)
        if cost_type == "copper":
            state.copper_consumed += cost
            if state.copper_consumed >= 1000000000:
                state.copper_consumed -= 1000000000
                is_dragon_pity = True
                triggered_pity_msg = "（触发个人铜钱消耗保底）"

        # 2. 高级场追魂法宝保底
        if state.field_type == "advanced" and cost_type == "soul_charm":
            # 个人消耗保底 (4000)
            state.soul_charm_consumed += cost
            if state.soul_charm_consumed >= 4000:
                state.soul_charm_consumed -= 4000
                is_dragon_pity = True
                triggered_pity_msg = "（触发个人追魂法宝消耗保底）"

            # 全服消耗保底 (40000)
            if pity_counter:
                if pity_counter.add_soul_charm_global(cost):
                    is_dragon_pity = True
                    triggered_pity_msg = "（触发全服追魂法宝消耗保底）"

        # 抽取魔魂等级
        if is_dragon_pity:
            grade = MoSoulGrade.DRAGON_SOUL
        else:
            grade = self._roll_soul_grade(drop_rates)
        
        # 抽取具体魔魂
        template_id = self._roll_specific_soul(grade, npc_config)

        # 处理废魂
        if grade == MoSoulGrade.WASTE_SOUL:
            sell_config = self.config.get("waste_soul_auto_sell", {})
            sell_price = sell_config.get("price", 5000)
            result = HuntingResult.waste_soul(sell_price)
            result.cost = cost
            result.cost_type = cost_type

            # 更新状态：消耗NPC，尝试解锁下一个
            state.consume_npc(npc_id)
            next_npc = npc_config.get("next_npc")
            next_chance = npc_config.get("next_npc_chance", 0)
            if next_npc and random.random() < next_chance:
                state.unlock_npc(next_npc)
                result.next_npc_unlocked = next_npc

            return result, state

        # 检查储魂器空间
        if storage.is_full():
            return HuntingResult.failure("储魂器已满，请先整理魔魂"), state

        # 创建魔魂实例
        soul = MoSoul(
            user_id=user_id,
            template_id=template_id,
            level=1,
            exp=0,
        )

        # 构建结果
        result = HuntingResult(
            success=True,
            soul=soul,
            cost=cost,
            cost_type=cost_type,
            message=f"猎取到{grade.chinese_name}：{soul.name}{triggered_pity_msg}",
        )

        # 更新状态
        state.consume_npc(npc_id)
        next_npc = npc_config.get("next_npc")
        next_chance = npc_config.get("next_npc_chance", 0)
        if next_npc and random.random() < next_chance:
            state.unlock_npc(next_npc)
            result.next_npc_unlocked = next_npc

        return result, state

    def get_hunting_cost(self, npc_id: str, field_type: str = "normal") -> Tuple[int, str]:
        """获取猎魂费用

        Returns:
            (费用, 货币类型)
        """
        npc_config = self.get_npc_info(npc_id, field_type)
        if not npc_config:
            return 0, "copper"
        return npc_config.get("cost", 0), npc_config.get("cost_type", "copper")


# ===================== 升级服务 =====================
class MoSoulUpgradeService:
    """魔魂升级服务

    通过吞噬其他魔魂获得经验来升级。
    """

    def upgrade(
        self,
        target: MoSoul,
        materials: List[MoSoul],
    ) -> Tuple[bool, int, int]:
        """升级魔魂

        Args:
            target: 要升级的目标魔魂
            materials: 作为材料的魔魂列表

        Returns:
            (是否升级, 获得的经验, 升级后的等级)
        """
        if not materials:
            return False, 0, target.level

        # 计算总经验
        total_exp = sum(m.get_exp_provide() for m in materials)

        # 目标魔魂加经验
        old_level = target.level
        leveled_up = target.add_exp(total_exp)

        return leveled_up, total_exp, target.level

    def calc_upgrade_preview(
        self,
        target: MoSoul,
        materials: List[MoSoul],
    ) -> Dict:
        """预览升级结果（不实际升级）

        Returns:
            预览信息字典
        """
        total_exp = sum(m.get_exp_provide() for m in materials)

        # 模拟升级
        current_level = target.level
        current_exp = target.exp
        remaining = total_exp

        while remaining > 0 and current_level < 10:
            required = target.exp_to_next_level()
            if required <= 0:
                break

            need = required - current_exp
            if remaining >= need:
                remaining -= need
                current_exp = 0
                current_level += 1
            else:
                current_exp += remaining
                remaining = 0

        return {
            "before_level": target.level,
            "before_exp": target.exp,
            "after_level": current_level,
            "after_exp": current_exp,
            "exp_gained": total_exp,
            "level_up_count": current_level - target.level,
            "material_count": len(materials),
        }


# ===================== 装备服务 =====================
class MoSoulEquipService:
    """魔魂装备服务

    处理魔魂装备到幻兽的逻辑。
    """

    def equip(
        self,
        soul: MoSoul,
        slot: BeastMoSoulSlot,
    ) -> Tuple[bool, str]:
        """装备魔魂到幻兽

        Args:
            soul: 要装备的魔魂
            slot: 幻兽魔魂槽位

        Returns:
            (是否成功, 消息)
        """
        # 检查魔魂是否已装备
        if soul.is_equipped():
            return False, "该魔魂已装备在其他幻兽上"

        # 完整校验
        can_equip, msg = validate_equip(soul, slot)
        if not can_equip:
            return False, msg

        # 执行装备
        slot.equip(soul)
        return True, f"成功装备魔魂[{soul.name}]"

    def unequip(
        self,
        soul_id: int,
        slot: BeastMoSoulSlot,
        storage: SoulStorage,
    ) -> Tuple[bool, str]:
        """从幻兽卸下魔魂

        Args:
            soul_id: 魔魂ID
            slot: 幻兽魔魂槽位
            storage: 储魂器（卸下的魔魂放入储魂器）

        Returns:
            (是否成功, 消息)
        """
        # 检查储魂器空间
        if storage.is_full():
            return False, "储魂器已满，无法卸下魔魂"

        # 执行卸下
        soul = slot.unequip(soul_id)
        if not soul:
            return False, "未找到该魔魂"

        # 放入储魂器
        storage.add_soul(soul)
        return True, f"成功卸下魔魂[{soul.name}]"

    def get_equip_preview(
        self,
        soul: MoSoul,
        slot: BeastMoSoulSlot,
    ) -> Dict:
        """预览装备效果

        Returns:
            预览信息字典
        """
        can_equip, msg = validate_equip(soul, slot)

        # 计算装备后的总加成
        current_bonus = slot.get_total_stat_bonus()
        soul_effects = soul.get_current_effects()

        after_bonus = dict(current_bonus)
        for eff in soul_effects:
            attr = eff["attr"]
            if attr not in after_bonus:
                after_bonus[attr] = {"flat": 0, "percent": 0.0}
            after_bonus[attr]["flat"] += eff.get("flat", 0)
            after_bonus[attr]["percent"] += eff.get("percent", 0.0)

        return {
            "can_equip": can_equip,
            "message": msg if not can_equip else "",
            "soul": soul.to_dict(),
            "current_bonus": current_bonus,
            "after_bonus": after_bonus,
            "slot_info": {
                "max": slot.get_max_slots(),
                "used": slot.get_used_slots(),
                "free": slot.get_free_slots(),
            },
        }


# ===================== 属性加成计算 =====================
class MoSoulStatBonusCalculator:
    """魔魂属性加成计算器

    将魔魂效果转换为 StatBonus 对象，与 beast_stats.py 集成。
    """

    @staticmethod
    def calc_stat_bonus(slot: BeastMoSoulSlot) -> StatBonus:
        """计算幻兽装备魔魂的总属性加成

        Args:
            slot: 幻兽魔魂槽位

        Returns:
            StatBonus: 属性加成对象
        """
        bonus = StatBonus()
        total = slot.get_total_stat_bonus()

        # 映射属性
        if "hp" in total:
            bonus.hp_flat = int(total["hp"].get("flat", 0))
            bonus.hp_percent = total["hp"].get("percent", 0) / 100.0

        if "physical_attack" in total:
            bonus.physical_attack_flat = int(total["physical_attack"].get("flat", 0))
            bonus.physical_attack_percent = (
                total["physical_attack"].get("percent", 0) / 100.0
            )

        if "magic_attack" in total:
            bonus.magic_attack_flat = int(total["magic_attack"].get("flat", 0))
            bonus.magic_attack_percent = total["magic_attack"].get("percent", 0) / 100.0

        if "physical_defense" in total:
            bonus.physical_defense_flat = int(total["physical_defense"].get("flat", 0))
            bonus.physical_defense_percent = (
                total["physical_defense"].get("percent", 0) / 100.0
            )

        if "magic_defense" in total:
            bonus.magic_defense_flat = int(total["magic_defense"].get("flat", 0))
            bonus.magic_defense_percent = (
                total["magic_defense"].get("percent", 0) / 100.0
            )

        if "speed" in total:
            bonus.speed_flat = int(total["speed"].get("flat", 0))
            bonus.speed_percent = total["speed"].get("percent", 0) / 100.0

        return bonus

    @staticmethod
    def calc_from_souls(souls: List[MoSoul]) -> StatBonus:
        """直接从魔魂列表计算属性加成"""
        slot = BeastMoSoulSlot(beast_id=0, beast_level=100, equipped_souls=souls)
        return MoSoulStatBonusCalculator.calc_stat_bonus(slot)


# ===================== 便捷函数 =====================
def calc_mosoul_bonus_from_repo(equipped_mosouls: List[Dict], base_stats: Dict[str, int]) -> Dict[str, int]:
    """从数据库返回的魔魂数据计算属性加成
    
    Args:
        equipped_mosouls: 从mosoul_repo.get_mosouls_by_beast返回的魔魂数据列表
        base_stats: 幻兽基础属性 {"hp": x, "physical_attack": x, ...}
    
    Returns:
        属性加成字典 {"hp": x, "physical_attack": x, ...}
    """
    result = {
        "hp": 0,
        "physical_attack": 0,
        "magic_attack": 0,
        "physical_defense": 0,
        "magic_defense": 0,
        "speed": 0,
    }
    pct = {
        "hp": 0,
        "physical_attack": 0,
        "magic_attack": 0,
        "physical_defense": 0,
        "magic_defense": 0,
        "speed": 0,
    }
    
    if equipped_mosouls:
        for mosoul_row in equipped_mosouls:
            template = get_mosoul_template(mosoul_row['template_id'])
            if template:
                level = mosoul_row.get('level', 1)
                effects = template.get_effect_at_level(level)
                for eff in effects:
                    attr = eff.get('attr', '')
                    if attr in result:
                        result[attr] += eff.get('flat', 0)
                        pct[attr] += eff.get('percent', 0)
    
    for attr in result:
        base_val = base_stats.get(attr, 0)
        result[attr] += int(base_val * pct[attr] / 100)
    
    return result


def get_beast_mosoul_bonus(beast_id: int, equipped_souls: List[MoSoul], beast_level: int) -> StatBonus:
    """获取幻兽魔魂加成的便捷函数

    Args:
        beast_id: 幻兽ID
        equipped_souls: 已装备的魔魂列表
        beast_level: 幻兽等级

    Returns:
        StatBonus: 属性加成
    """
    slot = BeastMoSoulSlot(
        beast_id=beast_id,
        beast_level=beast_level,
        equipped_souls=equipped_souls,
    )
    return MoSoulStatBonusCalculator.calc_stat_bonus(slot)
