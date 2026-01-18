"""测试新的幻兽战斗扣血公式

新公式：
①第一种情况（己方物攻/法攻-对方物防/法防≥0）：
  对方扣血数值＝（己方攻击数值-对方防御数值）×0.069（四舍五入）
②第二种情况（相减为＜0）：
  对方固定扣血5点
"""

from domain.services.battle_engine import BeastStats, BattleEngine, SimpleDamageCalculator
from domain.services.pvp_battle_engine import PvpBeast, PvpPlayer, run_pvp_battle


def test_simple_damage_calculator():
    """测试 SimpleDamageCalculator 的新公式"""
    print("=" * 60)
    print("测试 SimpleDamageCalculator（用于地图副本、闯塔等）")
    print("=" * 60)
    
    calculator = SimpleDamageCalculator()
    
    # 测试情况①：攻-防≥0
    print("\n【情况①：攻-防≥0】")
    test_cases_positive = [
        (1000, 500, "物理攻击1000 - 物理防御500"),
        (2000, 1500, "物理攻击2000 - 物理防御1500"),
        (500, 500, "物理攻击500 - 物理防御500（相等）"),
        (1450, 1000, "物理攻击1450 - 物理防御1000"),
    ]
    
    for phys_atk, phys_def, desc in test_cases_positive:
        attacker = BeastStats(
            id=1, name="攻击方", physical_attack=phys_atk, magic_attack=0,
            physical_defense=100, magic_defense=100, nature="物理"
        )
        defender = BeastStats(
            id=2, name="防守方", physical_attack=100, magic_attack=0,
            physical_defense=phys_def, magic_defense=100, nature="物理"
        )
        
        damage = calculator.calculate(attacker, defender)
        diff = phys_atk - phys_def
        expected = round(diff * 0.069)
        
        print(f"{desc}")
        print(f"  差值: {diff}")
        print(f"  预期伤害: {expected} (差值 × 0.069 四舍五入)")
        print(f"  实际伤害: {damage}")
        print(f"  ✓ 正确" if damage == expected else f"  ✗ 错误")
        print()
    
    # 测试情况②：攻-防<0
    print("\n【情况②：攻-防<0】")
    test_cases_negative = [
        (500, 1000, "物理攻击500 - 物理防御1000"),
        (100, 2000, "物理攻击100 - 物理防御2000"),
        (0, 500, "物理攻击0 - 物理防御500"),
    ]
    
    for phys_atk, phys_def, desc in test_cases_negative:
        attacker = BeastStats(
            id=1, name="攻击方", physical_attack=phys_atk, magic_attack=0,
            physical_defense=100, magic_defense=100, nature="物理"
        )
        defender = BeastStats(
            id=2, name="防守方", physical_attack=100, magic_attack=0,
            physical_defense=phys_def, magic_defense=100, nature="物理"
        )
        
        damage = calculator.calculate(attacker, defender)
        diff = phys_atk - phys_def
        
        print(f"{desc}")
        print(f"  差值: {diff}")
        print(f"  预期伤害: 5 (固定)")
        print(f"  实际伤害: {damage}")
        print(f"  ✓ 正确" if damage == 5 else f"  ✗ 错误")
        print()
    
    # 测试法术攻击
    print("\n【法术攻击测试】")
    attacker = BeastStats(
        id=1, name="法师", physical_attack=0, magic_attack=1500,
        physical_defense=100, magic_defense=100, nature="法术"
    )
    defender = BeastStats(
        id=2, name="防守方", physical_attack=100, magic_attack=0,
        physical_defense=100, magic_defense=1000, nature="物理"
    )
    
    damage = calculator.calculate(attacker, defender)
    diff = 1500 - 1000
    expected = round(diff * 0.069)
    
    print(f"法术攻击1500 - 法术防御1000")
    print(f"  差值: {diff}")
    print(f"  预期伤害: {expected}")
    print(f"  实际伤害: {damage}")
    print(f"  ✓ 正确" if damage == expected else f"  ✗ 错误")


def test_pvp_damage():
    """测试 PVP 战斗引擎的新公式"""
    print("\n" + "=" * 60)
    print("测试 PVP 战斗引擎（用于竞技场、擂台、切磋等）")
    print("=" * 60)
    
    # 测试情况①：攻-防≥0
    print("\n【情况①：攻-防≥0】")
    attacker_beast = PvpBeast(
        id=1, name="强攻幻兽",
        hp_max=1000, hp_current=1000,
        physical_attack=1500, magic_attack=0,
        physical_defense=500, magic_defense=500,
        speed=100, attack_type="physical"
    )
    
    defender_beast = PvpBeast(
        id=2, name="防守幻兽",
        hp_max=1000, hp_current=1000,
        physical_attack=500, magic_attack=0,
        physical_defense=1000, magic_defense=500,
        speed=50, attack_type="physical"
    )
    
    attacker_player = PvpPlayer(
        player_id=1, level=50, name="玩家1",
        beasts=[attacker_beast]
    )
    
    defender_player = PvpPlayer(
        player_id=2, level=50, name="玩家2",
        beasts=[defender_beast]
    )
    
    result = run_pvp_battle(attacker_player, defender_player, max_log_turns=10)
    
    print(f"攻击方物攻: 1500, 防守方物防: 1000")
    print(f"差值: 500")
    print(f"预期伤害: {round(500 * 0.069)} (500 × 0.069 四舍五入)")
    
    if result.logs:
        first_attack = result.logs[0]
        print(f"实际第一次攻击伤害: {first_attack.damage}")
        print(f"战报: {first_attack.description}")
    
    # 测试情况②：攻-防<0
    print("\n【情况②：攻-防<0】")
    weak_attacker = PvpBeast(
        id=3, name="弱攻幻兽",
        hp_max=1000, hp_current=1000,
        physical_attack=500, magic_attack=0,
        physical_defense=500, magic_defense=500,
        speed=100, attack_type="physical"
    )
    
    strong_defender = PvpBeast(
        id=4, name="高防幻兽",
        hp_max=1000, hp_current=1000,
        physical_attack=500, magic_attack=0,
        physical_defense=1500, magic_defense=500,
        speed=50, attack_type="physical"
    )
    
    attacker_player2 = PvpPlayer(
        player_id=3, level=50, name="玩家3",
        beasts=[weak_attacker]
    )
    
    defender_player2 = PvpPlayer(
        player_id=4, level=50, name="玩家4",
        beasts=[strong_defender]
    )
    
    result2 = run_pvp_battle(attacker_player2, defender_player2, max_log_turns=10)
    
    print(f"攻击方物攻: 500, 防守方物防: 1500")
    print(f"差值: -1000")
    print(f"预期伤害: 5 (固定)")
    
    if result2.logs:
        first_attack = result2.logs[0]
        print(f"实际第一次攻击伤害: {first_attack.damage}")
        print(f"战报: {first_attack.description}")


def test_battle_engine_integration():
    """测试完整战斗流程"""
    print("\n" + "=" * 60)
    print("测试完整战斗流程")
    print("=" * 60)
    
    engine = BattleEngine()
    
    # 创建攻击方幻兽（高攻）
    attacker_beasts = [
        BeastStats(
            id=1, name="火龙", realm="化神期",
            hp=1000, max_hp=1000,
            physical_attack=1500, magic_attack=0,
            physical_defense=500, magic_defense=500,
            speed=100, nature="物理"
        )
    ]
    
    # 创建防守方幻兽（高防）
    defender_beasts = [
        BeastStats(
            id=2, name="玄武", realm="元婴期",
            hp=1200, max_hp=1200,
            physical_attack=500, magic_attack=0,
            physical_defense=1000, magic_defense=800,
            speed=50, nature="物理"
        )
    ]
    
    result = engine.fight(attacker_beasts, defender_beasts, "攻击方", "防守方")
    
    print(f"\n战斗结果: {'攻击方胜利' if result.is_victory else '防守方胜利'}")
    print(f"攻击方获胜场次: {result.attacker_wins}")
    print(f"防守方获胜场次: {result.defender_wins}")
    print(f"\n战斗详情:")
    
    for battle in result.battles:
        print(f"\n第{battle.battle_num}场: {battle.attacker_beast} vs {battle.defender_beast}")
        print(f"胜者: {battle.winner}")
        print(f"回合数: {len(battle.rounds)}")
        
        # 显示前3回合
        for i, round_result in enumerate(battle.rounds[:3]):
            print(f"  回合{round_result.round_num}: {round_result.action_text}")
            print(f"    伤害: {round_result.damage}, "
                  f"攻击方HP: {round_result.attacker_hp_after}, "
                  f"防守方HP: {round_result.defender_hp_after}")


if __name__ == "__main__":
    test_simple_damage_calculator()
    test_pvp_damage()
    test_battle_engine_integration()
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)
