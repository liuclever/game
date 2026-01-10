"""魔魂装备规则。

实现魔魂装备的冲突检测规则：
1. 龙魂的百分比属性不能与天/地/玄/黄魂的同类百分比属性共存
2. 非龙魂之间，同类固定值或百分比属性不能共存
"""
from typing import List, Tuple, Optional, Set, Dict
from dataclasses import dataclass

from domain.entities.mosoul import MoSoul, MoSoulGrade, BeastMoSoulSlot


@dataclass
class ConflictResult:
    """冲突检测结果"""
    has_conflict: bool
    conflict_type: str = ""
    conflict_attr: str = ""
    conflict_souls: Tuple[str, str] = ("", "")
    message: str = ""

    @staticmethod
    def no_conflict() -> "ConflictResult":
        return ConflictResult(has_conflict=False)

    @staticmethod
    def dragon_percent_conflict(
        attr: str, dragon_name: str, other_name: str
    ) -> "ConflictResult":
        return ConflictResult(
            has_conflict=True,
            conflict_type="dragon_percent",
            conflict_attr=attr,
            conflict_souls=(dragon_name, other_name),
            message=f"龙魂[{dragon_name}]的{_attr_chinese(attr)}百分比加成"
                    f"与[{other_name}]冲突，不能同时装备",
        )

    @staticmethod
    def same_attr_conflict(
        attr: str, bonus_type: str, name1: str, name2: str
    ) -> "ConflictResult":
        type_name = "百分比" if bonus_type == "percent" else "固定值"
        return ConflictResult(
            has_conflict=True,
            conflict_type=f"same_{bonus_type}",
            conflict_attr=attr,
            conflict_souls=(name1, name2),
            message=f"[{name1}]与[{name2}]都有{_attr_chinese(attr)}{type_name}加成，不能同时装备",
        )


def _attr_chinese(attr: str) -> str:
    """属性英文转中文"""
    mapping = {
        "hp": "气血",
        "physical_attack": "物理攻击",
        "magic_attack": "法术攻击",
        "physical_defense": "物理防御",
        "magic_defense": "法术防御",
        "speed": "速度",
    }
    return mapping.get(attr, attr)


def _extract_percent_attrs(soul: MoSoul) -> Set[str]:
    """提取魔魂的百分比属性列表"""
    result = set()
    template = soul.get_template()
    if not template:
        return result
    for eff in template.effects:
        if eff.get("percent", 0) > 0:
            result.add(eff["attr"])
    return result


def _extract_flat_attrs(soul: MoSoul) -> Set[str]:
    """提取魔魂的固定值属性列表"""
    result = set()
    template = soul.get_template()
    if not template:
        return result
    for eff in template.effects:
        if eff.get("flat", 0) > 0:
            result.add(eff["attr"])
    return result


def check_equip_level(beast_level: int) -> Tuple[bool, str]:
    """检查幻兽等级是否满足装备魔魂要求

    Args:
        beast_level: 幻兽等级

    Returns:
        (是否满足, 错误信息)
    """
    if beast_level < 30:
        return False, f"幻兽需要达到30级才能装备魔魂，当前等级：{beast_level}"
    return True, ""


def get_max_equip_slots(beast_level: int) -> int:
    """获取幻兽可装备魔魂数量

    规则：30级起每10级可装备一个魔魂
    30-39级：3个；40-49级：4个；...；100级：10个
    """
    if beast_level < 30:
        return 0
    return beast_level // 10


def check_slot_availability(slot: BeastMoSoulSlot) -> Tuple[bool, str]:
    """检查槽位是否还有空余

    Args:
        slot: 幻兽魔魂槽位

    Returns:
        (是否有空位, 错误信息)
    """
    if not slot.can_equip():
        max_slots = slot.get_max_slots()
        return False, f"魔魂槽位已满，当前等级最多装备{max_slots}个魔魂"
    return True, ""


def check_dragon_soul_conflict(
    new_soul: MoSoul,
    equipped_souls: List[MoSoul],
) -> ConflictResult:
    """检查龙魂与其他魔魂的百分比属性冲突

    规则：龙魂的百分比属性不能与天/地/玄/黄魂的同类百分比属性共存

    例如：
    - 龙魂.斗战不息（物攻12%）不能与天魂.无人能挡（物攻8%）同时装备
    - 龙魂.谁与争锋（速度9.6%）不能与天魂.流星赶月（速度6.4%）同时装备
    """
    new_template = new_soul.get_template()
    if not new_template:
        return ConflictResult.no_conflict()

    new_is_dragon = new_template.grade == MoSoulGrade.DRAGON_SOUL
    new_percent_attrs = _extract_percent_attrs(new_soul)

    for equipped in equipped_souls:
        eq_template = equipped.get_template()
        if not eq_template:
            continue

        eq_is_dragon = eq_template.grade == MoSoulGrade.DRAGON_SOUL
        eq_percent_attrs = _extract_percent_attrs(equipped)

        # 情况1：新魔魂是龙魂，已装备的不是龙魂
        if new_is_dragon and not eq_is_dragon:
            common_attrs = new_percent_attrs & eq_percent_attrs
            if common_attrs:
                attr = list(common_attrs)[0]
                return ConflictResult.dragon_percent_conflict(
                    attr, new_template.name, eq_template.name
                )

        # 情况2：已装备的是龙魂，新魔魂不是龙魂
        if eq_is_dragon and not new_is_dragon:
            common_attrs = eq_percent_attrs & new_percent_attrs
            if common_attrs:
                attr = list(common_attrs)[0]
                return ConflictResult.dragon_percent_conflict(
                    attr, eq_template.name, new_template.name
                )

    return ConflictResult.no_conflict()


def check_same_bonus_type_conflict(
    new_soul: MoSoul,
    equipped_souls: List[MoSoul],
) -> ConflictResult:
    """检查非龙魂之间的同类属性冲突

    规则：除龙魂外，黄/玄/地/天魂有相同加成情况的不能同时装备

    例如：
    - 黄魂增加15物攻，不能和增加30、60、120物攻的玄/地/天魂同时装备
    - 天魂速度增加6.4%，不能和增加3.2%、1.6%、0.8%速度的地/玄/黄魂同时装备
    """
    new_template = new_soul.get_template()
    if not new_template:
        return ConflictResult.no_conflict()

    # 龙魂不参与此规则（龙魂冲突由 check_dragon_soul_conflict 处理）
    if new_template.grade == MoSoulGrade.DRAGON_SOUL:
        return ConflictResult.no_conflict()

    new_percent_attrs = _extract_percent_attrs(new_soul)
    new_flat_attrs = _extract_flat_attrs(new_soul)

    for equipped in equipped_souls:
        eq_template = equipped.get_template()
        if not eq_template:
            continue

        # 龙魂不参与此规则
        if eq_template.grade == MoSoulGrade.DRAGON_SOUL:
            continue

        eq_percent_attrs = _extract_percent_attrs(equipped)
        eq_flat_attrs = _extract_flat_attrs(equipped)

        # 检查百分比属性冲突
        common_percent = new_percent_attrs & eq_percent_attrs
        if common_percent:
            attr = list(common_percent)[0]
            return ConflictResult.same_attr_conflict(
                attr, "percent", new_template.name, eq_template.name
            )

        # 检查固定值属性冲突
        common_flat = new_flat_attrs & eq_flat_attrs
        if common_flat:
            attr = list(common_flat)[0]
            return ConflictResult.same_attr_conflict(
                attr, "flat", new_template.name, eq_template.name
            )

    return ConflictResult.no_conflict()


def check_equip_conflict(
    new_soul: MoSoul,
    slot: BeastMoSoulSlot,
) -> ConflictResult:
    """综合检查装备魔魂的所有冲突规则

    Args:
        new_soul: 要装备的新魔魂
        slot: 幻兽魔魂槽位

    Returns:
        ConflictResult: 冲突检测结果
    """
    equipped = slot.equipped_souls

    # 检查龙魂百分比冲突
    result = check_dragon_soul_conflict(new_soul, equipped)
    if result.has_conflict:
        return result

    # 检查非龙魂同类属性冲突
    result = check_same_bonus_type_conflict(new_soul, equipped)
    if result.has_conflict:
        return result

    return ConflictResult.no_conflict()


def validate_equip(
    soul: MoSoul,
    slot: BeastMoSoulSlot,
) -> Tuple[bool, str]:
    """完整的装备校验

    Args:
        soul: 要装备的魔魂
        slot: 幻兽魔魂槽位

    Returns:
        (是否可以装备, 错误信息)
    """
    # 检查等级
    can_equip, msg = check_equip_level(slot.beast_level)
    if not can_equip:
        return False, msg

    # 检查槽位
    can_equip, msg = check_slot_availability(slot)
    if not can_equip:
        return False, msg

    # 检查冲突
    conflict = check_equip_conflict(soul, slot)
    if conflict.has_conflict:
        return False, conflict.message

    return True, ""


def find_conflicting_souls(
    new_soul: MoSoul,
    equipped_souls: List[MoSoul],
) -> List[MoSoul]:
    """找出所有与新魔魂冲突的已装备魔魂

    Args:
        new_soul: 要装备的新魔魂
        equipped_souls: 已装备的魔魂列表

    Returns:
        冲突的魔魂列表
    """
    conflicts = []
    new_template = new_soul.get_template()
    if not new_template:
        return conflicts

    new_is_dragon = new_template.grade == MoSoulGrade.DRAGON_SOUL
    new_percent_attrs = _extract_percent_attrs(new_soul)
    new_flat_attrs = _extract_flat_attrs(new_soul)

    for equipped in equipped_souls:
        eq_template = equipped.get_template()
        if not eq_template:
            continue

        eq_is_dragon = eq_template.grade == MoSoulGrade.DRAGON_SOUL
        eq_percent_attrs = _extract_percent_attrs(equipped)
        eq_flat_attrs = _extract_flat_attrs(equipped)

        has_conflict = False

        # 龙魂百分比冲突
        if new_is_dragon and not eq_is_dragon:
            if new_percent_attrs & eq_percent_attrs:
                has_conflict = True
        elif eq_is_dragon and not new_is_dragon:
            if eq_percent_attrs & new_percent_attrs:
                has_conflict = True
        # 非龙魂同类属性冲突
        elif not new_is_dragon and not eq_is_dragon:
            if new_percent_attrs & eq_percent_attrs:
                has_conflict = True
            elif new_flat_attrs & eq_flat_attrs:
                has_conflict = True

        if has_conflict:
            conflicts.append(equipped)

    return conflicts


def suggest_replacement(
    new_soul: MoSoul,
    slot: BeastMoSoulSlot,
) -> Optional[MoSoul]:
    """建议替换的魔魂（如果存在冲突）

    优先建议替换等级较低或效果较弱的魔魂。

    Args:
        new_soul: 要装备的新魔魂
        slot: 幻兽魔魂槽位

    Returns:
        建议替换的魔魂，如果无冲突返回 None
    """
    conflicts = find_conflicting_souls(new_soul, slot.equipped_souls)
    if not conflicts:
        return None

    # 按等级和稀有度排序，优先替换低等级低稀有度的
    conflicts.sort(key=lambda s: (s.level, s.grade.rarity if s.grade else 0))
    return conflicts[0]
