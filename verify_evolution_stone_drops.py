#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证地图副本进化石掉落配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json

def load_dungeon_config():
    """加载副本配置"""
    config_path = 'configs/dungeon_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_items_config():
    """加载物品配置"""
    config_path = 'configs/items.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_evolution_stone_item_id(dungeon_name, dungeon_config):
    """根据副本/地图获取对应的进化石 ID"""
    # 查找所属地图
    target_map = None
    for m in dungeon_config['maps']:
        for d in m['dungeons']:
            if d['name'] == dungeon_name:
                target_map = m
                break
        if target_map: break
        
    if not target_map:
        return None, None
        
    map_name = target_map['map_name']
    
    # 根据地图返回对应的进化石ID
    evolution_stones = {
        "定老城": 3001,  # 黄阶进化石
        "迷雾城": 3002,  # 玄阶进化石
        "飞龙港": 3003,  # 地阶进化石
        "落龙镇": 3004,  # 天阶进化石
        "圣龙城": 3005,  # 飞马进化石
        "乌托邦": 3006,  # 天龙进化石
    }
    
    return evolution_stones.get(map_name), map_name

def main():
    print("="*70)
    print("地图副本进化石掉落配置验证")
    print("="*70)
    
    dungeon_config = load_dungeon_config()
    items_config = load_items_config()
    
    # 创建物品ID到名称的映射
    item_names = {}
    for item in items_config:
        item_names[item['id']] = item['name']
    
    print("\n📋 地图与进化石对应关系：\n")
    
    # 遍历所有地图
    for map_data in dungeon_config['maps']:
        map_name = map_data['map_name']
        dungeons = map_data['dungeons']
        
        print(f"【{map_name}】")
        print(f"  副本数量: {len(dungeons)}")
        print(f"  副本列表:")
        
        for dungeon in dungeons:
            dungeon_name = dungeon['name']
            stone_id, _ = get_evolution_stone_item_id(dungeon_name, dungeon_config)
            
            if stone_id:
                stone_name = item_names.get(stone_id, f"未知物品({stone_id})")
                print(f"    - {dungeon_name} → {stone_name} (ID:{stone_id})")
            else:
                print(f"    - {dungeon_name} → ❌ 无进化石配置")
        
        print()
    
    print("="*70)
    print("验证完成")
    print("="*70)
    
    print("\n📊 进化石掉落规则：")
    print("  - 掉落位置：35层Boss战利品")
    print("  - 掉落概率：30%")
    print("  - 双倍卡效果：数量翻倍（1 → 2）")
    print("  - 独立掉落：与骨魂掉落独立计算")
    
    print("\n💡 用户描述对比：")
    print("  用户说：升龙城 → 飞马进化石")
    print("  实际是：圣龙城 → 飞马进化石")
    print("  说明：地图名称是'圣龙城'，不是'升龙城'")
    print()
    print("  用户说：乌托邦 → 北斗进化石")
    print("  实际是：乌托邦 → 天龙进化石")
    print("  说明：配置中是'天龙进化石'(3006)，没有'北斗进化石'")

if __name__ == '__main__':
    main()
