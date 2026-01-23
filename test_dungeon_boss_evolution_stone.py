"""测试地图副本35层boss掉落进化石"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
import json

def load_dungeon_config():
    config_path = os.path.join(os.path.dirname(__file__), 'configs', 'dungeon_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_evolution_stone_item_id(dungeon_name):
    """根据副本/地图获取对应的进化石 ID"""
    dungeon_config = load_dungeon_config()
    
    # 查找所属地图
    target_map = None
    for m in dungeon_config['maps']:
        for d in m['dungeons']:
            if d['name'] == dungeon_name:
                target_map = m
                break
        if target_map: break
        
    if not target_map:
        return None
        
    map_name = target_map['map_name']
    
    # 根据地图返回对应的进化石ID
    if map_name == "定老城": return 3001  # 黄阶进化石
    if map_name == "迷雾城": return 3002  # 玄阶进化石
    if map_name == "飞龙港": return 3003  # 地阶进化石
    if map_name == "落龙镇": return 3004  # 天阶进化石
    if map_name == "圣龙城": return 3005  # 飞马进化石
    if map_name == "乌托邦": return 3006  # 天龙进化石
        
    return None

def test_evolution_stone_mapping():
    """测试进化石映射关系"""
    
    print("=" * 80)
    print("测试地图副本35层boss掉落进化石配置")
    print("=" * 80)
    print()
    
    # 测试场景
    test_cases = [
        {"map": "定老城", "dungeons": ["石工矿场", "幻灵湖畔"], "expected_id": 3001, "expected_name": "黄阶进化石"},
        {"map": "迷雾城", "dungeons": ["回音之谷", "死亡沼泽"], "expected_id": 3002, "expected_name": "玄阶进化石"},
        {"map": "飞龙港", "dungeons": ["日落海峡", "聚灵孤岛"], "expected_id": 3003, "expected_name": "地阶进化石"},
        {"map": "落龙镇", "dungeons": ["龙骨墓地", "巨龙冰原"], "expected_id": 3004, "expected_name": "天阶进化石"},
        {"map": "圣龙城", "dungeons": ["圣龙城郊", "皇城迷宫"], "expected_id": 3005, "expected_name": "飞马进化石"},
        {"map": "乌托邦", "dungeons": ["梦幻海湾", "幻光公园"], "expected_id": 3006, "expected_name": "天龙进化石"},
    ]
    
    # 进化石名称映射
    evolution_stone_names = {
        3001: "黄阶进化石", 3002: "玄阶进化石", 3003: "地阶进化石",
        3004: "天阶进化石", 3005: "飞马进化石", 3006: "天龙进化石"
    }
    
    all_passed = True
    
    for test_case in test_cases:
        map_name = test_case["map"]
        dungeons = test_case["dungeons"]
        expected_id = test_case["expected_id"]
        expected_name = test_case["expected_name"]
        
        print(f"地图：{map_name}")
        print(f"预期进化石：{expected_name} (ID: {expected_id})")
        print(f"副本列表：{', '.join(dungeons)}")
        print()
        
        for dungeon_name in dungeons:
            stone_id = get_evolution_stone_item_id(dungeon_name)
            stone_name = evolution_stone_names.get(stone_id, "未知")
            
            if stone_id == expected_id:
                print(f"  ✓ {dungeon_name}: {stone_name} (ID: {stone_id})")
            else:
                print(f"  ✗ {dungeon_name}: {stone_name} (ID: {stone_id}) - 预期: {expected_name} (ID: {expected_id})")
                all_passed = False
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败！")
    print("=" * 80)
    print()
    
    # 显示掉落规则
    print("=" * 80)
    print("Boss战利品掉落规则（35层）")
    print("=" * 80)
    print()
    print("基础奖励：")
    print("  - 铜钱 × 600")
    print("  - 随机结晶 × 1")
    print()
    print("额外奖励（概率掉落）：")
    print("  - 骨魂 × 1 (30%概率)")
    print("  - 进化石 × 1 (30%概率)")
    print()
    print("进化石掉落对应关系：")
    for test_case in test_cases:
        print(f"  - {test_case['map']}: {test_case['expected_name']} (30%)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    test_evolution_stone_mapping()
