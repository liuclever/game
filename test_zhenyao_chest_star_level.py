"""测试镇妖宝箱星级命名"""
from application.services.zhenyao_service import ZhenyaoService

def test_star_level_calculation():
    """测试星级计算逻辑"""
    print("=== 测试宝箱星级计算 ===\n")
    
    # 创建服务实例（只测试星级计算方法）
    service = ZhenyaoService(
        player_repo=None,
        zhenyao_repo=None,
        tower_state_repo=None
    )
    
    test_cases = [
        (29, 0, "29级以下"),
        (30, 3, "30级"),
        (35, 3, "35级"),
        (39, 3, "39级"),
        (40, 4, "40级"),
        (45, 4, "45级"),
        (49, 4, "49级"),
        (50, 5, "50级"),
        (55, 5, "55级"),
        (59, 5, "59级"),
        (60, 6, "60级"),
        (65, 6, "65级"),
        (69, 6, "69级"),
        (70, 7, "70级"),
        (75, 7, "75级"),
        (79, 7, "79级"),
        (80, 8, "80级"),
        (85, 8, "85级"),
        (90, 8, "90级"),
        (100, 8, "100级"),
    ]
    
    print("等级 | 星级 | 试炼宝箱名称 | 炼狱宝箱名称")
    print("-" * 60)
    
    for level, expected_star, desc in test_cases:
        star = service._get_chest_star_level(level)
        star_prefix = f"{star}星" if star > 0 else ""
        trial_name = f"{star_prefix}试炼宝箱"
        hell_name = f"{star_prefix}炼狱宝箱"
        
        status = "✓" if star == expected_star else "✗"
        print(f"{status} {level:3d}级 | {star}星 | {trial_name:12s} | {hell_name}")
        
        if star != expected_star:
            print(f"  ⚠ 预期{expected_star}星，实际{star}星")

def test_chest_naming():
    """测试宝箱命名规则"""
    print("\n=== 宝箱命名规则 ===\n")
    
    rules = [
        ("30-39级", "3星试炼宝箱", "3星炼狱宝箱"),
        ("40-49级", "4星试炼宝箱", "4星炼狱宝箱"),
        ("50-59级", "5星试炼宝箱", "5星炼狱宝箱"),
        ("60-69级", "6星试炼宝箱", "6星炼狱宝箱"),
        ("70-79级", "7星试炼宝箱", "7星炼狱宝箱"),
        ("80级及以上", "8星试炼宝箱", "8星炼狱宝箱"),
    ]
    
    print("等级范围 | 试炼宝箱 | 炼狱宝箱")
    print("-" * 50)
    
    for level_range, trial, hell in rules:
        print(f"{level_range:12s} | {trial:12s} | {hell}")

def test_reward_grant_simulation():
    """模拟奖励发放"""
    print("\n=== 模拟奖励发放 ===\n")
    
    service = ZhenyaoService(
        player_repo=None,
        zhenyao_repo=None,
        tower_state_repo=None
    )
    
    scenarios = [
        (35, 31, True, "35级玩家占领试炼层"),
        (35, 41, False, "35级玩家占领炼狱层"),
        (45, 51, True, "45级玩家占领试炼层"),
        (55, 71, False, "55级玩家占领炼狱层"),
        (65, 91, True, "65级玩家占领试炼层"),
        (75, 111, False, "75级玩家占领炼狱层"),
        (85, 131, True, "85级玩家占领试炼层"),
    ]
    
    print("场景 | 玩家等级 | 层数 | 宝箱类型 | 宝箱名称")
    print("-" * 70)
    
    for level, floor, is_trial, desc in scenarios:
        star = service._get_chest_star_level(level)
        star_prefix = f"{star}星" if star > 0 else ""
        chest_type = "试炼" if is_trial else "炼狱"
        chest_name = f"{star_prefix}{chest_type}宝箱"
        
        print(f"{desc:20s} | {level:3d}级 | {floor:3d}层 | {chest_type:4s} | {chest_name}")

if __name__ == "__main__":
    print("镇妖宝箱星级命名测试")
    print("=" * 70)
    
    try:
        test_star_level_calculation()
        test_chest_naming()
        test_reward_grant_simulation()
        
        print("\n" + "=" * 70)
        print("测试完成")
        print("\n星级规则:")
        print("- 30-39级: 3星宝箱")
        print("- 40-49级: 4星宝箱")
        print("- 50-59级: 5星宝箱")
        print("- 60-69级: 6星宝箱")
        print("- 70-79级: 7星宝箱")
        print("- 80级及以上: 8星宝箱")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
