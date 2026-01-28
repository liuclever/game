from dataclasses import dataclass
from typing import Iterable, List, Dict
import json
import os
import random

from domain.entities.beast import Beast, BeastTemplate


# ===================== 境界倍率配置加载 =====================
def _load_realm_config() -> Dict:
    """加载 configs/realm_multipliers.json 配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "configs", "realm_multipliers.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


_REALM_CONFIG = _load_realm_config()
# 从低到高排列的境界列表
REALM_ORDER: List[str] = _REALM_CONFIG["realms"]
# 当最高境界为天界时的基础倍率
BASE_MULTIPLIERS: Dict[str, float] = _REALM_CONFIG["base_multipliers"]


# ===================== 成长率倍率配置加载 =====================
def _load_growth_config() -> Dict[str, float]:
    """加载 configs/growth_rate_multipliers.json 配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "configs", "growth_rate_multipliers.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 转换 key 为 int 方便查找
    return {int(k): v for k, v in data["growth_score_to_multiplier"].items()}


_GROWTH_MULTIPLIERS: Dict[int, float] = _load_growth_config()


def get_growth_multiplier(growth_score: int) -> float:
    """根据成长率评分获取倍率。

    若评分不在配置中，返回最接近且不超过该评分的倍率；
    若评分低于最小值，返回最小倍率。
    """
    if growth_score in _GROWTH_MULTIPLIERS:
        return _GROWTH_MULTIPLIERS[growth_score]
    # 找到不超过 growth_score 的最大 key
    sorted_scores = sorted(_GROWTH_MULTIPLIERS.keys())
    for score in reversed(sorted_scores):
        if score <= growth_score:
            return _GROWTH_MULTIPLIERS[score]
    # 若都比 growth_score 大，返回最小倍率
    return _GROWTH_MULTIPLIERS[sorted_scores[0]]


def calc_level1_speed_from_aptitude(speed_aptitude: int) -> int:
    """根据速度资质计算1级时的速度值
    
    规则: 每1100资质为一档
    - 0-1100 => 1
    - 1101-2200 => 2
    - 2201-3300 => 3
    """
    try:
        sa = int(speed_aptitude or 0)
    except (TypeError, ValueError):
        sa = 0
    if sa < 0:
        sa = 0
    return max(1, (sa + 1099) // 1100)


def get_beast_max_realm(template_realms: Iterable[str]) -> str:
    """根据模板配置的境界列表，找到该幻兽能达到的最高境界"""
    if not template_realms:
        return "地界"
    # 按照 REALM_ORDER 的顺序找最后一个存在的境界
    max_realm = "地界"
    for r in REALM_ORDER:
        if r in template_realms:
            max_realm = r
    return max_realm


def get_buff_skill_bonuses(skills: List[str]) -> Dict[str, float]:
    """计算增幅技能的属性加成百分比
    
    Args:
        skills: 幻兽当前技能列表
        
    Returns:
        各属性的加成百分比字典，例如：
        {
            'hp': 0.10,  # 10%加成
            'physical_attack': 0.09,
            'magic_attack': 0.0,
            'physical_defense': 0.05,
            'magic_defense': 0.0,
            'speed': 0.10
        }
    """
    bonuses = {
        'hp': 0.0,
        'physical_attack': 0.0,
        'magic_attack': 0.0,
        'physical_defense': 0.0,
        'magic_defense': 0.0,
        'speed': 0.0
    }
    
    # 加载技能配置
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "configs", "skills.json"
    )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            skill_config = json.load(f)
    except Exception:
        return bonuses
    
    # 获取增幅技能配置
    buff_skills = skill_config.get("buff_skills", {})
    all_buffs = {}
    for category in ["normal", "advanced"]:
        all_buffs.update(buff_skills.get(category, {}))
    
    # 遍历幻兽技能，累加增幅效果
    for skill_name in skills:
        if skill_name in all_buffs:
            buff_config = all_buffs[skill_name]
            stat = buff_config.get("stat")
            modifier = buff_config.get("modifier", 0.0)
            
            if stat and modifier:
                bonuses[stat] = bonuses.get(stat, 0.0) + modifier
    
    return bonuses


def calc_beast_attributes(
    hp_aptitude: int,
    speed_aptitude: int,
    phys_atk_aptitude: int,
    magic_atk_aptitude: int,
    phys_def_aptitude: int,
    magic_def_aptitude: int,
    level: int = 1,
    realm: str = "地界",
    max_realm: str = "地界",
    growth_score: int = 840,
    nature: str = "",
    skills: List[str] = None,
) -> Dict[str, int]:
    """统一的幻兽属性计算函数
    
    参数:
        hp_aptitude: 气血资质
        speed_aptitude: 速度资质
        phys_atk_aptitude: 物攻资质
        magic_atk_aptitude: 法攻资质
        phys_def_aptitude: 物防资质
        magic_def_aptitude: 法防资质
        level: 当前等级
        realm: 当前境界
        max_realm: 最高可达境界（必须传入真实上限，不再默认天界）
        growth_score: 成长率评分
        nature: 特性(物系/法系/物系善攻/法系善攻/物系高速/法系高速)
        skills: 幻兽技能列表（用于计算增幅技能加成）
    
    返回:
        {hp, speed, physical_attack, magic_attack, 
         physical_defense, magic_defense, combat_power}
    """
    realm_mult = get_realm_multiplier(realm, max_realm)
    growth_mult = get_growth_multiplier(growth_score)
    
    # 计算基础属性（不含增幅技能）
    hp_level_bonus = (level - 1) * 50 * realm_mult * growth_mult
    hp_base = hp_aptitude * 0.102 * realm_mult * growth_mult
    hp_naked = int(hp_base + hp_level_bonus)
    
    base_speed_lv1 = calc_level1_speed_from_aptitude(speed_aptitude)
    speed_level_bonus = (level - 1) * growth_mult * realm_mult * base_speed_lv1
    speed_naked = max(1, int(base_speed_lv1 + speed_level_bonus))
    
    is_good_attack = str(nature).endswith('善攻')
    is_physical = '物系' in str(nature)
    
    # 根据幻兽类型选择对应的攻击资质
    target_atk_aptitude = phys_atk_aptitude if is_physical else magic_atk_aptitude
    
    base_attack_lv1 = max(10, int(target_atk_aptitude * 0.051 * realm_mult * growth_mult))
    
    if is_good_attack:
        atk_level_bonus = (level - 1) * growth_mult * realm_mult * 1.5 * 35
        atk_value_naked = max(10, int(base_attack_lv1 * 1.5 + atk_level_bonus))
    else:
        atk_level_bonus = (level - 1) * growth_mult * realm_mult * 35
        atk_value_naked = max(10, int(base_attack_lv1 + atk_level_bonus))
    
    phys_atk_naked = atk_value_naked if is_physical else 0
    magic_atk_naked = atk_value_naked if not is_physical else 0
    
    is_high_speed = nature in ("物系高速", "法系高速")
    def_level_bonus = (level - 1) * growth_mult * realm_mult * 22
    
    phys_def_lv1 = (phys_def_aptitude or 0) * 0.046 * realm_mult * growth_mult
    magic_def_lv1 = (magic_def_aptitude or 0) * 0.046 * realm_mult * growth_mult
    
    phys_mult = 1.0
    magic_mult = 1.0
    if not is_high_speed:
        if int(phys_def_aptitude or 0) < int(magic_def_aptitude or 0):
            phys_mult = 0.85
        elif int(magic_def_aptitude or 0) < int(phys_def_aptitude or 0):
            magic_mult = 0.85
    
    phys_def_naked = max(10, int((phys_def_lv1 + def_level_bonus) * phys_mult))
    magic_def_naked = max(10, int((magic_def_lv1 + def_level_bonus) * magic_mult))
    
    # 计算增幅技能加成
    buff_bonuses = get_buff_skill_bonuses(skills or [])
    
    # 应用增幅技能加成（基于裸属性）
    hp = int(hp_naked * (1 + buff_bonuses.get('hp', 0.0)))
    speed = int(speed_naked * (1 + buff_bonuses.get('speed', 0.0)))
    phys_atk = int(phys_atk_naked * (1 + buff_bonuses.get('physical_attack', 0.0)))
    magic_atk = int(magic_atk_naked * (1 + buff_bonuses.get('magic_attack', 0.0)))
    phys_def = int(phys_def_naked * (1 + buff_bonuses.get('physical_defense', 0.0)))
    magic_def = int(magic_def_naked * (1 + buff_bonuses.get('magic_defense', 0.0)))
    
    combat_power = (
        round(hp / 9.0906) +
        round(phys_atk / 8.0165) +
        round(magic_atk / 8.0165) +
        round(phys_def / 4.7368) +
        round(magic_def / 4.7368) +
        round(speed / 1)
    )
    
    return {
        "hp": hp,
        "speed": speed,
        "physical_attack": phys_atk,
        "magic_attack": magic_atk,
        "physical_defense": phys_def,
        "magic_defense": magic_def,
        "combat_power": combat_power,
    }


def get_realm_multiplier(current_realm: str, max_realm: str) -> float:
    """根据幻兽当前境界和最高可达境界，计算实际倍率。

    规则：
    - 幻兽的最高境界对应倍率为 1.0
    - 往下每降一级，倍率递减 0.1
    - 例如：最高境界为神界时，神界=1.0，灵界=0.9，地界=0.8
    - 例如：最高境界为灵界时，灵界=1.0，地界=0.9
    - 若 current_realm 不在 REALM_ORDER 中，返回 1.0（容错）
    """
    if current_realm not in REALM_ORDER or max_realm not in REALM_ORDER:
        return 1.0

    max_idx = REALM_ORDER.index(max_realm)
    cur_idx = REALM_ORDER.index(current_realm)

    if cur_idx > max_idx:
        cur_idx = max_idx

    diff = max_idx - cur_idx

    return max(0.1, 1.0 - diff * 0.1)


@dataclass
class BattleStats:
    """战斗用的幻兽属性快照（全部是最终数值）"""

    hp: int                 # 当前总气血（用于战斗起始最大HP）
    physical_attack: int    # 当前物理攻击力
    magic_attack: int       # 当前法术攻击力
    physical_defense: int   # 当前物理防御力
    magic_defense: int      # 当前法术防御力
    speed: int              # 当前速度（决定出手顺序）


@dataclass
class StatBonus:
    """来自装备 / Buff / 副本等的属性加成（统一格式）"""

    hp_flat: int = 0                    # 额外气血固定加成值
    hp_percent: float = 0.0             # 额外气血百分比加成（0.1 = +10%）

    physical_attack_flat: int = 0       # 额外物攻固定加成
    physical_attack_percent: float = 0.0# 额外物攻百分比加成

    magic_attack_flat: int = 0          # 额外法攻固定加成
    magic_attack_percent: float = 0.0   # 额外法攻百分比加成

    physical_defense_flat: int = 0      # 额外物防固定加成
    physical_defense_percent: float = 0.0# 额外物防百分比加成

    magic_defense_flat: int = 0         # 额外法防固定加成
    magic_defense_percent: float = 0.0  # 额外法防百分比加成

    speed_flat: int = 0                 # 额外速度固定加成
    speed_percent: float = 0.0          # 额外速度百分比加成


class BeastStatCalculator:
    """统一负责计算幻兽战斗属性的领域服务。

    流程大致分为三步：
    1. 根据模板 + 等级 + 资质计算基础属性；
    2. 应用装备 / 鼓舞 / 副本等数值加成（StatBonus）；
    3. （在外部）再交给技能系统处理技能效果。
    """

    # ===================== 资质→属性系数 =====================
    HP_COEFF = 0.102           # 1点气血资质 → 0.102 血
    ATK_COEFF = 0.051          # 1点攻击资质 → 0.051 攻
    ATK_COEFF_BONUS = 0.0765   # 善攻系：1点攻击资质 → 0.0765 攻
    DEF_COEFF = 0.046          # 1点防御资质 → 0.046 防
    DEF_COEFF_LOW = 0.0391     # 非高速系较低防御资质 → 0.0391 防
    LEVEL_BONUS = 50           # 每升一级的固定加成基数

    @staticmethod
    def calc_base_stats(
        beast: Beast, template: BeastTemplate, max_realm: str = None
    ) -> BattleStats:
        """只考虑幻兽自身（资质 + 等级 + 境界 + 成长率），不含装备/Buff加成。

        公式：
            属性 = 原始值 + 升级加成
            原始值 = 资质 × 系数 × 境界倍率 × 成长率倍率
            升级加成 = (等级 - 1) × 50 × 境界倍率 × 成长率倍率

        参数:
            beast: 幻兽实例
            template: 幻兽模板
            max_realm: 该幻兽可达到的最高境界（不传则从模板中自动推导）

        返回:
            BattleStats: 计算后的基础属性快照
        """
        # -------- 获取倍率 --------
        current_realm = beast.realm if beast.realm else template.realm
        if not max_realm:
            # 从模板配置中提取实际的最高境界
            max_realm = get_beast_max_realm(template.realms.keys())

        realm_mult = get_realm_multiplier(current_realm, max_realm)

        growth_score = beast.growth_rate if beast.growth_rate else template.growth_score
        growth_mult = get_growth_multiplier(growth_score)

        level_bonus_base = (beast.level - 1) * BeastStatCalculator.LEVEL_BONUS * realm_mult * growth_mult

        # -------- 气血 --------
        # 气血初始值 = 0.102 * 资质 * 境界倍率（不乘成长倍率）
        # 气血最终值 = 初始值 + 等级加成
        hp_base = beast.hp_aptitude * BeastStatCalculator.HP_COEFF * realm_mult
        hp = int(hp_base + level_bonus_base)

        # -------- 攻击（物攻 / 法攻） --------
        personality = template.personality  # 特性来自模板
        attack_type = beast.attack_type if beast.attack_type else template.attack_type

        # 兼容历史值：magical 统一归一化为 magic
        if attack_type == "magical":
            attack_type = "magic"

        # 判断善攻特性
        is_bonus_atk = "善攻" in personality  # 物系善攻 或 法系善攻

        atk_coeff = BeastStatCalculator.ATK_COEFF_BONUS if is_bonus_atk else BeastStatCalculator.ATK_COEFF

        if attack_type == "magic":
            atk_aptitude = beast.magic_atk_aptitude
        else:
            atk_aptitude = beast.physical_atk_aptitude

        atk_base = atk_aptitude * atk_coeff * realm_mult * growth_mult
        attack = int(atk_base + level_bonus_base)

        if attack_type == "magic":
            physical_attack = 0
            magic_attack = attack
        else:
            physical_attack = attack
            magic_attack = 0

        # -------- 防御（物防 / 法防） --------
        is_high_speed = "高速" in personality  # 高速系特性

        phys_def_apt = beast.physical_def_aptitude
        magic_def_apt = beast.magic_def_aptitude

        if is_high_speed:
            # 高速系：两防均使用标准系数
            phys_def_coeff = BeastStatCalculator.DEF_COEFF
            magic_def_coeff = BeastStatCalculator.DEF_COEFF
        else:
            # 非高速系：资质较低的防御使用低系数
            if phys_def_apt < magic_def_apt:
                phys_def_coeff = BeastStatCalculator.DEF_COEFF_LOW
                magic_def_coeff = BeastStatCalculator.DEF_COEFF
            elif magic_def_apt < phys_def_apt:
                phys_def_coeff = BeastStatCalculator.DEF_COEFF
                magic_def_coeff = BeastStatCalculator.DEF_COEFF_LOW
            else:
                # 两防资质相等时均使用标准系数
                phys_def_coeff = BeastStatCalculator.DEF_COEFF
                magic_def_coeff = BeastStatCalculator.DEF_COEFF

        phys_def_base = phys_def_apt * phys_def_coeff * realm_mult * growth_mult
        magic_def_base = magic_def_apt * magic_def_coeff * realm_mult * growth_mult

        physical_defense = int(phys_def_base + level_bonus_base)
        magic_defense = int(magic_def_base + level_bonus_base)

        # -------- 速度 --------
        # 资质 0~1100 → 1速，1100~2200 → 2速，以此类推
        speed_aptitude = beast.speed_aptitude
        speed = max(1, speed_aptitude // 1100 + 1)

        return BattleStats(
            hp=hp,
            physical_attack=physical_attack,
            magic_attack=magic_attack,
            physical_defense=physical_defense,
            magic_defense=magic_defense,
            speed=speed,
        )

    @staticmethod
    def apply_bonuses(base: BattleStats, bonuses: Iterable[StatBonus]) -> BattleStats:
        """在基础属性的基础上应用一组数值加成，返回新的属性快照。"""
        # TODO: 在这里实现 flat / percent 加成的叠加规则
        raise NotImplementedError


# ===================== 资质星级计算（骨架） =====================

def _calc_star_pair(x: int, xmax: int) -> (int, int):
    """根据当前资质值 x 和最大值 xmax 计算 (实心星数, 空心星数)。

    规则约定：
    - 令 Xmin = Xmax - 70 * 5；a = x - Xmin；
    - 0 < a < 350；当 a 可被 70 整除时，全是实心星，数量 = a / 70；
    - 当 a 不可被 70 整除时：
        * 先取 q = a // 70（整除部分），生成 q 颗实心星；
        * 再额外加 1 颗空心星；
        * 若 q 为 0，则只有 1 颗空心星（1 ≤ a < 70）。
    - 最多显示 5 颗星。

    为了健壮性：
    - 若 xmax <= 0，则返回 (0, 0)；
    - 若 x 超出 [Xmin, Xmax] 区间，则先按区间边界进行截断。
    """
    if xmax <= 0:
        return 0, 0

    xmin = xmax - 70 * 5
    # 允许 x 略微偏出范围，这里进行截断
    x_clamped = max(xmin + 1, min(x, xmax))
    a = x_clamped - xmin  # 1 <= a <= 70*5

    # 安全护栏
    if a <= 0:
        return 0, 0
    if a > 70 * 5:
        a = 70 * 5

    q, r = divmod(a, 70)
    if r == 0:
        # 能整除：全部是实心星
        solid = q
        hollow = 0
    else:
        # 不能整除：q 颗实心 + 1 颗空心；若 q 为 0，则只有 1 颗空心
        solid = q if q > 0 else 0
        hollow = 1

    # 最多 5 颗星
    total = solid + hollow
    if total > 5:
        # 优先保留实心星
        overflow = total - 5
        if hollow >= overflow:
            hollow -= overflow
        else:
            overflow -= hollow
            hollow = 0
            solid = max(0, solid - overflow)

    return solid, hollow


def _load_beast_templates_raw():
    """加载原始的幻兽模板配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'configs', 'beast_templates.json'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'templates' in data:
            return data['templates']
        else:
            return []
    except:
        return []


def calc_beast_aptitude_stars(beast_name: str, realm: str, aptitudes: dict) -> dict:
    """根据幻兽名称和境界计算各项资质的星级
    
    aptitudes: {
        'hp': 当前气血资质,
        'speed': 当前速度资质,
        'magic_attack': 当前法攻资质,
        'physical_defense': 当前物防资质,
        'magic_defense': 当前法防资质,
    }
    """
    result = {
        'hp_solid_stars': 0, 'hp_hollow_stars': 1,
        'speed_solid_stars': 0, 'speed_hollow_stars': 1,
        'magic_attack_solid_stars': 0, 'magic_attack_hollow_stars': 1,
        'physical_defense_solid_stars': 0, 'physical_defense_hollow_stars': 1,
        'magic_defense_solid_stars': 0, 'magic_defense_hollow_stars': 1,
    }
    
    templates = _load_beast_templates_raw()
    template_data = None
    for t in templates:
        if t.get('name') == beast_name:
            template_data = t
            break
    
    if not template_data:
        return result
    
    realms = template_data.get('realms', {})
    if not realms or realm not in realms:
        return result
    
    realm_config = realms[realm]
    
    def _calc_star_pair_internal(x: int, xmax: int, xmin: int) -> tuple:
        if xmax <= 0 or xmin < 0:
            return 0, 1
        x_clamped = max(xmin, min(x, xmax))
        a = x_clamped - xmin
        if a <= 0:
            return 0, 1
        q, r = divmod(a, 70)
        if r == 0:
            solid = q
            hollow = 0
        else:
            solid = q
            hollow = 1
        total = solid + hollow
        if total > 5:
            solid = 5
            hollow = 0
        return solid, hollow
    
    hp_max = realm_config.get('hp_aptitude_max', 0)
    hp_min = realm_config.get('hp_aptitude_min', hp_max - 350)
    solid, hollow = _calc_star_pair_internal(aptitudes.get('hp', 0), hp_max, hp_min)
    result['hp_solid_stars'] = solid
    result['hp_hollow_stars'] = hollow
    
    speed_max = realm_config.get('speed_aptitude_max', 0)
    speed_min = realm_config.get('speed_aptitude_min', speed_max - 350)
    solid, hollow = _calc_star_pair_internal(aptitudes.get('speed', 0), speed_max, speed_min)
    result['speed_solid_stars'] = solid
    result['speed_hollow_stars'] = hollow
    
    # 计算攻击资质星级
    is_physical = 'physical_attack' in aptitudes and aptitudes['physical_attack'] > 0
    if is_physical:
        atk_val = aptitudes.get('physical_attack', 0)
        atk_max = realm_config.get('physical_atk_aptitude_max', 0)
        atk_min = realm_config.get('physical_atk_aptitude_min', atk_max - 350)
    else:
        atk_val = aptitudes.get('magic_attack', 0)
        atk_max = realm_config.get('magic_atk_aptitude_max', 0)
        atk_min = realm_config.get('magic_atk_aptitude_min', atk_max - 350)
    
    solid, hollow = _calc_star_pair_internal(atk_val, atk_max, atk_min)
    
    # 统一放回 magic_attack 相关的 key 以保持前端兼容性，或者根据类型放置
    # 前端通常只读 magic_attack_solid_stars 来显示“攻击资质”
    result['magic_attack_solid_stars'] = solid
    result['magic_attack_hollow_stars'] = hollow
    
    # 同时也存一份 physical 以防万一
    result['physical_attack_solid_stars'] = solid
    result['physical_attack_hollow_stars'] = hollow
    
    phys_def_max = realm_config.get('physical_def_aptitude_max', 0)
    phys_def_min = realm_config.get('physical_def_aptitude_min', phys_def_max - 350)
    solid, hollow = _calc_star_pair_internal(aptitudes.get('physical_defense', 0), phys_def_max, phys_def_min)
    result['physical_defense_solid_stars'] = solid
    result['physical_defense_hollow_stars'] = hollow
    
    magic_def_max = realm_config.get('magic_def_aptitude_max', 0)
    magic_def_min = realm_config.get('magic_def_aptitude_min', magic_def_max - 350)
    solid, hollow = _calc_star_pair_internal(aptitudes.get('magic_defense', 0), magic_def_max, magic_def_min)
    result['magic_defense_solid_stars'] = solid
    result['magic_defense_hollow_stars'] = hollow
    
    return result


def calc_max_mosoul_slots(level: int) -> int:
    """根据幻兽等级计算最大魔魂槽位数
    
    规则：
    - 1-10级：1个槽位
    - 11-20级：2个槽位
    - 以此类推，每10级+1
    - 上限：10个槽位
    """
    lv = int(level or 0)
    if lv <= 0:
        return 0
    slots = (lv - 1) // 10 + 1
    return min(10, slots)


def get_beast_equipment_counts(
    beast_id: int,
    beast_level: int,
    mosoul_repo,
    bone_repo,
    spirit_repo
) -> Dict[str, int]:
    """获取幻兽的各类装备数量统计
    
    返回:
        {
            'mosoul_count': 魔魂数量,
            'max_mosoul_slots': 最大魔魂槽位,
            'bone_count': 战骨数量,
            'spirit_count': 战灵数量,
        }
    """
    mosoul_count = mosoul_repo.count_beast_mosouls(beast_id)
    max_mosoul_slots = calc_max_mosoul_slots(beast_level)
    
    equipped_bones = bone_repo.get_by_beast_id(beast_id)
    bone_count = len(equipped_bones) if equipped_bones else 0
    
    equipped_spirits = spirit_repo.get_by_beast_id(beast_id)
    spirit_count = len(equipped_spirits) if equipped_spirits else 0
    
    return {
        'mosoul_count': mosoul_count,
        'max_mosoul_slots': max_mosoul_slots,
        'bone_count': bone_count,
        'spirit_count': spirit_count,
    }


def calc_aptitude_stars(beast: Beast, template: BeastTemplate) -> Dict[str, int]:
    """根据实例资质和模板资质上限，计算各项资质对应的星级信息。

    返回的字典中包含：
        - 每项资质的实心星数 / 空心星数，例如：
            hp_solid_stars, hp_hollow_stars,
            speed_solid_stars, speed_hollow_stars,
            physical_atk_solid_stars, physical_atk_hollow_stars,
            physical_def_solid_stars, physical_def_hollow_stars,
            magic_def_solid_stars, magic_def_hollow_stars;
        - 成长率星级：growth_solid_stars, growth_hollow_stars
          （当前规则：固定 5 颗实心星）。
    """
    result: Dict[str, int] = {}

    def _calc_star_pair_by_minmax(x: int, xmin: int, xmax: int) -> (int, int):
        if xmax <= 0 or xmin < 0:
            return 0, 1
        x_clamped = max(xmin, min(int(x or 0), int(xmax)))
        a = x_clamped - int(xmin)
        if a <= 0:
            return 0, 1
        q, r = divmod(a, 70)
        if r == 0:
            solid = q
            hollow = 0
        else:
            solid = q
            hollow = 1
        total = solid + hollow
        if total > 5:
            return 5, 0
        return solid, hollow

    current_realm = (beast.realm or template.realm or "地界")
    realm_cfg = template.realms.get(current_realm, {}) if isinstance(template.realms, dict) else {}

    def _get_minmax(min_key: str, max_key: str, fallback_max: int) -> (int, int):
        xmax = realm_cfg.get(max_key)
        if xmax is None:
            xmax = fallback_max
        try:
            xmax = int(xmax or 0)
        except (TypeError, ValueError):
            xmax = int(fallback_max or 0)

        xmin = realm_cfg.get(min_key)
        try:
            xmin = int(xmin) if xmin is not None else max(0, xmax - 350)
        except (TypeError, ValueError):
            xmin = max(0, xmax - 350)

        return xmin, xmax

    # HP 资质星级
    hp_min, hp_max = _get_minmax("hp_aptitude_min", "hp_aptitude_max", template.hp_aptitude_max)
    solid, hollow = _calc_star_pair_by_minmax(beast.hp_aptitude, hp_min, hp_max)
    result["hp_solid_stars"] = solid
    result["hp_hollow_stars"] = hollow

    # 速度资质星级
    speed_min, speed_max = _get_minmax("speed_aptitude_min", "speed_aptitude_max", template.speed_aptitude_max)
    solid, hollow = _calc_star_pair_by_minmax(beast.speed_aptitude, speed_min, speed_max)
    result["speed_solid_stars"] = solid
    result["speed_hollow_stars"] = hollow

    # 攻击资质星级（根据攻击类型选择物攻/法攻）
    atk_type = (beast.attack_type or template.attack_type or "physical")
    if atk_type == "magical":
        atk_type = "magic"
    is_physical = str(atk_type).lower() == "physical"
    if is_physical:
        atk_min, atk_max = _get_minmax(
            "physical_atk_aptitude_min",
            "physical_atk_aptitude_max",
            template.physical_atk_aptitude_max,
        )
        solid, hollow = _calc_star_pair_by_minmax(beast.physical_atk_aptitude, atk_min, atk_max)
    else:
        atk_min, atk_max = _get_minmax(
            "magic_atk_aptitude_min",
            "magic_atk_aptitude_max",
            template.magic_atk_aptitude_max,
        )
        solid, hollow = _calc_star_pair_by_minmax(beast.magic_atk_aptitude, atk_min, atk_max)
    result["physical_atk_solid_stars"] = solid
    result["physical_atk_hollow_stars"] = hollow

    # 物防资质星级
    pdef_min, pdef_max = _get_minmax(
        "physical_def_aptitude_min",
        "physical_def_aptitude_max",
        template.physical_def_aptitude_max,
    )
    solid, hollow = _calc_star_pair_by_minmax(beast.physical_def_aptitude, pdef_min, pdef_max)
    result["physical_def_solid_stars"] = solid
    result["physical_def_hollow_stars"] = hollow

    # 法防资质星级
    mdef_min, mdef_max = _get_minmax(
        "magic_def_aptitude_min",
        "magic_def_aptitude_max",
        template.magic_def_aptitude_max,
    )
    solid, hollow = _calc_star_pair_by_minmax(beast.magic_def_aptitude, mdef_min, mdef_max)
    result["magic_def_solid_stars"] = solid
    result["magic_def_hollow_stars"] = hollow

    # 成长率星级：按需求，固定返回 5 颗实心星
    result["growth_solid_stars"] = 5
    result["growth_hollow_stars"] = 0

    return result


STAT_ATTRS = ["hp", "physical_attack", "magic_attack", "physical_defense", "magic_defense", "speed"]


def calc_total_stats_with_bonus(
    base_stats: Dict[str, int],
    spirit_bonus: Dict[str, int],
    bone_bonus: Dict[str, int],
    mosoul_bonus: Dict[str, int]
) -> Dict[str, int]:
    """计算幻兽总属性（基础 + 战灵 + 战骨 + 魔魂）并计算战力
    
    Args:
        base_stats: 基础属性
        spirit_bonus: 战灵加成
        bone_bonus: 战骨加成
        mosoul_bonus: 魔魂加成
    
    Returns:
        包含总属性和战力的字典
    """
    total = {}
    for attr in STAT_ATTRS:
        total[attr] = (
            base_stats.get(attr, 0) +
            spirit_bonus.get(attr, 0) +
            bone_bonus.get(attr, 0) +
            mosoul_bonus.get(attr, 0)
        )
    
    total["combat_power"] = (
        round(total["hp"] / 9.0906) +
        round(total["physical_attack"] / 8.0165) +
        round(total["magic_attack"] / 8.0165) +
        round(total["physical_defense"] / 4.7368) +
        round(total["magic_defense"] / 4.7368) +
        round(total["speed"] / 1)
    )
    return total


def calc_aptitude_boost(beast_name: str, old_realm: str, new_realm: str) -> Dict[str, int]:
    """计算进化时的资质提升
    
    Args:
        beast_name: 幻兽名称
        old_realm: 旧境界
        new_realm: 新境界
    
    Returns:
        各项资质的提升值字典：
        {
            'hp_aptitude': 气血资质提升,
            'speed_aptitude': 速度资质提升,
            'physical_atk_aptitude': 物攻资质提升,
            'magic_atk_aptitude': 法攻资质提升,
            'physical_def_aptitude': 物防资质提升,
            'magic_def_aptitude': 法防资质提升,
        }
    """
    boosts = {
        'hp_aptitude': 0,
        'speed_aptitude': 0,
        'physical_atk_aptitude': 0,
        'magic_atk_aptitude': 0,
        'physical_def_aptitude': 0,
        'magic_def_aptitude': 0,
    }
    
    templates = _load_beast_templates_raw()
    template_data = None
    for t in templates:
        if t.get('name') == beast_name:
            template_data = t
            break
    
    if not template_data:
        return boosts
    
    realms = template_data.get('realms', {})
    if old_realm not in realms or new_realm not in realms:
        return boosts
    
    old_realm_config = realms[old_realm]
    new_realm_config = realms[new_realm]
    
    aptitude_fields = [
        'hp_aptitude',
        'speed_aptitude',
        'physical_atk_aptitude',
        'magic_atk_aptitude',
        'physical_def_aptitude',
        'magic_def_aptitude',
    ]
    
    for field in aptitude_fields:
        max_key = f'{field}_max'
        old_max = old_realm_config.get(max_key, 0)
        new_max = new_realm_config.get(max_key, 0)
        max_boost = new_max - old_max
        
        if max_boost > 0:
            boosts[field] = random.randint(1, max_boost)
    
    return boosts
