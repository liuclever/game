"""domain/services/beast_factory.py

负责根据幻兽模板创建一只新的幻兽实例（初始化幻兽）。

这里只定义整体流程骨架，不实现任何具体规则：
- 从模板中读取基础信息（名字、属地、稀有、特性等）；
- 决定初始化等级 / 经验；
- 按规则生成初始各项资质；
- 按规则从模板技能池中选出初始技能；
- 决定性格等实例专属属性；
- 返回一个尚未持久化的 Beast 实例。

具体规则（随机范围、概率、公式）后续再逐步补充。
"""

from typing import List
import random

from domain.entities.beast import Beast, BeastTemplate
from domain.services.skill_system import get_skill_config

# 可选性格列表
_PERSONALITIES: List[str] = ["勇敢", "精明", "胆小", "谨慎", "傻瓜"]


# ========== 初始化技能相关 ==========

def _choose_initial_skill_ids(all_skill_ids: List[int]) -> List[int]:
    """
    规则：
    - 假设 all_skill_ids 有 N 个技能；
    - 初始化时可能的情况共有 N+1 种：
      0 个技能、1 个技能、...、N 个技能；
    - 本函数先在 [0, N] 中随机选择一个技能数量 k，然后从 all_skill_ids 中随机选出 k 个不重复的技能ID。
    """
    n = len(all_skill_ids)
    if n == 0:
        return []

    # 在 [0, n] 之间随机选择本次拥有的技能数量
    k = random.randint(0, n)
    if k == 0:
        return []

    # 从技能池中随机选择 k 个技能ID（不重复）
    return random.sample(all_skill_ids, k)


def _convert_skill_ids_to_names(skill_ids: List[int]) -> List[str]:
    """将技能ID列表转换为技能名称列表，便于技能系统使用。

    技能ID到名称的映射来自 configs/skills.json 中的 "skill_ids" 字段。
    """
    if not skill_ids:
        return []

    config = get_skill_config()
    id_map = config.get("skill_ids", {})

    # 反转映射： name -> id  =>  id -> name
    id_to_name = {v: k for k, v in id_map.items()}
    names: List[str] = []
    for sid in skill_ids:
        name = id_to_name.get(sid)
        if name:
            names.append(name)
    return names


# ========== 初始化资质相关 ==========


def _roll_aptitude(max_value: int) -> int:
    """根据模板上的资质上限随机生成一条资质数值。

    规则：
    - 给定某项资质上限 max_value；
    - 随机选择一个 x，满足 0 <= x < 350；
    - 实际资质 = max_value - x；
    - 如果结果小于 0，则按 0 处理（安全兜底）。
    """
    if max_value <= 0:
        return 0

    x = random.randint(0, 349)  # 0 ≤ x < 350
    value = max_value - x
    return value if value > 0 else 0


def _init_aptitudes(template: BeastTemplate) -> dict:
    """根据模板上的各项 *_aptitude_max 字段，生成实例的初始资质。"""
    # DEBUG: 打印模板的物攻资质上限
    print(f"[DEBUG] Template {template.name}: physical_atk_aptitude_max = {template.physical_atk_aptitude_max}")
    
    p_atk = _roll_aptitude(template.physical_atk_aptitude_max)
    print(f"[DEBUG] Rolled physical_atk_aptitude = {p_atk}")
    return {
        "hp_aptitude": _roll_aptitude(template.hp_aptitude_max),
        "speed_aptitude": _roll_aptitude(template.speed_aptitude_max),
        "physical_atk_aptitude": _roll_aptitude(template.physical_atk_aptitude_max),
        "magic_atk_aptitude": _roll_aptitude(template.magic_atk_aptitude_max),
        "physical_def_aptitude": _roll_aptitude(template.physical_def_aptitude_max),
        "magic_def_aptitude": _roll_aptitude(template.magic_def_aptitude_max),
    }


def _init_personality() -> str:
    """随机生成一条性格。"""
    return random.choice(_PERSONALITIES)


def create_initial_beast(user_id: int, template: BeastTemplate) -> Beast:
    """
    当前实现：
    - 等级固定为1级，经验为0；
    - 资质、性格等仍使用默认值（后续可在此扩展）；
    - 初始化技能：
        * 从模板的 all_skill_ids 中，根据上述规则随机选择若干个技能ID；
        * 再转换为技能名称，存入 Beast.skills。
    """
    # 1. 选择初始化技能ID集合
    initial_skill_ids = _choose_initial_skill_ids(template.all_skill_ids)

    # 2. 将技能ID转换为技能名称，以便技能系统按名称查配置
    initial_skill_names = _convert_skill_ids_to_names(initial_skill_ids)

    # 3. 初始化各项资质
    aptitudes = _init_aptitudes(template)

    # 4. 构造一个尚未持久化的 Beast 实例（其他字段使用默认值或简单规则）
    beast = Beast(
        user_id=user_id,                                        # 所属玩家ID
        template_id=template.id,                                # 幻兽模板ID
        nickname=template.name,                                 # 昵称，默认使用模板名称
        level=1,                                                # 初始等级为1级
        exp=0,                                                  # 初始经验为0
        is_main=False,                                          # 默认不出战
        # 实例性格，从预定义列表中随机一个
        personality=_init_personality(),
        # 复制模板上的攻击类型和境界，便于调试和后续可能的个体修改
        attack_type=template.attack_type,
        realm=template.realm,
        # 成长率（从模板的 growth_score 获取）
        growth_rate=template.growth_score,
        # 资质相关
        hp_aptitude=aptitudes["hp_aptitude"],                   # 气血资质
        speed_aptitude=aptitudes["speed_aptitude"],             # 速度资质
        physical_atk_aptitude=aptitudes["physical_atk_aptitude"],  # 物攻资质
        magic_atk_aptitude=aptitudes["magic_atk_aptitude"],     # 法攻资质
        physical_def_aptitude=aptitudes["physical_def_aptitude"],  # 物防资质
        magic_def_aptitude=aptitudes["magic_def_aptitude"],     # 法防资质
        # 技能列表
        skills=initial_skill_names,                             # 初始技能名称列表
    )

    return beast
