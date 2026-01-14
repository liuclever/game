#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
给测试联盟1添加战功用于测试
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query, execute_update

# 查找测试联盟1
sql_find = "SELECT id, name, war_honor, war_honor_history FROM alliances WHERE name = '测试联盟1'"
rows = execute_query(sql_find, ())

if not rows:
    print("未找到'测试联盟1'")
    sys.exit(1)

alliance = rows[0]
alliance_id = alliance['id']
current_honor = alliance.get('war_honor', 0) or 0
current_history = alliance.get('war_honor_history', 0) or 0

print(f"联盟：{alliance['name']} (ID: {alliance_id})")
print(f"当前战功: {current_honor}")
print(f"历史战功: {current_history}")
print()

# 添加50战功（足够测试所有兑换选项）
honor_to_add = 50
new_honor = current_honor + honor_to_add
new_history = current_history + honor_to_add

sql_update = "UPDATE alliances SET war_honor = %s, war_honor_history = %s WHERE id = %s"
execute_update(sql_update, (new_honor, new_history, alliance_id))

print(f"已添加 {honor_to_add} 战功")
print(f"新当前战功: {new_honor}")
print(f"新历史战功: {new_history}")
print("完成！")
