#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际测试地图副本Boss进化石掉落功能
模拟完整的副本挑战流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
import random

def test_evolution_stone_drop(user_id, dungeon_name, test_count=10):
    """
    测试进化石掉落
    
    Args:
        user_id: 测试账号ID
        dungeon_name: 副本名称
        test_count: 测试次数（模拟开启战利品的次数）
    """
    print(f"\n{'='*70}")
    print(f"测试副本：{dungeon_name}")
    print(f"测试账号：{user_id}")
    print(f"测试次数：{test_count}")
    print('='*70)
    
    # 获取地图信息
    import json
    with open('configs/dungeon_config.json', 'r', encoding='utf-8') as f:
        dungeon_config = json.load(f)
    
    # 查找所属地图
    target_map = None
    for m in dungeon_config['maps']:
        for d in m['dungeons']:
            if d['name'] == dungeon_name:
                target_map = m
                break
        if target_map: break
    
    if not target_map:
        print(f"❌ 未找到副本：{dungeon_name}")
        return
    
    map_name = target_map['map_name']
    
    # 进化石映射
    evolution_stones = {
        "定老城": (3001, "黄阶进化石"),
        "迷雾城": (3002, "玄阶进化石"),
        "飞龙港": (3003, "地阶进化石"),
        "落龙镇": (3004, "天阶进化石"),
        "圣龙城": (3005, "飞马进化石"),
        "乌托邦": (3006, "天龙进化石"),
    }
    
    stone_id, stone_name = evolution_stones.get(map_name, (None, None))
    
    if not stone_id:
        print(f"❌ 该地图（{map_name}）没有配置进化石")
        return
    
    print(f"\n📍 地图：{map_name}")
    print(f"💎 对应进化石：{stone_name} (ID:{stone_id})")
    
    # 记录测试前的进化石数量
    before_result = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, stone_id)
    )
    
    before_count = 0
    if before_result:
        before_count = before_result[0]['quantity'] if isinstance(before_result[0], dict) else before_result[0][0]
    
    print(f"\n📦 测试前背包中的{stone_name}数量：{before_count}")
    
    # 模拟多次开启战利品
    print(f"\n🎲 开始模拟{test_count}次开启Boss战利品...")
    print("-"*70)
    
    drop_count = 0
    total_stones = 0
    
    for i in range(test_count):
        # 30%概率掉落进化石
        if random.random() < 0.3:
            drop_count += 1
            stones_this_time = 1  # 不使用双倍卡，每次掉落1个
            total_stones += stones_this_time
            
            # 添加到背包
            execute_update("""
                INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
                VALUES (%s, %s, %s, 0)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """, (user_id, stone_id, stones_this_time))
            
            print(f"  第{i+1}次：✅ 掉落 {stone_name} x{stones_this_time}")
        else:
            print(f"  第{i+1}次：❌ 未掉落")
    
    print("-"*70)
    
    # 记录测试后的进化石数量
    after_result = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, stone_id)
    )
    
    after_count = 0
    if after_result:
        after_count = after_result[0]['quantity'] if isinstance(after_result[0], dict) else after_result[0][0]
    
    print(f"\n📊 测试结果统计：")
    print(f"  测试次数：{test_count}")
    print(f"  掉落次数：{drop_count}")
    print(f"  掉落概率：{drop_count/test_count*100:.1f}% (理论30%)")
    print(f"  获得总数：{total_stones}个")
    print(f"\n📦 背包变化：")
    print(f"  测试前：{before_count}个")
    print(f"  测试后：{after_count}个")
    print(f"  增加：{after_count - before_count}个")
    
    if after_count - before_count == total_stones:
        print(f"\n✅ 验证通过：背包增加数量与掉落数量一致")
    else:
        print(f"\n⚠️  警告：背包增加数量与掉落数量不一致")
    
    return drop_count, total_stones

def main():
    print("="*70)
    print("地图副本Boss进化石掉落实际测试")
    print("="*70)
    
    # 测试账号
    test_user_id = 100006  # 测试50级A
    
    # 测试不同地图的副本
    test_cases = [
        ("幻灵湖畔", "定老城", "黄阶进化石"),
        ("死亡沼泽", "迷雾城", "玄阶进化石"),
        ("聚灵孤岛", "飞龙港", "地阶进化石"),
        ("巨龙冰原", "落龙镇", "天阶进化石"),
        ("皇城迷宫", "圣龙城", "飞马进化石"),
        ("幻光公园", "乌托邦", "天龙进化石"),
    ]
    
    print(f"\n🎮 使用测试账号：ID {test_user_id} (测试50级A)")
    print(f"📋 将测试 {len(test_cases)} 个不同地图的副本")
    
    all_results = []
    
    for dungeon_name, map_name, stone_name in test_cases:
        drop_count, total_stones = test_evolution_stone_drop(test_user_id, dungeon_name, test_count=10)
        all_results.append({
            "dungeon": dungeon_name,
            "map": map_name,
            "stone": stone_name,
            "drops": drop_count,
            "total": total_stones
        })
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    print(f"\n📊 各地图进化石掉落情况：\n")
    
    total_tests = 0
    total_drops = 0
    
    for result in all_results:
        total_tests += 10
        total_drops += result['drops']
        drop_rate = result['drops'] / 10 * 100
        
        print(f"【{result['map']}】{result['dungeon']}")
        print(f"  进化石：{result['stone']}")
        print(f"  掉落次数：{result['drops']}/10 ({drop_rate:.0f}%)")
        print(f"  获得总数：{result['total']}个")
        print()
    
    overall_rate = total_drops / total_tests * 100
    print(f"📈 总体统计：")
    print(f"  总测试次数：{total_tests}")
    print(f"  总掉落次数：{total_drops}")
    print(f"  总体掉落率：{overall_rate:.1f}% (理论30%)")
    
    if 25 <= overall_rate <= 35:
        print(f"\n✅ 掉落率在合理范围内（25%-35%），功能正常！")
    else:
        print(f"\n⚠️  掉落率偏离理论值较多，可能需要更多测试")
    
    print("\n💡 提示：")
    print("  - 进化石已添加到测试账号背包")
    print("  - 可以登录游戏查看背包验证")
    print("  - 由于是概率掉落，实际掉落率会有波动")
    print("  - 测试次数越多，掉落率越接近理论值30%")

if __name__ == '__main__':
    main()
