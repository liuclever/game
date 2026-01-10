"""tests/init_beast/test_beast_stats.py

测试幻兽初始属性计算是否正确，并展示每个属性的详细计算流程和代码位置。

运行方式（在项目根目录）：
    python -m tests.init_beast.test_beast_stats
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from dataclasses import dataclass
from typing import Optional


# ===================== 配置读取 =====================

def load_growth_multipliers() -> dict:
    """读取成长率倍率配置"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "configs", "growth_rate_multipliers.json"
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {int(k): v for k, v in data.get("growth_score_to_multiplier", {}).items()}


# ===================== 测试用幻兽数据结构 =====================

@dataclass
class TestBeast:
    """测试用幻兽数据"""
    name: str = "测试幻兽"
    level: int = 1
    realm: str = "地界"
    growth_rate: int = 840
    nature: str = ""
    hp_aptitude: int = 0
    speed_aptitude: int = 0
    physical_attack_aptitude: int = 0
    magic_attack_aptitude: int = 0
    physical_defense_aptitude: int = 0
    magic_defense_aptitude: int = 0
    hp: int = 0
    speed: int = 0
    physical_attack: int = 0
    magic_attack: int = 0
    physical_defense: int = 0
    magic_defense: int = 0
    combat_power: int = 0


# ===================== 属性计算详解类 =====================

class BeastStatsCalculator:
    """幻兽属性计算器，带详细流程输出"""
    
    REALM_MULTIPLIERS = {"地界": 0.8, "灵界": 0.85, "神界": 0.9, "天界": 1.0}
    
    def __init__(self, beast: TestBeast):
        self.beast = beast
        self.growth_multipliers = load_growth_multipliers()
        self.logs = []
    
    def log(self, msg: str):
        self.logs.append(msg)
        print(msg)
    
    def print_separator(self, title: str = ""):
        sep = "=" * 60
        if title:
            self.log(f"\n{sep}\n{title}\n{sep}")
        else:
            self.log(f"\n{sep}")
    
    def calculate_all(self) -> TestBeast:
        """计算所有属性并输出详细流程"""
        self.print_separator("幻兽属性计算详解")
        
        self.log(f"\n【输入参数】")
        self.log(f"  幻兽名称: {self.beast.name}")
        self.log(f"  等级: {self.beast.level}")
        self.log(f"  境界: {self.beast.realm}")
        self.log(f"  成长率: {self.beast.growth_rate}")
        self.log(f"  特性: {self.beast.nature}")
        self.log(f"  气血资质: {self.beast.hp_aptitude}")
        self.log(f"  速度资质: {self.beast.speed_aptitude}")
        self.log(f"  法攻资质: {self.beast.magic_attack_aptitude}")
        self.log(f"  物防资质: {self.beast.physical_defense_aptitude}")
        self.log(f"  法防资质: {self.beast.magic_defense_aptitude}")
        
        # 第一步：境界倍率
        realm_mult = self._calc_realm_multiplier()
        
        # 第二步：成长倍率
        growth_mult = self._calc_growth_multiplier()
        
        # 第三步：等级加成
        level_bonus = self._calc_level_bonus(realm_mult, growth_mult)
        
        # 第四步：判断攻击类型
        attack_type = self._determine_attack_type()
        
        # 第五步：计算气血
        self._calc_hp(realm_mult, level_bonus)
        
        # 第六步：计算速度
        self._calc_speed(realm_mult, growth_mult)
        
        # 第七步：计算防御
        self._calc_defense(realm_mult, growth_mult)
        
        # 第八步：计算攻击
        self._calc_attack(realm_mult, growth_mult, attack_type)
        
        # 第九步：计算战力
        self._calc_combat_power()
        
        # 输出最终结果
        self._print_result()
        
        return self.beast
    
    def _calc_realm_multiplier(self) -> float:
        """第一步：获取境界倍率"""
        self.print_separator("第一步：获取境界倍率")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第827-829行")
        self.log(f"【代码内容】")
        self.log(f'  realm_multipliers = {{"地界": 0.8, "灵界": 0.85, "神界": 0.9, "天界": 1.0}}')
        self.log(f'  realm_mult = realm_multipliers.get(beast.realm, 0.8)')
        self.log(f"【计算过程】")
        realm_mult = self.REALM_MULTIPLIERS.get(self.beast.realm, 0.8)
        self.log(f"  境界 = {self.beast.realm}")
        self.log(f"  realm_mult = {realm_mult}")
        return realm_mult
    
    def _calc_growth_multiplier(self) -> float:
        """第二步：获取成长倍率"""
        self.print_separator("第二步：获取成长倍率")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第775-794行 _get_growth_multiplier()")
        self.log(f"【配置文件】configs/growth_rate_multipliers.json")
        self.log(f"【查找规则】找到不超过 growth_score 的最大键对应的倍率")
        self.log(f"【计算过程】")
        
        growth_score = self.beast.growth_rate or 840
        sorted_keys = sorted(self.growth_multipliers.keys())
        result_mult = self.growth_multipliers[sorted_keys[0]]
        
        for key in sorted_keys:
            if key <= growth_score:
                result_mult = self.growth_multipliers[key]
                self.log(f"  成长率 {growth_score} >= {key}，暂取倍率 = {result_mult}")
            else:
                break
        
        self.log(f"【结果】growth_mult = {result_mult}")
        return result_mult
    
    def _calc_level_bonus(self, realm_mult: float, growth_mult: float) -> float:
        """第三步：计算等级加成"""
        self.print_separator("第三步：计算等级加成")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第835-837行")
        self.log(f"【公式】level_bonus = (等级 - 1) × 50 × 境界倍率 × 成长倍率")
        self.log(f"【计算过程】")
        level_bonus = (self.beast.level - 1) * 50 * realm_mult * growth_mult
        self.log(f"  level_bonus = ({self.beast.level} - 1) × 50 × {realm_mult} × {growth_mult}")
        self.log(f"             = {self.beast.level - 1} × 50 × {realm_mult} × {growth_mult}")
        self.log(f"             = {level_bonus}")
        return level_bonus
    
    def _determine_attack_type(self) -> str:
        """第四步：判断攻击类型"""
        self.print_separator("第四步：判断攻击类型")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第839-847行")
        self.log(f"【规则】特性包含'物系'则为物理攻击，否则为法术攻击")
        self.log(f"【计算过程】")
        nature = self.beast.nature or ''
        if '物系' in nature:
            attack_type = "physical"
            self.log(f"  特性 = '{nature}' 包含 '物系'")
        else:
            attack_type = "magic"
            self.log(f"  特性 = '{nature}' 不包含 '物系'")
        self.log(f"【结果】attack_type = {attack_type}")
        return attack_type
    
    def _calc_hp(self, realm_mult: float, level_bonus: float):
        """第五步：计算气血"""
        self.print_separator("第五步：计算气血 (HP)")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第850-853行")
        self.log(f"【公式】")
        self.log(f"  hp_base = 气血资质 × 0.102 × 境界倍率")
        self.log(f"  hp = int(hp_base + level_bonus)")
        self.log(f"【计算过程】")
        hp_base = self.beast.hp_aptitude * 0.102 * realm_mult
        self.log(f"  hp_base = {self.beast.hp_aptitude} × 0.102 × {realm_mult}")
        self.log(f"          = {hp_base:.4f}")
        self.beast.hp = int(hp_base + level_bonus)
        self.log(f"  hp = int({hp_base:.4f} + {level_bonus})")
        self.log(f"     = int({hp_base + level_bonus:.4f})")
        self.log(f"     = {self.beast.hp}")
    
    def _calc_speed(self, realm_mult: float, growth_mult: float):
        """第六步：计算速度"""
        self.print_separator("第六步：计算速度 (Speed)")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第807-815行, 第855-860行")
        self.log(f"【步骤6.1】计算1级初始速度（资质分档）")
        self.log(f"【函数】_calc_level1_speed_from_aptitude()")
        self.log(f"【分档规则】每1100资质为一档：0-1100→1, 1101-2200→2, 2201-3300→3...")
        self.log(f"【公式】base_speed_lv1 = max(1, (speed_aptitude + 1099) // 1100)")
        self.log(f"【计算过程】")
        
        sa = self.beast.speed_aptitude or 0
        base_speed_lv1 = max(1, (sa + 1099) // 1100)
        self.log(f"  base_speed_lv1 = max(1, ({sa} + 1099) // 1100)")
        self.log(f"                 = max(1, {sa + 1099} // 1100)")
        self.log(f"                 = max(1, {(sa + 1099) // 1100})")
        self.log(f"                 = {base_speed_lv1}")
        
        self.log(f"\n【步骤6.2】计算速度等级加成")
        self.log(f"【公式】speed_level_bonus = (等级 - 1) × 成长倍率 × 境界倍率 × base_speed_lv1")
        speed_level_bonus = (self.beast.level - 1) * growth_mult * realm_mult * base_speed_lv1
        self.log(f"  speed_level_bonus = ({self.beast.level} - 1) × {growth_mult} × {realm_mult} × {base_speed_lv1}")
        self.log(f"                    = {speed_level_bonus}")
        
        self.log(f"\n【步骤6.3】计算最终速度")
        self.log(f"【公式】speed = max(1, int(base_speed_lv1 + speed_level_bonus))")
        self.beast.speed = max(1, int(base_speed_lv1 + speed_level_bonus))
        self.log(f"  speed = max(1, int({base_speed_lv1} + {speed_level_bonus}))")
        self.log(f"        = max(1, int({base_speed_lv1 + speed_level_bonus}))")
        self.log(f"        = {self.beast.speed}")
    
    def _calc_defense(self, realm_mult: float, growth_mult: float):
        """第七步：计算防御"""
        self.print_separator("第七步：计算防御 (物防/法防)")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第862-883行")
        
        self.log(f"\n【步骤7.1】判断是否高速系")
        nature = self.beast.nature or ''
        is_high_speed = nature in ("物系高速", "法系高速")
        self.log(f"  特性 = '{nature}'")
        self.log(f"  is_high_speed = {is_high_speed}")
        
        self.log(f"\n【步骤7.2】计算防御等级加成")
        self.log(f"【公式】def_level_bonus = (等级 - 1) × 成长倍率 × 境界倍率 × 22")
        def_level_bonus = (self.beast.level - 1) * growth_mult * realm_mult * 22
        self.log(f"  def_level_bonus = ({self.beast.level} - 1) × {growth_mult} × {realm_mult} × 22")
        self.log(f"                  = {def_level_bonus}")
        
        self.log(f"\n【步骤7.3】计算1级防御初始值")
        self.log(f"【公式】def_lv1 = 防御资质 × 0.046 × 境界倍率 × 成长倍率")
        phys_def_lv1 = (self.beast.physical_defense_aptitude or 0) * 0.046 * realm_mult * growth_mult
        magic_def_lv1 = (self.beast.magic_defense_aptitude or 0) * 0.046 * realm_mult * growth_mult
        self.log(f"  phys_def_lv1 = {self.beast.physical_defense_aptitude} × 0.046 × {realm_mult} × {growth_mult}")
        self.log(f"               = {phys_def_lv1:.4f}")
        self.log(f"  magic_def_lv1 = {self.beast.magic_defense_aptitude} × 0.046 × {realm_mult} × {growth_mult}")
        self.log(f"                = {magic_def_lv1:.4f}")
        
        self.log(f"\n【步骤7.4】计算防御惩罚系数（非高速系适用）")
        phys_mult = 1.0
        magic_mult = 1.0
        if not is_high_speed:
            phys_apt = self.beast.physical_defense_aptitude or 0
            magic_apt = self.beast.magic_defense_aptitude or 0
            if phys_apt < magic_apt:
                phys_mult = 0.85
                self.log(f"  物防资质({phys_apt}) < 法防资质({magic_apt})，物防打85折")
            elif magic_apt < phys_apt:
                magic_mult = 0.85
                self.log(f"  法防资质({magic_apt}) < 物防资质({phys_apt})，法防打85折")
            else:
                self.log(f"  物防资质({phys_apt}) = 法防资质({magic_apt})，无惩罚")
        else:
            self.log(f"  高速系，无惩罚")
        self.log(f"  phys_mult = {phys_mult}, magic_mult = {magic_mult}")
        
        self.log(f"\n【步骤7.5】计算最终防御")
        self.log(f"【公式】defense = max(10, int((def_lv1 + def_level_bonus) × mult))")
        
        self.beast.physical_defense = max(10, int((phys_def_lv1 + def_level_bonus) * phys_mult))
        self.log(f"  physical_defense = max(10, int(({phys_def_lv1:.4f} + {def_level_bonus}) × {phys_mult}))")
        self.log(f"                   = max(10, int({(phys_def_lv1 + def_level_bonus) * phys_mult:.4f}))")
        self.log(f"                   = {self.beast.physical_defense}")
        
        self.beast.magic_defense = max(10, int((magic_def_lv1 + def_level_bonus) * magic_mult))
        self.log(f"  magic_defense = max(10, int(({magic_def_lv1:.4f} + {def_level_bonus}) × {magic_mult}))")
        self.log(f"                = max(10, int({(magic_def_lv1 + def_level_bonus) * magic_mult:.4f}))")
        self.log(f"                = {self.beast.magic_defense}")
    
    def _calc_attack(self, realm_mult: float, growth_mult: float, attack_type: str):
        """第八步：计算攻击"""
        self.print_separator("第八步：计算攻击 (物攻/法攻)")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第885-906行")
        
        self.log(f"\n【步骤8.1】判断是否善攻")
        nature = self.beast.nature or ''
        is_good_attack = str(nature).endswith('善攻')
        self.log(f"  特性 = '{nature}'")
        self.log(f"  is_good_attack = {is_good_attack} (特性是否以'善攻'结尾)")
        
        self.log(f"\n【步骤8.2】计算1级攻击初始值")
        self.log(f"【公式】base_attack_lv1 = max(10, int(攻击资质 × 0.051 × 境界倍率 × 成长倍率))")
        atk_aptitude = self.beast.magic_attack_aptitude if attack_type == "magic" else self.beast.physical_attack_aptitude
        base_attack_lv1 = max(10, int(atk_aptitude * 0.051 * realm_mult * growth_mult))
        self.log(f"  攻击资质 = {atk_aptitude} ({'法攻' if attack_type == 'magic' else '物攻'})")
        self.log(f"  base_attack_lv1 = max(10, int({atk_aptitude} × 0.051 × {realm_mult} × {growth_mult}))")
        self.log(f"                  = max(10, int({atk_aptitude * 0.051 * realm_mult * growth_mult:.4f}))")
        self.log(f"                  = {base_attack_lv1}")
        
        self.log(f"\n【步骤8.3】计算攻击值")
        if is_good_attack:
            self.log(f"  [善攻特性公式]")
            self.log(f"  【公式】atk_level_bonus = (等级 - 1) × 成长倍率 × 境界倍率 × 1.5 × 35")
            atk_level_bonus = (self.beast.level - 1) * growth_mult * realm_mult * 1.5 * 35
            self.log(f"  atk_level_bonus = ({self.beast.level} - 1) × {growth_mult} × {realm_mult} × 1.5 × 35")
            self.log(f"                  = {atk_level_bonus}")
            self.log(f"  【公式】atk_value = max(10, int(base_attack_lv1 × 1.5 + atk_level_bonus))")
            atk_value = max(10, int(base_attack_lv1 * 1.5 + atk_level_bonus))
            self.log(f"  atk_value = max(10, int({base_attack_lv1} × 1.5 + {atk_level_bonus}))")
            self.log(f"            = max(10, int({base_attack_lv1 * 1.5 + atk_level_bonus}))")
            self.log(f"            = {atk_value}")
        else:
            self.log(f"  [非善攻公式]")
            level_bonus = (self.beast.level - 1) * 50 * realm_mult * growth_mult
            self.log(f"  【公式】atk_value = max(10, int(攻击资质 × 0.051 × 境界倍率 × 成长倍率 + level_bonus))")
            atk_value = max(10, int(atk_aptitude * 0.051 * realm_mult * growth_mult + level_bonus))
            self.log(f"  atk_value = max(10, int({atk_aptitude} × 0.051 × {realm_mult} × {growth_mult} + {level_bonus}))")
            self.log(f"            = max(10, int({atk_aptitude * 0.051 * realm_mult * growth_mult + level_bonus:.4f}))")
            self.log(f"            = {atk_value}")
        
        self.log(f"\n【步骤8.4】根据攻击类型分配")
        if attack_type == "physical":
            self.beast.physical_attack = atk_value
            self.beast.magic_attack = 0
            self.log(f"  attack_type = physical")
            self.log(f"  physical_attack = {atk_value}")
            self.log(f"  magic_attack = 0")
        else:
            self.beast.magic_attack = atk_value
            self.beast.physical_attack = 0
            self.log(f"  attack_type = magic")
            self.log(f"  magic_attack = {atk_value}")
            self.log(f"  physical_attack = 0")
    
    def _calc_combat_power(self):
        """第九步：计算战力"""
        self.print_separator("第九步：计算综合战力 (combat_power)")
        self.log(f"【代码位置】interfaces/routes/beast_routes.py 第908-917行")
        self.log(f"【公式】")
        self.log(f"  战力 = round(气血 / 9.0906)")
        self.log(f"       + round(物攻 / 8.0165)")
        self.log(f"       + round(法攻 / 8.0165)")
        self.log(f"       + round(物防 / 4.7368)")
        self.log(f"       + round(法防 / 4.7368)")
        self.log(f"       + round(速度 / 1)")
        self.log(f"\n【换算比例】")
        self.log(f"  1点战力 = 9.0906点气血")
        self.log(f"  1点战力 = 8.0165点攻击")
        self.log(f"  1点战力 = 4.7368点防御")
        self.log(f"  1点战力 = 1点速度")
        self.log(f"\n【计算过程】")
        
        hp_power = round(self.beast.hp / 9.0906)
        phys_atk_power = round(self.beast.physical_attack / 8.0165)
        magic_atk_power = round(self.beast.magic_attack / 8.0165)
        phys_def_power = round(self.beast.physical_defense / 4.7368)
        magic_def_power = round(self.beast.magic_defense / 4.7368)
        speed_power = round(self.beast.speed / 1)
        
        self.log(f"  气血贡献 = round({self.beast.hp} / 9.0906) = {hp_power}")
        self.log(f"  物攻贡献 = round({self.beast.physical_attack} / 8.0165) = {phys_atk_power}")
        self.log(f"  法攻贡献 = round({self.beast.magic_attack} / 8.0165) = {magic_atk_power}")
        self.log(f"  物防贡献 = round({self.beast.physical_defense} / 4.7368) = {phys_def_power}")
        self.log(f"  法防贡献 = round({self.beast.magic_defense} / 4.7368) = {magic_def_power}")
        self.log(f"  速度贡献 = round({self.beast.speed} / 1) = {speed_power}")
        
        self.beast.combat_power = hp_power + phys_atk_power + magic_atk_power + phys_def_power + magic_def_power + speed_power
        self.log(f"\n  总战力 = {hp_power} + {phys_atk_power} + {magic_atk_power} + {phys_def_power} + {magic_def_power} + {speed_power}")
        self.log(f"         = {self.beast.combat_power}")
    
    def _print_result(self):
        """输出最终结果"""
        self.print_separator("最终计算结果")
        self.log(f"  气血 (HP): {self.beast.hp}")
        self.log(f"  物攻 (Physical Attack): {self.beast.physical_attack}")
        self.log(f"  法攻 (Magic Attack): {self.beast.magic_attack}")
        self.log(f"  物防 (Physical Defense): {self.beast.physical_defense}")
        self.log(f"  法防 (Magic Defense): {self.beast.magic_defense}")
        self.log(f"  速度 (Speed): {self.beast.speed}")
        self.log(f"  战力 (Combat Power): {self.beast.combat_power}")


# ===================== 测试用例 =====================

def test_example_beast():
    """测试圣灵蚁-地界的属性计算"""
    print("\n" + "=" * 60)
    print("测试案例：圣灵蚁-地界 (根据BEAST_STATS_CALCULATION.md文档)")
    print("=" * 60)
    
    beast = TestBeast(
        name="圣灵蚁-地界",
        level=1,
        realm="地界",
        growth_rate=1440,
        nature="法系善攻",
        hp_aptitude=1177,
        speed_aptitude=1241,
        magic_attack_aptitude=1425,
        physical_defense_aptitude=723,
        magic_defense_aptitude=1146,
    )
    
    calculator = BeastStatsCalculator(beast)
    result = calculator.calculate_all()
    
    # 验证结果
    expected = {
        "hp": 96,
        "magic_attack": 75,
        "physical_attack": 0,
        "physical_defense": 19,
        "magic_defense": 36,
        "speed": 2,
        "combat_power": 34,
    }
    
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    all_pass = True
    for attr, expected_val in expected.items():
        actual_val = getattr(result, attr)
        status = "[PASS]" if actual_val == expected_val else "[FAIL]"
        if actual_val != expected_val:
            all_pass = False
        print(f"  {attr}: 期望={expected_val}, 实际={actual_val} {status}")
    
    print("\n" + ("所有属性验证通过！" if all_pass else "部分属性验证失败！"))
    return all_pass


def test_custom_beast(name: str, level: int, realm: str, growth_rate: int, nature: str,
                      hp_apt: int, speed_apt: int, magic_atk_apt: int, 
                      phys_def_apt: int, magic_def_apt: int):
    """测试自定义幻兽"""
    beast = TestBeast(
        name=name,
        level=level,
        realm=realm,
        growth_rate=growth_rate,
        nature=nature,
        hp_aptitude=hp_apt,
        speed_aptitude=speed_apt,
        magic_attack_aptitude=magic_atk_apt,
        physical_defense_aptitude=phys_def_apt,
        magic_defense_aptitude=magic_def_apt,
    )
    
    calculator = BeastStatsCalculator(beast)
    return calculator.calculate_all()


def main():
    """主函数"""
    print("=" * 60)
    print("幻兽属性计算测试脚本")
    print("=" * 60)
    print("\n此脚本用于测试幻兽初始属性计算是否正确")
    print("并展示每个属性的详细计算流程和代码位置")
    print("\n核心代码位置：")
    print("  - interfaces/routes/beast_routes.py 第818行 _calc_beast_stats()")
    print("  - interfaces/routes/beast_routes.py 第775行 _get_growth_multiplier()")
    print("  - interfaces/routes/beast_routes.py 第807行 _calc_level1_speed_from_aptitude()")
    print("  - configs/growth_rate_multipliers.json (成长率配置)")
    
    # 运行默认测试案例
    test_example_beast()
    
    # 可以在这里添加更多测试案例
    # test_custom_beast("测试幻兽", 10, "灵界", 1240, "物系善攻", 1000, 1000, 1000, 800, 800)


if __name__ == "__main__":
    main()
