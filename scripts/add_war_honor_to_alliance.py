#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
给指定联盟添加战功用于测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query, execute_update

def add_war_honor_to_alliance(alliance_name: str, honor_amount: int):
    """给指定联盟添加战功"""
    
    # 1. 查找联盟
    sql_find = "SELECT id, name, war_honor, war_honor_history FROM alliances WHERE name = %s"
    rows = execute_query(sql_find, (alliance_name,))
    
    if not rows:
        print(f"错误：找不到联盟 '{alliance_name}'")
        return
    
    alliance = rows[0]
    alliance_id = alliance['id']
    current_honor = alliance.get('war_honor', 0) or 0
    current_history = alliance.get('war_honor_history', 0) or 0
    
    print(f"找到联盟：{alliance['name']} (ID: {alliance_id})")
    print(f"当前战功: {current_honor}")
    print(f"历史战功: {current_history}")
    print()
    
    # 2. 更新战功
    new_honor = current_honor + honor_amount
    new_history = current_history + honor_amount
    
    sql_update = """
        UPDATE alliances 
        SET war_honor = %s, war_honor_history = %s 
        WHERE id = %s
    """
    
    execute_update(sql_update, (new_honor, new_history, alliance_id))
    
    print(f"已添加 {honor_amount} 战功")
    print(f"新当前战功: {new_honor}")
    print(f"新历史战功: {new_history}")
    print()
    print("更新完成！")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python add_war_honor_to_alliance.py <联盟名称> <战功数量>")
        print("示例: python add_war_honor_to_alliance.py 测试联盟1 50")
        sys.exit(1)
    
    alliance_name = sys.argv[1]
    try:
        honor_amount = int(sys.argv[2])
    except ValueError:
        print(f"错误：战功数量必须是数字，您输入的是: {sys.argv[2]}")
        sys.exit(1)
    
    try:
        add_war_honor_to_alliance(alliance_name, honor_amount)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
