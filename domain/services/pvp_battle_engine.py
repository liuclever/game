"""玩家 vs 玩家 幻兽对战引擎

说明：
- 这是一个纯领域层模块，不依赖 Flask / MySQL。
- 只负责：按照策划提供的公式和流程，计算一场玩家之间的幻兽战斗结果 + 战报。
- 不负责：从数据库读取玩家/幻兽、发放奖励、扣除活力等。这些放在 application/infrastructure 层。

当前实现范围：
- 支持多只幻兽依次上场作战，未阵亡的幻兽可以带着剩余气血继续下一场。
- 战斗顺序：使用多级先手规则（速度 > 品质 > 星数总和 > 资质总和 > 属性总和，相同则随机）决定谁先出手。
- 扣血公式：完全按照需求中给出的“攻防差 + 0.069~0.071 浮动 + 防御档位倍数 / 负数特别规则”实现。
- 战报：以“每次攻击”为一回合记录，最多保留前 50 条攻击记录。

后续可以在此基础上继续接入技能、Buff/Debuff 等更复杂规则。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional
import random

AttackType = Literal["physical", "magic"]


@dataclass
class StatusEffect:
    """状态效果（预留给中毒/减防/减速等）

    当前实现只负责回合数递减；具体数值效果可以根据技能文档再补充。
    """

    type: str  # 例如: "poison", "def_down", "speed_down" 等
    value: float  # 数值含义由 type 决定（倍数 / 百分比 / 绝对值）
    remain_rounds: int
    source_skill: str = ""


@dataclass
class PvpBeast:
    """PVP 战斗用的幻兽快照。

    注意：这里的属性应该是“已经算好所有被动/装备加成之后的最终属性”。
    """

    # ===== 必填字段（无默认值） =====
    id: int
    name: str

    hp_max: int
    hp_current: int

    physical_attack: int
    magic_attack: int
    physical_defense: int
    magic_defense: int
    speed: int

    # 攻击类型必须显式指定，不能有默认值，避免 dataclass 顺序错误
    attack_type: AttackType  # "physical" / "magic"

    # ===== 下面都是有默认值的可选字段 =====
    # 品质 / 阶位：数值越大品质越高，例如 2=神兽, 1=精英, 0=普通。
    grade: int = 0

    # 星数（用于先手规则第三步：星数总和），可按前端/策划规则映射后填入。
    hp_star: int = 0
    attack_star: int = 0  # 主攻（物攻或法攻）的星数
    physical_defense_star: int = 0
    magic_defense_star: int = 0
    speed_star: int = 0

    # 资质（用于先手规则第四步：资质总和）。
    hp_aptitude: int = 0
    attack_aptitude: int = 0  # 主攻（物攻或法攻）的资质
    physical_defense_aptitude: int = 0
    magic_defense_aptitude: int = 0
    speed_aptitude: int = 0

    skills: List[str] = field(default_factory=list)

    is_dead: bool = False
    status_effects: List[StatusEffect] = field(default_factory=list)

    # 技能系统用到的被动加成标记（增益技能）
    poison_enhance: float = 0.0      # 毒攻强化（增加毒攻触发概率）
    critical_resist: float = 0.0      # 必杀抗性（减少必杀触发概率）
    immune_counter: bool = False      # 免疫反击/反震（偷袭技能）
    poison_resist: float = 0.0        # 毒抗（抗性增强技能）

    def effective_speed(self) -> int:
        """考虑减速/加速等效果后的速度（目前只简单处理减速/加速）。"""

        spd = self.speed
        for eff in self.status_effects:
            if eff.remain_rounds <= 0:
                continue
            if eff.type == "speed_down":
                spd = int(spd * (1.0 - eff.value))
            elif eff.type == "speed_up":
                spd = int(spd * (1.0 + eff.value))
        return max(1, spd)

    @property
    def alive(self) -> bool:
        return (not self.is_dead) and self.hp_current > 0


@dataclass
class PvpPlayer:
    """PVP 战斗用的玩家快照。"""

    player_id: int
    level: int
    beasts: List[PvpBeast]
    name: str = ""

    def first_alive_index(self) -> Optional[int]:
        """找到第一只还活着的幻兽索引，没有则返回 None。"""

        for idx, b in enumerate(self.beasts):
            if b.alive:
                return idx
        return None


@dataclass
class AttackLog:
    """单次攻击的战报记录（一回合 = 一次攻击）。"""

    turn: int  # 第几回合（从 1 开始）

    attacker_player_id: int
    defender_player_id: int

    attacker_beast_id: int
    defender_beast_id: int

    attacker_name: str
    defender_name: str

    skill_name: str  # 本次使用的技能名（目前默认为 "普攻"，后续可按技能系统扩展）

    damage: int
    attacker_hp_after: int
    defender_hp_after: int

    description: str  # 用于前端展示的一整句描述


@dataclass
class PvpBattleResult:
    """整场玩家 vs 玩家 战斗结果。"""

    attacker_player_id: int
    defender_player_id: int

    winner_player_id: int
    loser_player_id: int

    total_turns: int
    logs: List[AttackLog] = field(default_factory=list)  # 最多 50 条


# ============================================================
# 伤害计算相关
# ============================================================


def _pick_attack_and_defense(attacker: PvpBeast, defender: PvpBeast) -> tuple[int, int, AttackType]:
    """根据攻击类型选择攻防数值。

    返回: (攻防差 attack_minus_defense, 防御数值 defense_value, 实际使用的攻击类型)
    """

    # 优先按 attack_type 判断，其次看哪种攻击力非 0
    if attacker.attack_type == "magic" or (
        attacker.magic_attack > 0 and attacker.physical_attack <= 0
    ):
        atk = attacker.magic_attack
        df = defender.magic_defense
        atk_type: AttackType = "magic"
    else:
        atk = attacker.physical_attack
        df = defender.physical_defense
        atk_type = "physical"

    diff = atk - df
    return diff, df, atk_type


def _defense_multiplier(defense_value: int) -> float:
    """根据防御档位返回相关倍数（攻减防 >= 0 的情况）。"""

    if defense_value < 0:
        defense_value = 0

    if defense_value < 1000:
        return 3.8
    if defense_value < 2000:
        return 2.0
    if defense_value < 3000:
        return 1.6
    if defense_value < 4000:
        return 1.3
    if defense_value < 5000:
        return 1.1
    return 1.0


def _is_low_rank_level(player_level: int) -> bool:
    """黄阶(20-29) 或 玄阶(30-39) 视为低阶，用于负数伤害再额外 *0.3。"""

    return 20 <= player_level <= 39


def calc_damage(attacker: PvpBeast, defender: PvpBeast, attacker_player_level: int) -> int:
    """按照需求文档计算一次攻击的扣血量。

    - 正常情况（攻减防 >= 0）:
        damage = (攻减防) * rand(0.069, 0.071) * 防御档位倍数
    - 当攻减防 < 0 时：
        完全采用区间伤害 250~300 或 20~40 乘以系数，不再乘防御档位倍数。
        若攻击方玩家等级在 [20, 39]，再整体 *0.3。

    最终伤害向下取整，至少为 1。
    """

    diff, defense_value, _ = _pick_attack_and_defense(attacker, defender)

    # 攻 - 防 >= 0 的情况
    if diff >= 0:
        rand_factor = random.uniform(0.069, 0.071)  # 浮点数随机
        mul = _defense_multiplier(defense_value)
        raw = diff * rand_factor * mul
        dmg = int(raw)
    else:
        # 攻 - 防 < 0 的特殊规则
        # diff 为负数，按其绝对值决定区间
        d = abs(diff)
        base: float

        if d <= 1000:
            base = random.randint(250, 300)
        elif d <= 2000:
            base = random.randint(250, 300) * 0.7
        elif d <= 3000:
            base = random.randint(250, 300) * 0.5
        elif d <= 4000:
            base = random.randint(250, 300) * 0.3
        else:
            base = random.randint(20, 40)

        # 低阶玩家（黄阶/玄阶）再 *0.3
        if _is_low_rank_level(attacker_player_level):
            base *= 0.3

        dmg = int(base)

    return max(1, dmg)


# ============================================================
# 主战斗流程
# ============================================================


def _first_striker_is_attacker(attacker_beast: PvpBeast, defender_beast: PvpBeast) -> bool:
    """根据先手规则决定当前 1v1 中哪一方先手。

    返回 True 表示攻方先手，False 表示守方先手。
    规则优先级：
    1. 速度数值高的先手（考虑 effective_speed 后的结果）。
    2. 幻兽级别高的先手（grade 大的先手，例如 神兽 > 精英 > 普通）。
    3. 气血、主攻（物攻或法攻）、物防、法防、速度的星数总和，大者先手。
    4. 上述 5 项的资质总和，大者先手。
    5. 上述 5 项的属性数值总和（气血用 hp_max，速度用 effective_speed），大者先手。
    6. 仍然完全相同，则随机决定先手。
    """

    # 1. 速度
    a_speed = attacker_beast.effective_speed()
    d_speed = defender_beast.effective_speed()
    if a_speed != d_speed:
        return a_speed > d_speed

    # 2. 品质 / 阶位
    if attacker_beast.grade != defender_beast.grade:
        return attacker_beast.grade > defender_beast.grade

    # 辅助函数：主攻（物攻或法攻）
    def _main_attack_value(beast: PvpBeast) -> int:
        return beast.magic_attack if beast.attack_type == "magic" else beast.physical_attack

    def _main_attack_star(beast: PvpBeast) -> int:
        return beast.attack_star

    def _main_attack_aptitude(beast: PvpBeast) -> int:
        return beast.attack_aptitude

    # 3. 星数总和
    a_star_sum = (
        attacker_beast.hp_star
        + _main_attack_star(attacker_beast)
        + attacker_beast.physical_defense_star
        + attacker_beast.magic_defense_star
        + attacker_beast.speed_star
    )
    d_star_sum = (
        defender_beast.hp_star
        + _main_attack_star(defender_beast)
        + defender_beast.physical_defense_star
        + defender_beast.magic_defense_star
        + defender_beast.speed_star
    )
    if a_star_sum != d_star_sum:
        return a_star_sum > d_star_sum

    # 4. 资质总和
    a_apt_sum = (
        attacker_beast.hp_aptitude
        + _main_attack_aptitude(attacker_beast)
        + attacker_beast.physical_defense_aptitude
        + attacker_beast.magic_defense_aptitude
        + attacker_beast.speed_aptitude
    )
    d_apt_sum = (
        defender_beast.hp_aptitude
        + _main_attack_aptitude(defender_beast)
        + defender_beast.physical_defense_aptitude
        + defender_beast.magic_defense_aptitude
        + defender_beast.speed_aptitude
    )
    if a_apt_sum != d_apt_sum:
        return a_apt_sum > d_apt_sum

    # 5. 属性数值总和（使用最大气血 + 主攻 + 物防 + 法防 + 当前速度）
    a_stat_sum = (
        attacker_beast.hp_max
        + _main_attack_value(attacker_beast)
        + attacker_beast.physical_defense
        + attacker_beast.magic_defense
        + a_speed
    )
    d_stat_sum = (
        defender_beast.hp_max
        + _main_attack_value(defender_beast)
        + defender_beast.physical_defense
        + defender_beast.magic_defense
        + d_speed
    )
    if a_stat_sum != d_stat_sum:
        return a_stat_sum > d_stat_sum

    # 6. 完全相同则随机
    return bool(random.getrandbits(1))


def run_pvp_battle(
    attacker_player: PvpPlayer,
    defender_player: PvpPlayer,
    max_log_turns: int = 50,
) -> PvpBattleResult:
    """执行一场完整的玩家 vs 玩家 幻兽战斗，并接入技能系统。

    流程要点：
    1. 对当前上场幻兽使用 `_first_striker_is_attacker` 判定先手；
    2. 每次攻击前结算持续效果（目前仅预留接口）；
    3. 判定主动技能（必杀/连击/破甲/毒攻等）是否触发；
    4. 判定被动技能（闪避/反震/反击）是否触发；
    5. 生成带技能名的战报文本；
    6. 当一方所有幻兽阵亡时，战斗结束；
    7. 战报最多保留前 `max_log_turns` 条。
    """

    # 为避免循环依赖，这里在函数内部导入技能系统
    from domain.services.skill_system import (
        try_trigger_active_skill,
        try_trigger_passive_skill,
        check_poison_resist,
    )

    logs: List[AttackLog] = []
    turn = 0

    # 当前出战幻兽索引
    a_idx = attacker_player.first_alive_index()
    d_idx = defender_player.first_alive_index()

    while a_idx is not None and d_idx is not None:
        a_beast = attacker_player.beasts[a_idx]
        d_beast = defender_player.beasts[d_idx]

        # 当前这两只打到其中一只阵亡为止
        while a_beast.alive and d_beast.alive:
            # 使用先手规则决定本轮攻击顺序
            attacker_first = _first_striker_is_attacker(a_beast, d_beast)

            if attacker_first:
                order = [
                    (attacker_player, a_beast, defender_player, d_beast),
                    (defender_player, d_beast, attacker_player, a_beast),
                ]
            else:
                order = [
                    (defender_player, d_beast, attacker_player, a_beast),
                    (attacker_player, a_beast, defender_player, d_beast),
                ]

            for atk_player, atk_beast, def_player, def_beast in order:
                if not atk_beast.alive or not def_beast.alive:
                    # 可能在上一击中已经阵亡
                    continue

                # 回合数 +1
                turn += 1

                # 1. 结算攻击方身上的持续效果（占位，当前仅做回合数递减）
                _tick_status_effects_before_action(atk_beast)

                # 2. 主动技能判定（必杀/连击/破甲/毒攻等）
                skill_result = try_trigger_active_skill(
                    attacker_skills=atk_beast.skills,
                    attack_type=atk_beast.attack_type,
                    defender_critical_resist=def_beast.critical_resist,
                    attacker_poison_enhance=atk_beast.poison_enhance,
                )

                is_normal_attack = not skill_result.triggered
                skill_name = skill_result.skill_name if skill_result.triggered else "普攻"
                damage_multiplier = (
                    skill_result.damage_multiplier if skill_result.triggered else 1.0
                )

                # 3. 被动技能判定（闪避/反震/反击）
                passive_result = try_trigger_passive_skill(
                    defender_skills=def_beast.skills,
                    is_normal_attack=is_normal_attack,
                    attacker_immune_counter=atk_beast.immune_counter,
                )

                # 4. 基础伤害
                base_damage = calc_damage(atk_beast, def_beast, atk_player.level)
                final_damage = int(base_damage * damage_multiplier)

                # 5. 闪避处理
                dodged = False
                if (
                    passive_result.triggered
                    and passive_result.effect_type == "dodge"
                ):
                    dodged = True
                    final_damage = 0

                # 6. 扣血
                actual_damage = final_damage
                if not dodged:
                    def_beast.hp_current = max(
                        0, def_beast.hp_current - final_damage
                    )
                    if def_beast.hp_current <= 0:
                        def_beast.is_dead = True

                # 7. 吸血（高级/普通吸血）
                if skill_result.lifesteal_ratio > 0 and actual_damage > 0:
                    heal_amount = int(actual_damage * skill_result.lifesteal_ratio)
                    if heal_amount > 0:
                        atk_beast.hp_current = min(
                            atk_beast.hp_max,
                            atk_beast.hp_current + heal_amount,
                        )

                # 8. 反震/反击
                reflect_damage = 0
                if (
                    passive_result.triggered
                    and passive_result.effect_type in ("reflect", "counter")
                    and actual_damage > 0
                ):
                    reflect_damage = int(actual_damage * passive_result.effect_value)
                    atk_beast.hp_current = max(
                        0, atk_beast.hp_current - reflect_damage
                    )
                    if atk_beast.hp_current <= 0:
                        atk_beast.is_dead = True

                # 9. 技能附加效果（破甲/致盲/麻痹/迷惑/虚弱/毒攻等）
                applied_effects = []
                for eff in skill_result.effects:
                    # 毒攻受抗性影响
                    if eff.effect_type == "poison":
                        if check_poison_resist(def_beast.skills):
                            continue
                    _apply_or_refresh_effect(def_beast, eff)
                    applied_effects.append(eff)

                # 10. 生成战报文本（只保留前 max_log_turns 条）
                if turn <= max_log_turns:
                    description = _build_attack_description(
                        turn=turn,
                        atk_player=atk_player,
                        atk_beast=atk_beast,
                        def_player=def_player,
                        def_beast=def_beast,
                        skill_name=skill_name,
                        damage=actual_damage,
                        dodged=dodged,
                        passive_result=passive_result,
                        reflect_damage=reflect_damage,
                        lifesteal_ratio=skill_result.lifesteal_ratio,
                        applied_effects=applied_effects,
                    )

                    logs.append(
                        AttackLog(
                            turn=turn,
                            attacker_player_id=atk_player.player_id,
                            defender_player_id=def_player.player_id,
                            attacker_beast_id=atk_beast.id,
                            defender_beast_id=def_beast.id,
                            attacker_name=atk_beast.name,
                            defender_name=def_beast.name,
                            skill_name=skill_name,
                            damage=actual_damage,
                            attacker_hp_after=atk_beast.hp_current,
                            defender_hp_after=def_beast.hp_current,
                            description=description,
                        )
                    )

                # 若被攻击方阵亡，本小循环结束，换下一只幻兽
                if not def_beast.alive:
                    break

            # 检查是否有一方已经没有活着的幻兽
            if not a_beast.alive or not d_beast.alive:
                break

        # 当前这两只之一阵亡，更新索引，继续下一只对战
        a_idx = attacker_player.first_alive_index()
        d_idx = defender_player.first_alive_index()

    # 判定胜负
    attacker_alive = attacker_player.first_alive_index() is not None
    defender_alive = defender_player.first_alive_index() is not None

    if attacker_alive and not defender_alive:
        winner_id = attacker_player.player_id
        loser_id = defender_player.player_id
    elif defender_alive and not attacker_alive:
        winner_id = defender_player.player_id
        loser_id = attacker_player.player_id
    else:
        # 双方都无幻兽或都还有幻兽的极端情况，这里简单认为防守方获胜
        winner_id = defender_player.player_id
        loser_id = attacker_player.player_id

    return PvpBattleResult(
        attacker_player_id=attacker_player.player_id,
        defender_player_id=defender_player.player_id,
        winner_player_id=winner_id,
        loser_player_id=loser_id,
        total_turns=turn,
        logs=logs,
    )


def _build_attack_description(
    *,
    turn: int,
    atk_player: PvpPlayer,
    atk_beast: PvpBeast,
    def_player: PvpPlayer,
    def_beast: PvpBeast,
    skill_name: str,
    damage: int,
    dodged: bool,
    passive_result,
    reflect_damage: int,
    lifesteal_ratio: float,
    applied_effects: List,
) -> str:
    """构造一条用于前端展示的战报描述，不包含 "[回合X]" 前缀。

    前端会自行在外层加上 "[回合X]："。
    """

    atk_player_name = atk_player.name or str(atk_player.player_id)
    def_player_name = def_player.name or str(def_player.player_id)

    # 闪避类：不扣血，优先描述防守方躲避了攻击
    if dodged:
        if getattr(passive_result, "triggered", False) and getattr(
            passive_result, "skill_name", ""
        ):
            return (
                f"『{def_player_name}』的{def_beast.name}触发{passive_result.skill_name}，"
                f"躲开了『{atk_player_name}』的{atk_beast.name}的攻击"
            )
        return (
            f"『{def_player_name}』的{def_beast.name}躲开了"
            f"『{atk_player_name}』的{atk_beast.name}的攻击"
        )

    # 基础攻击文案
    if skill_name and skill_name != "普攻":
        desc = (
            f"『{atk_player_name}』的{atk_beast.name}使用{skill_name}攻击"
            f"『{def_player_name}』的{def_beast.name}"
        )
    else:
        desc = (
            f"『{atk_player_name}』的{atk_beast.name}攻击"
            f"『{def_player_name}』的{def_beast.name}"
        )

    # 造成伤害
    if damage > 0:
        desc += f"，气血-{damage}"
    else:
        desc += "，未造成伤害"

    # 吸血效果（根据伤害和吸血比例简单计算展示用的回复量）
    if lifesteal_ratio > 0 and damage > 0:
        heal_amount = int(damage * lifesteal_ratio)
        if heal_amount > 0:
            desc += f"，自身回复{heal_amount}点气血"

    # 反震 / 反击伤害展示
    if reflect_damage > 0 and getattr(passive_result, "triggered", False):
        if passive_result.effect_type == "reflect":
            # 反震：被攻击方反弹固定比例伤害
            desc += (
                f"，受到{passive_result.skill_name}反震，"
                f"自身气血-{reflect_damage}"
            )
        elif passive_result.effect_type == "counter":
            # 反击：被攻击方追加一次反击伤害
            desc += (
                f"，受到{passive_result.skill_name}反击，"
                f"自身气血-{reflect_damage}"
            )

    # 附加的减防 / 减攻 / 减速 / 中毒等效果说明
    for eff in applied_effects:
        eff_type = getattr(eff, "effect_type", "")
        value = getattr(eff, "value", 0.0)
        duration = getattr(eff, "duration", 0)

        if eff_type == "physical_defense_down":
            desc += f"，使其物理防御下降{int(value * 100)}%，持续{duration}回合"
        elif eff_type == "magic_defense_down":
            desc += f"，使其法术防御下降{int(value * 100)}%，持续{duration}回合"
        elif eff_type == "speed_down":
            desc += f"，使其速度下降{int(value * 100)}%，持续{duration}回合"
        elif eff_type == "physical_attack_down":
            desc += f"，使其物理攻击下降{int(value * 100)}%，持续{duration}回合"
        elif eff_type == "magic_attack_down":
            desc += f"，使其法术攻击下降{int(value * 100)}%，持续{duration}回合"
        elif eff_type == "poison":
            # 中毒只提示一次，实际伤害在 _tick_status_effects_before_action 中结算
            desc += f"，使其中毒，每回合损失一定气血（持续{duration}回合）"

    return desc


def _apply_or_refresh_effect(beast: PvpBeast, effect) -> None:
    """应用或刷新状态效果（同类型效果刷新持续时间）。

    `effect` 来自技能系统的 SkillEffect，包含 effect_type / value / duration / source_skill。
    在战斗内部，我们将其转换为本地的 StatusEffect 存储在 PvpBeast.status_effects 中。
    """

    # 如果已存在同类型效果，则刷新持续时间和数值
    for existing in beast.status_effects:
        if existing.type == getattr(effect, "effect_type", None):
            existing.remain_rounds = getattr(effect, "duration", 0)
            existing.value = getattr(effect, "value", 0.0)
            existing.source_skill = getattr(effect, "source_skill", "")
            return

    # 否则追加一个新的状态
    beast.status_effects.append(
        StatusEffect(
            type=getattr(effect, "effect_type", ""),
            value=getattr(effect, "value", 0.0),
            remain_rounds=getattr(effect, "duration", 0),
            source_skill=getattr(effect, "source_skill", ""),
        )
    )


def _tick_status_effects_before_action(beast: PvpBeast) -> None:
    """在幻兽自己行动前结算一次持续效果，并扣减回合数。

    目前只做回合数递减，占位留给将来的真正效果实现。
    """

    new_effects: List[StatusEffect] = []
    for eff in beast.status_effects:
        if eff.remain_rounds <= 0:
            continue

        # TODO: 根据 eff.type / eff.value 在这里实现诸如中毒掉血等效果。
        # 例如：
        # if eff.type == "poison":
        #     poison_damage = max(1, int(beast.hp_max * eff.value))
        #     beast.hp_current = max(0, beast.hp_current - poison_damage)

        eff.remain_rounds -= 1
        if eff.remain_rounds > 0:
            new_effects.append(eff)
    beast.status_effects = new_effects
