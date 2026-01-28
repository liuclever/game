"""检查数据库中是否有宝箱事件"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update

# 检查宝箱事件
records = execute_query("""
    SELECT user_id, dungeon_name, current_floor, floor_event_type 
    FROM player_dungeon_progress 
    WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
""")

print(f"数据库中的宝箱事件记录数: {len(records)}")

if records:
    print("\n详细信息:")
    for r in records:
        print(f"  用户{r['user_id']} - {r['dungeon_name']} - 第{r['current_floor']}层 - {r['floor_event_type']}")
    
    print("\n需要修复这些记录！")
    choice = input("\n是否将这些宝箱事件改为幻兽事件？(输入 yes 确认): ")
    if choice.lower() == 'yes':
        result = execute_update("""
            UPDATE player_dungeon_progress 
            SET floor_event_type = 'beast' 
            WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
        """)
        print(f"\n✅ 已修复 {result} 条记录，将宝箱事件改为幻兽事件")
else:
    print("\n✅ 数据库中没有宝箱事件，状态正常")
