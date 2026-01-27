"""简单检查副本重置状态"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query
from datetime import date

# 查询需要重置的记录
records = execute_query("""
    SELECT user_id, dungeon_name, current_floor, last_reset_date 
    FROM player_dungeon_progress 
    WHERE current_floor > 1
""")

today = date.today()

print(f"当前日期: {today}")
print(f"需要重置的记录数: {len(records)}")
print()

if records:
    print("详细信息:")
    for r in records:
        print(f"  用户ID: {r['user_id']}, 副本: {r['dungeon_name']}, 当前层: {r['current_floor']}层, 上次重置: {r['last_reset_date']}")
else:
    print("✅ 所有副本都已在第1层")
