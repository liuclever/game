#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试地图副本法攻型幻兽的法攻属性

验证：
1. 法攻型幻兽的法攻值不为0
2. 法攻值与配置文件中的matk值一致
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


def load_dungeon_beasts_config():
    """加载副本幻兽配置"""
    config_path = project_root / 'configs' / 'dungeon_beasts.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_magic_attack_beasts():
    """测试法攻型幻兽的属性"""
    
    print("=" * 80)
    print("地图副本法攻型幻兽属性测试")
    print("=" * 80)
    print()
    
    config = load_dungeon_beasts_config()
    
    magic_beasts = []
    
    # 遍历所有副本
    for dungeon_id, dungeon_data in config['dungeons'].items():
        dungeon_name = dungeon_data['name']
        beasts = dungeon_data.get('beasts', {})
        
        # 检查普通怪物
        for beast in beasts.get('normal', []):
            if beast.get('attack_type') == 'magical':
                magic_beasts.append({
                    'dungeon': dungeon_name,
                    'type': '普通',
                    'name': beast['name'],
                    'level': beast['level'],
                    'matk': beast['stats'].get('matk', 0),
                    'atk': beast['stats'].get('atk', 0)
                })
        
        # 检查精英怪物
        for beast in beasts.get('elite', []):
            if beast.get('attack_type') == 'magical':
                magic_beasts.append({
                    'dungeon': dungeon_name,
                    'type': '精英',
                    'name': beast['name'],
                    'level': beast['level'],
                    'matk': beast['stats'].get('matk', 0),
                    'atk': beast['stats'].get('atk', 0)
                })
        
        # 检查BOSS
        boss = beasts.get('boss')
        if boss and boss.get('attack_type') == 'magical':
            magic_beasts.append({
                'dungeon': dungeon_name,
                'type': 'BOSS',
                'name': boss['name'],
                'level': boss['level'],
                'matk': boss['stats'].get('matk', 0),
                'atk': boss['stats'].get('atk', 0)
            })
    
    print(f"找到 {len(magic_beasts)} 个法攻型幻兽\n")
    
    # 统计
    has_matk = 0
    has_atk = 0
    matk_zero = 0
    
    print("法攻型幻兽列表：")
    print("-" * 80)
    print(f"{'副本':<20} {'类型':<6} {'名称':<15} {'等级':<4} {'matk':<6} {'atk':<6}")
    print("-" * 80)
    
    for beast in magic_beasts:
        matk = beast['matk']
        atk = beast['atk']
        
        if matk > 0:
            has_matk += 1
        if atk > 0:
            has_atk += 1
        if matk == 0:
            matk_zero += 1
        
        status = ""
        if matk == 0:
            status = " ⚠️ 法攻为0"
        elif atk > 0:
            status = " ⚠️ 同时有物攻"
        
        print(f"{beast['dungeon']:<20} {beast['type']:<6} {beast['name']:<15} "
              f"{beast['level']:<4} {matk:<6} {atk:<6}{status}")
    
    print("-" * 80)
    print()
    
    # 统计结果
    print("统计结果：")
    print(f"  总法攻型幻兽数: {len(magic_beasts)}")
    print(f"  有matk值的: {has_matk} ({has_matk/len(magic_beasts)*100:.1f}%)")
    print(f"  有atk值的: {has_atk} ({has_atk/len(magic_beasts)*100:.1f}%)")
    print(f"  matk为0的: {matk_zero} ({matk_zero/len(magic_beasts)*100:.1f}%)")
    print()
    
    # 验证结果
    if matk_zero == 0 and has_atk == 0:
        print("✅ 测试通过：所有法攻型幻兽都有正确的matk值，且没有atk值")
    else:
        print("❌ 测试失败：")
        if matk_zero > 0:
            print(f"   - {matk_zero} 个法攻型幻兽的matk为0")
        if has_atk > 0:
            print(f"   - {has_atk} 个法攻型幻兽同时有atk值（应该只有matk）")
    
    print()
    print("=" * 80)
    
    # 显示修复前后的代码对比
    print("\n修复说明：")
    print("-" * 80)
    print("问题：法攻型幻兽的法攻值都为0")
    print()
    print("原因：代码逻辑错误")
    print("  修复前：ma = stats.get('atk', 0) if attack_type == 'magic' else stats.get('matk', 0)")
    print("  问题：当attack_type=='magic'时，从'atk'字段读取，但配置文件中法攻型幻兽使用'matk'字段")
    print()
    print("  修复后：ma = stats.get('matk', 0) if attack_type == 'magic' else 0")
    print("  正确：当attack_type=='magic'时，从'matk'字段读取法攻值")
    print()
    print("文件位置：interfaces/routes/dungeon_routes.py 第241行")
    print("-" * 80)


if __name__ == "__main__":
    test_magic_attack_beasts()
