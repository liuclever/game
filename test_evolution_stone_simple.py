#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试进化石掉落 - 直接给测试账号添加各种进化石
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

def main():
    print("="*70)
    print("给测试账号添加进化石样本")
    print("="*70)
    
    user_id = 100006  # 测试50级A
    
    # 进化石列表
    evolution_stones = [
        (3001, "黄阶进化石", 5),
        (3002, "玄阶进化石", 5),
        (3003, "地阶进化石", 5),
        (3004, "天阶进化石", 5),
        (3005, "飞马进化石", 5),
        (3006, "天龙进化石", 5),
    ]
    
    print(f"\n📦 为账号 {user_id} (测试50级A) 添加进化石...\n")
    
    for stone_id, stone_name, quantity in evolution_stones:
        # 先删除
        execute_update(
            "DELETE FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, stone_id)
        )
        
        # 再添加
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) VALUES (%s, %s, %s, 0)",
            (user_id, stone_id, quantity)
        )
        
        print(f"  ✅ {stone_name} x{quantity}")
    
    print("\n" + "="*70)
    print("验证结果")
    print("="*70)
    
    print(f"\n📦 背包中的进化石：\n")
    
    total = 0
    for stone_id, stone_name, expected_qty in evolution_stones:
        result = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, stone_id)
        )
        
        if result:
            actual_qty = result[0]['quantity'] if isinstance(result[0], dict) else result[0][0]
            total += actual_qty
            status = "✅" if actual_qty == expected_qty else "⚠️"
            print(f"  {status} {stone_name}: {actual_qty}个 (预期{expected_qty}个)")
        else:
            print(f"  ❌ {stone_name}: 0个 (预期{expected_qty}个)")
    
    print(f"\n📊 总计：{total}个进化石")
    
    if total == sum(q for _, _, q in evolution_stones):
        print("\n✅ 测试成功！所有进化石都已正确添加到背包")
        print("\n💡 现在可以登录游戏查看背包，验证进化石是否显示正确")
    else:
        print("\n⚠️  部分进化石添加失败")

if __name__ == '__main__':
    main()
