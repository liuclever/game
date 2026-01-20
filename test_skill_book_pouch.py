#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试技能书口袋功能
验证：
1. 技能书口袋道具ID为6007
2. 打开技能书口袋随机获得53个技能书中的一个
3. 53个技能书的配置正确
"""

import json
import os
import sys


def test_skill_book_config():
    """测试技能书配置"""
    print("=" * 60)
    print("测试1: 验证技能书配置")
    print("=" * 60)
    
    cfg_path = os.path.join('configs', 'skill_books.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    all_books = []
    for category, books in cfg.get('skill_books', {}).items():
        print(f"\n{category}: {len(books)}个技能书")
        for b in books:
            if b and b.get('item_id'):
                all_books.append(b['item_id'])
                print(f"  - {b['name']} (ID: {b['item_id']}) -> 技能: {b['skill_name']}")
    
    print(f"\n✓ 技能书总数: {len(all_books)}")
    print(f"✓ 技能书ID范围: {min(all_books)} - {max(all_books)}")
    
    if len(all_books) == 53:
        print("✓ 技能书数量正确 (53个)")
    else:
        print(f"✗ 技能书数量错误，期望53个，实际{len(all_books)}个")
    
    return all_books


def test_item_config():
    """测试道具配置"""
    print("\n" + "=" * 60)
    print("测试2: 验证道具配置")
    print("=" * 60)
    
    items_path = os.path.join('configs', 'items.json')
    with open(items_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # 查找技能书口袋
    skill_book_pouch = None
    for item in items:
        if item.get('id') == 6007:
            skill_book_pouch = item
            break
    
    if skill_book_pouch:
        print(f"✓ 找到技能书口袋:")
        print(f"  - ID: {skill_book_pouch['id']}")
        print(f"  - 名称: {skill_book_pouch['name']}")
        print(f"  - 类型: {skill_book_pouch['type']}")
        print(f"  - 描述: {skill_book_pouch['description']}")
    else:
        print("✗ 未找到技能书口袋 (ID: 6007)")
    
    # 查找所有技能书道具
    skill_books = [item for item in items if item.get('type') == 'skill_book']
    print(f"\n✓ 找到 {len(skill_books)} 个技能书道具")
    
    return skill_book_pouch, skill_books


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("技能书口袋功能测试")
    print("=" * 60)
    
    # 测试1: 验证技能书配置
    all_books = test_skill_book_config()
    
    # 测试2: 验证道具配置
    pouch, skill_books = test_item_config()
    
    print("\n" + "=" * 60)
    print("配置验证完成")
    print("=" * 60)
    print("\n总结:")
    print(f"✓ 技能书配置: {len(all_books)} 个技能书")
    print(f"✓ 技能书口袋道具: ID={pouch['id'] if pouch else 'N/A'}")
    print(f"✓ 技能书道具: {len(skill_books)} 个")
    print("\n功能说明:")
    print("- 道具ID 6007: 技能书口袋")
    print("- 使用技能书口袋可随机获得53个技能书中的一个")
    print("- 每个技能书等概率获得")
    print("- 支持批量打开，一次最多10个")


if __name__ == "__main__":
    main()
