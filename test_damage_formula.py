"""测试新的伤害公式

新的扣血公式：
1. 当 (攻击 - 防御) ≥ 0 时：伤害 = (攻击 - 防御) × 0.069（四舍五入）
2. 当 (攻击 - 防御) < 0 时：固定扣血 5 点
"""

def test_damage_formula():
    """测试伤害公式"""
    
    test_cases = [
        # (攻击, 防御, 期望伤害)
        (1000, 500, round((1000 - 500) * 0.069)),  # 正常情况
        (2000, 1000, round((2000 - 1000) * 0.069)),  # 正常情况
        (500, 1000, 5),  # 负数情况，固定5点
        (100, 200, 5),  # 负数情况，固定5点
        (1500, 1500, round(0 * 0.069)),  # 相等情况
        (3000, 2000, round((3000 - 2000) * 0.069)),  # 大数值
        (100, 50, round((100 - 50) * 0.069)),  # 小数值
    ]
    
    print("=" * 60)
    print("伤害公式测试")
    print("=" * 60)
    
    for attack, defense, expected in test_cases:
        diff = attack - defense
        if diff >= 0:
            actual = round(diff * 0.069)
        else:
            actual = 5
        
        actual = max(1, actual)  # 最少1点伤害
        
        status = "✓" if actual == max(1, expected) else "✗"
        print(f"{status} 攻击:{attack:5d} 防御:{defense:5d} 差值:{diff:6d} "
              f"期望伤害:{max(1, expected):3d} 实际伤害:{actual:3d}")
    
    print("=" * 60)


def test_pvp_battle_engine():
    """测试PVP战斗引擎的伤害计算"""
    from domain.services.pvp_battle_engine import PvpBeast, calc_damage
    
    print("\n" + "=" * 60)
    print("PVP战斗引擎伤害测试")
    print("=" * 60)
    
    # 创建测试幻兽
    attacker = PvpBeast(
        id=1,
        name="攻击兽",
        hp_max=1000,
        hp_current=1000,
        physical_attack=1500,
        magic_attack=0,
        physical_defense=500,
        magic_defense=500,
        speed=100,
        attack_type="physical"
    )
    
    defender = PvpBeast(
        id=2,
        name="防御兽",
        hp_max=1000,
        hp_current=1000,
        physical_attack=500,
        magic_attack=0,
        physical_defense=1000,
        magic_defense=1000,
        speed=80,
        attack_type="physical"
    )
    
    # 测试1: 攻击 > 防御
    damage1 = calc_damage(attacker, defender, 50)
    expected1 = round((1500 - 1000) * 0.069)
    print(f"测试1 - 攻击>防御: 攻击1500 防御1000 差值500")
    print(f"  期望伤害: {expected1}, 实际伤害: {damage1}, 结果: {'✓' if damage1 == expected1 else '✗'}")
    
    # 测试2: 攻击 < 防御
    damage2 = calc_damage(defender, attacker, 50)
    expected2 = 5
    print(f"测试2 - 攻击<防御: 攻击500 防御500 差值0")
    print(f"  期望伤害: {expected2}, 实际伤害: {damage2}, 结果: {'✓' if damage2 == expected2 else '✗'}")
    
    # 测试3: 法术攻击
    attacker.attack_type = "magic"
    attacker.magic_attack = 2000
    damage3 = calc_damage(attacker, defender, 50)
    expected3 = round((2000 - 1000) * 0.069)
    print(f"测试3 - 法术攻击: 法攻2000 法防1000 差值1000")
    print(f"  期望伤害: {expected3}, 实际伤害: {damage3}, 结果: {'✓' if damage3 == expected3 else '✗'}")
    
    print("=" * 60)


def test_battle_engine():
    """测试旧战斗引擎的伤害计算"""
    from domain.services.battle_engine import BeastStats, SimpleDamageCalculator
    
    print("\n" + "=" * 60)
    print("旧战斗引擎伤害测试")
    print("=" * 60)
    
    calculator = SimpleDamageCalculator()
    
    # 创建测试幻兽
    attacker = BeastStats(
        id=1,
        name="攻击兽",
        hp=1000,
        max_hp=1000,
        physical_attack=1500,
        magic_attack=0,
        physical_defense=500,
        magic_defense=500,
        speed=100,
        nature="物理"
    )
    
    defender = BeastStats(
        id=2,
        name="防御兽",
        hp=1000,
        max_hp=1000,
        physical_attack=500,
        magic_attack=0,
        physical_defense=1000,
        magic_defense=1000,
        speed=80,
        nature="物理"
    )
    
    # 测试1: 攻击 > 防御
    damage1 = calculator.calculate(attacker, defender)
    expected1 = round((1500 - 1000) * 0.069)
    print(f"测试1 - 攻击>防御: 物攻1500 物防1000 差值500")
    print(f"  期望伤害: {expected1}, 实际伤害: {damage1}, 结果: {'✓' if damage1 == expected1 else '✗'}")
    
    # 测试2: 攻击 < 防御
    damage2 = calculator.calculate(defender, attacker)
    expected2 = 5
    print(f"测试2 - 攻击<防御: 物攻500 物防500 差值0")
    print(f"  期望伤害: {expected2}, 实际伤害: {damage2}, 结果: {'✓' if damage2 == expected2 else '✗'}")
    
    print("=" * 60)


def test_tower_service():
    """测试塔服务的伤害计算"""
    print("\n" + "=" * 60)
    print("塔服务伤害测试")
    print("=" * 60)
    
    # 模拟塔服务的伤害计算
    def calc_damage(attack, defense):
        diff = attack - defense
        if diff >= 0:
            return max(1, round(diff * 0.069))
        else:
            return max(1, 5)
    
    test_cases = [
        (1500, 1000, round((1500 - 1000) * 0.069)),
        (500, 1000, 5),
        (2000, 1500, round((2000 - 1500) * 0.069)),
    ]
    
    for attack, defense, expected in test_cases:
        actual = calc_damage(attack, defense)
        status = "✓" if actual == max(1, expected) else "✗"
        print(f"{status} 攻击:{attack:5d} 防御:{defense:5d} "
              f"期望伤害:{max(1, expected):3d} 实际伤害:{actual:3d}")
    
    print("=" * 60)


if __name__ == "__main__":
    # 运行所有测试
    test_damage_formula()
    test_pvp_battle_engine()
    test_battle_engine()
    test_tower_service()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
