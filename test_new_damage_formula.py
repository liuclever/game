"""测试新的幻兽战斗扣血公式

新规则（2026年1月修订）：
- 第一种情况（攻击 - 防御 >= 0）：对方扣血 = (攻击差) × 0.069，四舍五入
- 第二种情况（攻击 - 防御 < 0）：对方固定扣血 5 点
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from domain.services.pvp_battle_engine import PvpBeast, calc_damage


def test_damage_formula():
    """测试新的扣血公式"""
    
    print("=" * 80)
    print("测试新的幻兽战斗扣血公式")
    print("=" * 80)
    
    # 测试用例1：物攻 - 物防 > 0 的情况
    print("\n【测试用例1】物攻 - 物防 > 0")
    print("-" * 80)
    
    attacker1 = PvpBeast(
        id=1,
        name="测试幻兽A",
        hp_max=1000,
        hp_current=1000,
        physical_attack=500,
        magic_attack=0,
        physical_defense=100,
        magic_defense=100,
        speed=100,
        attack_type="physical"
    )
    
    defender1 = PvpBeast(
        id=2,
        name="测试幻兽B",
        hp_max=1000,
        hp_current=1000,
        physical_attack=200,
        magic_attack=0,
        physical_defense=200,
        magic_defense=200,
        speed=80,
        attack_type="physical"
    )
    
    damage1 = calc_damage(attacker1, defender1, 30)
    expected1 = round((attacker1.physical_attack - defender1.physical_defense) * 0.069)
    
    print(f"攻击方物攻: {attacker1.physical_attack}")
    print(f"防御方物防: {defender1.physical_defense}")
    print(f"攻击差: {attacker1.physical_attack - defender1.physical_defense}")
    print(f"计算公式: ({attacker1.physical_attack} - {defender1.physical_defense}) × 0.069 = {(attacker1.physical_attack - defender1.physical_defense) * 0.069}")
    print(f"四舍五入后: {expected1}")
    print(f"实际扣血: {damage1}")
    print(f"测试结果: {'✅ 通过' if damage1 == expected1 else '❌ 失败'}")
    
    # 测试用例2：法攻 - 法防 > 0 的情况
    print("\n【测试用例2】法攻 - 法防 > 0")
    print("-" * 80)
    
    attacker2 = PvpBeast(
        id=3,
        name="测试幻兽C",
        hp_max=1000,
        hp_current=1000,
        physical_attack=0,
        magic_attack=600,
        physical_defense=100,
        magic_defense=100,
        speed=100,
        attack_type="magic"
    )
    
    defender2 = PvpBeast(
        id=4,
        name="测试幻兽D",
        hp_max=1000,
        hp_current=1000,
        physical_attack=200,
        magic_attack=0,
        physical_defense=200,
        magic_defense=250,
        speed=80,
        attack_type="physical"
    )
    
    damage2 = calc_damage(attacker2, defender2, 30)
    expected2 = round((attacker2.magic_attack - defender2.magic_defense) * 0.069)
    
    print(f"攻击方法攻: {attacker2.magic_attack}")
    print(f"防御方法防: {defender2.magic_defense}")
    print(f"攻击差: {attacker2.magic_attack - defender2.magic_defense}")
    print(f"计算公式: ({attacker2.magic_attack} - {defender2.magic_defense}) × 0.069 = {(attacker2.magic_attack - defender2.magic_defense) * 0.069}")
    print(f"四舍五入后: {expected2}")
    print(f"实际扣血: {damage2}")
    print(f"测试结果: {'✅ 通过' if damage2 == expected2 else '❌ 失败'}")
    
    # 测试用例3：攻击 - 防御 < 0 的情况
    print("\n【测试用例3】攻击 - 防御 < 0（固定扣血5点）")
    print("-" * 80)
    
    attacker3 = PvpBeast(
        id=5,
        name="测试幻兽E",
        hp_max=1000,
        hp_current=1000,
        physical_attack=100,
        magic_attack=0,
        physical_defense=100,
        magic_defense=100,
        speed=100,
        attack_type="physical"
    )
    
    defender3 = PvpBeast(
        id=6,
        name="测试幻兽F",
        hp_max=1000,
        hp_current=1000,
        physical_attack=200,
        magic_attack=0,
        physical_defense=500,
        magic_defense=500,
        speed=80,
        attack_type="physical"
    )
    
    damage3 = calc_damage(attacker3, defender3, 30)
    expected3 = 5  # 固定扣血 5 点
    
    print(f"攻击方物攻: {attacker3.physical_attack}")
    print(f"防御方物防: {defender3.physical_defense}")
    print(f"攻击差: {attacker3.physical_attack - defender3.physical_defense}")
    print(f"计算规则: 攻击差 < 0，固定扣血 5 点")
    print(f"实际扣血: {damage3}")
    print(f"测试结果: {'✅ 通过' if damage3 == expected3 else '❌ 失败'}")
    
    # 测试用例4：攻击 - 防御 = 0 的边界情况
    print("\n【测试用例4】攻击 - 防御 = 0（边界情况）")
    print("-" * 80)
    
    attacker4 = PvpBeast(
        id=7,
        name="测试幻兽G",
        hp_max=1000,
        hp_current=1000,
        physical_attack=300,
        magic_attack=0,
        physical_defense=100,
        magic_defense=100,
        speed=100,
        attack_type="physical"
    )
    
    defender4 = PvpBeast(
        id=8,
        name="测试幻兽H",
        hp_max=1000,
        hp_current=1000,
        physical_attack=200,
        magic_attack=0,
        physical_defense=300,
        magic_defense=300,
        speed=80,
        attack_type="physical"
    )
    
    damage4 = calc_damage(attacker4, defender4, 30)
    expected4 = max(1, round((attacker4.physical_attack - defender4.physical_defense) * 0.069))
    
    print(f"攻击方物攻: {attacker4.physical_attack}")
    print(f"防御方物防: {defender4.physical_defense}")
    print(f"攻击差: {attacker4.physical_attack - defender4.physical_defense}")
    print(f"计算公式: ({attacker4.physical_attack} - {defender4.physical_defense}) × 0.069 = {(attacker4.physical_attack - defender4.physical_defense) * 0.069}")
    print(f"四舍五入后: {round((attacker4.physical_attack - defender4.physical_defense) * 0.069)}")
    print(f"最小伤害保护: max(1, {round((attacker4.physical_attack - defender4.physical_defense) * 0.069)}) = {expected4}")
    print(f"实际扣血: {damage4}")
    print(f"测试结果: {'✅ 通过' if damage4 == expected4 else '❌ 失败'}")
    
    # 测试用例5：大数值测试
    print("\n【测试用例5】大数值测试")
    print("-" * 80)
    
    attacker5 = PvpBeast(
        id=9,
        name="测试幻兽I",
        hp_max=10000,
        hp_current=10000,
        physical_attack=5000,
        magic_attack=0,
        physical_defense=1000,
        magic_defense=1000,
        speed=100,
        attack_type="physical"
    )
    
    defender5 = PvpBeast(
        id=10,
        name="测试幻兽J",
        hp_max=10000,
        hp_current=10000,
        physical_attack=2000,
        magic_attack=0,
        physical_defense=2000,
        magic_defense=2000,
        speed=80,
        attack_type="physical"
    )
    
    damage5 = calc_damage(attacker5, defender5, 50)
    expected5 = round((attacker5.physical_attack - defender5.physical_defense) * 0.069)
    
    print(f"攻击方物攻: {attacker5.physical_attack}")
    print(f"防御方物防: {defender5.physical_defense}")
    print(f"攻击差: {attacker5.physical_attack - defender5.physical_defense}")
    print(f"计算公式: ({attacker5.physical_attack} - {defender5.physical_defense}) × 0.069 = {(attacker5.physical_attack - defender5.physical_defense) * 0.069}")
    print(f"四舍五入后: {expected5}")
    print(f"实际扣血: {damage5}")
    print(f"测试结果: {'✅ 通过' if damage5 == expected5 else '❌ 失败'}")
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    all_passed = (
        damage1 == expected1 and
        damage2 == expected2 and
        damage3 == expected3 and
        damage4 == expected4 and
        damage5 == expected5
    )
    
    if all_passed:
        print("✅ 所有测试通过！新的扣血公式已正确实现。")
    else:
        print("❌ 部分测试失败，请检查实现。")
    
    print("=" * 80)


if __name__ == "__main__":
    test_damage_formula()
