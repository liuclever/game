"""联盟升级功能简单测试

运行方式（项目根目录）：
    python -m pytest tests/alliance/test_alliance_upgrades_simple.py -vv -s
    或者直接运行：
    python tests/alliance/test_alliance_upgrades_simple.py
"""

import sys
sys.path.insert(0, '.')

from domain.rules.alliance_rules import AllianceRules


def test_council_upgrade_rules():
    """测试议事厅升级规则"""
    print("\n=== 测试议事厅升级规则 ===")
    
    # 测试1级到2级
    rule = AllianceRules.get_council_upgrade_rule(1)
    assert rule is not None, "应该能找到1级升级规则"
    assert rule["next_level"] == 2, "下一级应该是2级"
    assert rule["funds"] == 1000, "资金消耗应该是1000"
    assert rule["crystals"] == 3000, "焚火晶消耗应该是3000"
    assert rule["prosperity"] == 40000, "繁荣度要求应该是40000"
    assert rule["requires"] == {"furnace": 1, "talent": 1, "beast": 1}, "建筑要求应该是全部1级"
    print("[OK] 1->2级规则正确")
    
    # 测试9级到10级
    rule = AllianceRules.get_council_upgrade_rule(9)
    assert rule is not None, "应该能找到9级升级规则"
    assert rule["next_level"] == 10, "下一级应该是10级"
    assert rule["funds"] == 25000, "资金消耗应该是25000"
    assert rule["crystals"] == 35000, "焚火晶消耗应该是35000"
    assert rule["prosperity"] == 6500000, "繁荣度要求应该是650万"
    print("[OK] 9→10级规则正确")
    
    # 测试10级（最高级）
    rule = AllianceRules.get_council_upgrade_rule(10)
    assert rule is None, "10级应该没有升级规则（已达最高级）"
    print("[OK] 10级无升级规则（最高级）")


def test_furnace_upgrade_rules():
    """测试焚天炉升级规则"""
    print("\n=== 测试焚天炉升级规则 ===")
    
    rule = AllianceRules.get_furnace_upgrade_rule(1)
    assert rule is not None, "应该能找到1级升级规则"
    assert rule["next_level"] == 2, "下一级应该是2级"
    assert rule["council_level"] == 2, "议事厅要求应该是2级"
    assert rule["funds"] == 1000, "资金消耗应该是1000"
    assert rule["crystals"] == 300, "焚火晶消耗应该是300"
    assert rule["prosperity"] == 40000, "繁荣度要求应该是40000"
    print("[OK] 焚天炉1→2级规则正确")
    
    # 测试焚火晶加成：每升一级，火能修行每个人所获得的焚火晶增加2个
    bonus_1 = AllianceRules.furnace_crystal_bonus(1)
    bonus_2 = AllianceRules.furnace_crystal_bonus(2)
    bonus_3 = AllianceRules.furnace_crystal_bonus(3)
    assert bonus_1 == 0, "1级加成应该是0"
    assert bonus_2 == 2, "2级加成应该是2"
    assert bonus_3 == 4, "3级加成应该是4"
    print("[OK] 焚火晶加成规则正确（每级+2）")


def test_talent_pool_upgrade_rules():
    """测试天赋池升级规则"""
    print("\n=== 测试天赋池升级规则 ===")
    
    rule = AllianceRules.get_talent_pool_upgrade_rule(1)
    assert rule is not None, "应该能找到1级升级规则"
    assert rule["next_level"] == 2, "下一级应该是2级"
    assert rule["council_level"] == 2, "议事厅要求应该是2级"
    assert rule["funds"] == 1000, "资金消耗应该是1000"
    assert rule["crystals"] == 300, "焚火晶消耗应该是300"
    print("[OK] 天赋池1→2级规则正确")


def test_talent_research_rules():
    """测试天赋研发规则"""
    print("\n=== 测试天赋研发规则 ===")
    
    # 测试1级到2级研发成本
    cost = AllianceRules.get_talent_research_cost(2, "atk")
    assert cost is not None, "应该能找到2级研发成本"
    assert cost["funds"] == 1000, "资金消耗应该是1000"
    assert cost["crystals"] == 500, "焚火晶消耗应该是500"
    print("[OK] 天赋研发2级成本正确")
    
    # 测试9级到10级研发成本
    cost = AllianceRules.get_talent_research_cost(10, "hp")
    assert cost is not None, "应该能找到10级研发成本"
    assert cost["funds"] == 3200, "资金消耗应该是3200"
    assert cost["crystals"] == 2000, "焚火晶消耗应该是2000"
    print("[OK] 天赋研发10级成本正确")


def test_talent_learn_contribution():
    """测试学习天赋贡献消耗"""
    print("\n=== 测试学习天赋贡献消耗 ===")
    
    # 测试学习1级天赋
    cost = AllianceRules.get_talent_learn_contribution_cost(1)
    assert cost["per_talent"] == 10, "单项天赋1级消耗应该是10贡献"
    assert cost["total"] == 60, "6项天赋总计应该是60贡献"
    print("[OK] 学习1级天赋消耗正确（单项10，总计60）")
    
    # 测试学习2级天赋
    cost = AllianceRules.get_talent_learn_contribution_cost(2)
    assert cost["per_talent"] == 20, "单项天赋2级消耗应该是20贡献"
    assert cost["total"] == 120, "6项天赋总计应该是120贡献"
    print("[OK] 学习2级天赋消耗正确（单项20，总计120）")


def test_beast_room_upgrade_rules():
    """测试幻兽室升级规则"""
    print("\n=== 测试幻兽室升级规则 ===")
    
    rule = AllianceRules.get_beast_room_upgrade_rule(1)
    assert rule is not None, "应该能找到1级升级规则"
    assert rule["next_level"] == 2, "下一级应该是2级"
    assert rule["council_level"] == 2, "议事厅要求应该是2级"
    print("[OK] 幻兽室1→2级规则正确")
    
    # 测试容量：1级时寄存容量为1，每升一级，寄存容量＋1
    cap_1 = AllianceRules.beast_room_capacity_from_level(1)
    cap_2 = AllianceRules.beast_room_capacity_from_level(2)
    cap_3 = AllianceRules.beast_room_capacity_from_level(3)
    assert cap_1 == 1, "1级容量应该是1"
    assert cap_2 == 2, "2级容量应该是2"
    assert cap_3 == 3, "3级容量应该是3"
    print("[OK] 幻兽室容量规则正确（1级1个，每级+1）")


def test_item_storage_upgrade_rules():
    """测试寄存仓库升级规则"""
    print("\n=== 测试寄存仓库升级规则 ===")
    
    rule = AllianceRules.get_item_storage_upgrade_rule(1)
    assert rule is not None, "应该能找到1级升级规则"
    assert rule["next_level"] == 2, "下一级应该是2级"
    assert rule["council_level"] == 2, "议事厅要求应该是2级"
    print("[OK] 寄存仓库1→2级规则正确")
    
    # 测试容量：1级时，寄存仓库容量为5，每升一级，容量＋5
    cap_1 = AllianceRules.item_storage_capacity_from_level(1)
    cap_2 = AllianceRules.item_storage_capacity_from_level(2)
    cap_3 = AllianceRules.item_storage_capacity_from_level(3)
    assert cap_1 == 5, "1级容量应该是5"
    assert cap_2 == 10, "2级容量应该是10"
    assert cap_3 == 15, "3级容量应该是15"
    print("[OK] 寄存仓库容量规则正确（1级5格，每级+5）")


def test_member_capacity():
    """测试联盟成员容量"""
    print("\n=== 测试联盟成员容量 ===")
    
    # 测试成员容量：基础30人，每升一级+10人
    cap_1 = AllianceRules.member_capacity(1)
    cap_2 = AllianceRules.member_capacity(2)
    cap_3 = AllianceRules.member_capacity(3)
    assert cap_1 == 30, "1级容量应该是30人"
    assert cap_2 == 40, "2级容量应该是40人（+10）"
    assert cap_3 == 50, "3级容量应该是50人（+10）"
    print("[OK] 联盟成员容量规则正确（基础30，每级+10）")


def test_all_rules_summary():
    """测试所有规则汇总"""
    print("\n=== 规则汇总测试 ===")
    
    # 测试所有建筑升级规则都有定义
    buildings = ["council", "furnace", "talent", "beast", "warehouse"]
    for building in buildings:
        assert AllianceRules.is_valid_building_key(building), f"建筑 {building} 应该是有效的"
        label = AllianceRules.building_label(building)
        assert label, f"建筑 {building} 应该有标签"
        print(f"[OK] {building}: {label}")
    
    # 测试所有天赋键都有定义
    talents = AllianceRules.TALENT_KEYS
    assert len(talents) == 6, "应该有6个天赋"
    for talent in talents:
        label = AllianceRules.talent_label(talent)
        assert label, f"天赋 {talent} 应该有标签"
        print(f"[OK] 天赋 {talent}: {label}")


if __name__ == "__main__":
    print("开始测试联盟升级规则...")
    
    try:
        test_council_upgrade_rules()
        test_furnace_upgrade_rules()
        test_talent_pool_upgrade_rules()
        test_talent_research_rules()
        test_talent_learn_contribution()
        test_beast_room_upgrade_rules()
        test_item_storage_upgrade_rules()
        test_member_capacity()
        test_all_rules_summary()
        
        print("\n" + "="*50)
        print("[SUCCESS] 所有测试通过！")
        print("="*50)
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
