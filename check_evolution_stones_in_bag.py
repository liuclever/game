#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查测试账号背包中的进化石
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

def main():
    print("="*70)
    print("检查测试账号背包中的进化石")
    print("="*70)
    
    user_id = 100006  # 测试50级A
    
    # 进化石列表
    evolution_stones = [
        (3001, "黄阶进化石"),
        (3002, "玄阶进化石"),
        (3003, "地阶进化石"),
        (3004, "天阶进化石"),
        (3005, "飞马进化石"),
        (3006, "天龙进化石"),
    ]
    
    print(f"\n📦 账号 {user_id} (测试50级A) 的进化石：\n")
    
    total_stones = 0
    
    for stone_id, stone_name in evolution_stones:
        result = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, stone_id)
        )
        
        if result:
            quantity = result[0]['quantity'] if isinstance(result[0], dict) else result[0][0]
            total_stones += quantity
            print(f"  ✅ {stone_name} (ID:{stone_id}): {quantity}个")
        else:
            print(f"  ❌ {stone_name} (ID:{stone_id}): 0个")
    
    print(f"\n📊 总计：{total_stones}个进化石")
    
    if total_stones > 0:
        print(f"\n✅ 测试成功！背包中有进化石，说明掉落功能正常工作")
    else:
        print(f"\n⚠️  背包中没有进化石")

if __name__ == '__main__':
    main()
