#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查土地占领联盟是否存在"""

import sys
import os
import io

# 设置标准输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query

# 从图片中看到的联盟名称
alliance_names = [
    'ぜ紫月遮天づ',
    '蹲街_浅/唱_季`沫✨',
    '明月'
]

print("=" * 50)
print("检查土地占领联盟是否存在")
print("=" * 50)

for name in alliance_names:
    sql = "SELECT id, name FROM alliances WHERE name = %s"
    rows = execute_query(sql, (name,))
    if rows:
        alliance = rows[0]
        print(f"[存在] 联盟: {alliance['name']} (ID: {alliance['id']})")
    else:
        print(f"[不存在] 联盟: {name}")

# 同时查询土地占领表，看哪些联盟ID在占领表中
print("\n" + "=" * 50)
print("查询土地占领记录")
print("=" * 50)

sql = """
    SELECT 
        o.land_id,
        o.alliance_id,
        a.name AS alliance_name,
        o.occupied_at
    FROM alliance_land_occupation o
    LEFT JOIN alliances a ON a.id = o.alliance_id
    ORDER BY o.land_id
"""
rows = execute_query(sql)
if rows:
    for row in rows:
        if row['alliance_name']:
            print(f"土地ID {row['land_id']}: 联盟 {row['alliance_name']} (ID: {row['alliance_id']}) - {row['occupied_at']}")
        else:
            print(f"土地ID {row['land_id']}: 联盟ID {row['alliance_id']} (联盟不存在!)")
else:
    print("没有找到土地占领记录")
