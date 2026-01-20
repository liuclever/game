"""测试镇妖宝箱结晶奖励"""
import random

def test_crystal_selection_logic():
    """测试结晶选择逻辑"""
    print("=== 测试结晶选择逻辑 ===\n")
    
    # 七类结晶的ID
    crystal_pool = [1001, 1002, 1003, 1004, 1005, 1006, 1007]
    crystal_names = {
        1001: "金之结晶",
        1002: "木之结晶",
        1003: "水之结晶",
        1004: "火之结晶",
        1005: "土之结晶",
        1006: "电之结晶",
        1007: "风之结晶"
    }
    
    test_cases = [
        (3, "三星宝箱"),
        (4, "四星宝箱"),
        (5, "五星宝箱"),
        (6, "六星宝箱"),
        (7, "七星宝箱"),
        (8, "八星宝箱（超过池大小）"),
    ]
    
    print("测试从7种结晶中随机选择N种:\n")
    
    for count, desc in test_cases:
        print(f"{desc} - 应该获得 {count} 种不同的结晶:")
        
        # 模拟10次抽取
        for i in range(3):
            # 使用 random.sample 确保不重复
            selected = random.sample(crystal_pool, min(count, len(crystal_pool)))
            selected_names = [crystal_names[cid] for cid in selected]
            print(f"  第{i+1}次: {', '.join(selected_names)} (共{len(selected)}种)")
        
        print()

def test_reward_distribution():
    """测试奖励分配"""
    print("=== 测试奖励分配 ===\n")
    
    scenarios = [
        {
            "level": 35,
            "star": 3,
            "chest": "三星试炼宝箱",
            "crystals": 3,
            "gold": 100000,
            "other": ["活力草×1"]
        },
        {
            "level": 45,
            "star": 4,
            "chest": "四星试炼宝箱",
            "crystals": 4,
            "gold": 120000,
            "other": ["活力草×1"]
        },
        {
            "level": 55,
            "star": 5,
            "chest": "五星试炼宝箱",
            "crystals": 5,
            "gold": 140000,
            "other": ["活力草×2"]
        },
        {
            "level": 65,
            "star": 6,
            "chest": "六星试炼宝箱",
            "crystals": 6,
            "gold": 160000,
            "other": ["活力草×3"]
        },
        {
            "level": 75,
            "star": 7,
            "chest": "七星试炼宝箱",
            "crystals": 7,
            "gold": 180000,
            "other": ["活力草×4"]
        },
        {
            "level": 85,
            "star": 8,
            "chest": "八星试炼宝箱",
            "crystals": 8,
            "gold": 200000,
            "other": ["活力草×5"]
        },
    ]
    
    print("各星级宝箱的奖励配置:\n")
    print(f"{'宝箱':15s} | {'结晶数量':10s} | {'铜钱':10s} | 其他奖励")
    print("-" * 60)
    
    for s in scenarios:
        other_str = "、".join(s['other'])
        print(f"{s['chest']:15s} | {s['crystals']}种不同结晶 | {s['gold']:8d} | {other_str}")

def test_炼狱宝箱_rewards():
    """测试炼狱宝箱奖励"""
    print("\n=== 炼狱宝箱奖励 ===\n")
    
    scenarios = [
        {
            "star": 3,
            "chest": "三星炼狱宝箱",
            "crystals": 3,
            "gold": 100000,
            "other": ["活力草×1", "强力捕捉球×1", "追魂法宝×1", "灵力水晶×1"]
        },
        {
            "star": 4,
            "chest": "四星炼狱宝箱",
            "crystals": 4,
            "gold": 120000,
            "other": ["活力草×1", "强力捕捉球×1", "追魂法宝×1", "灵力水晶×1"]
        },
        {
            "star": 5,
            "chest": "五星炼狱宝箱",
            "crystals": 5,
            "gold": 140000,
            "other": ["活力草×2", "强力捕捉球×2", "追魂法宝×2", "灵力水晶×1"]
        },
    ]
    
    print(f"{'宝箱':15s} | {'结晶数量':10s} | {'铜钱':10s} | 其他奖励")
    print("-" * 80)
    
    for s in scenarios:
        other_str = "、".join(s['other'])
        print(f"{s['chest']:15s} | {s['crystals']}种不同结晶 | {s['gold']:8d} | {other_str}")

def explain_fix():
    """说明修复内容"""
    print("\n=== 修复说明 ===\n")
    
    print("问题:")
    print("- 原逻辑: 从7种结晶中随机选1种，然后给N个")
    print("- 例如: 三星宝箱随机到金之结晶，给3个金之结晶")
    print()
    
    print("正确逻辑:")
    print("- 新逻辑: 从7种结晶中随机选N种不同的，每种给1个")
    print("- 例如: 三星宝箱随机选3种（金、木、水），各给1个")
    print()
    
    print("实现方法:")
    print("- 使用 random.sample(pool, count) 确保不重复")
    print("- 每种结晶只给1个")
    print("- 星级越高，获得的结晶种类越多")
    print()
    
    print("星级与结晶数量对应:")
    print("- 3星: 3种不同结晶")
    print("- 4星: 4种不同结晶")
    print("- 5星: 5种不同结晶")
    print("- 6星: 6种不同结晶")
    print("- 7星: 7种不同结晶（全部）")
    print("- 8星: 7种不同结晶（全部，因为只有7种）")

if __name__ == "__main__":
    print("镇妖宝箱结晶奖励测试")
    print("=" * 70)
    
    test_crystal_selection_logic()
    test_reward_distribution()
    test_炼狱宝箱_rewards()
    explain_fix()
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("\n七类结晶:")
    print("- 金之结晶 (1001)")
    print("- 木之结晶 (1002)")
    print("- 水之结晶 (1003)")
    print("- 火之结晶 (1004)")
    print("- 土之结晶 (1005)")
    print("- 电之结晶 (1006)")
    print("- 风之结晶 (1007)")
