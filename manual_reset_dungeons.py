"""手动重置所有副本到第1层"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query
from datetime import date

print("=" * 60)
print("手动重置所有副本")
print("=" * 60)

# 先查看当前状态
records = execute_query("""
    SELECT COUNT(*) as count 
    FROM player_dungeon_progress 
    WHERE current_floor > 1
""")

count = records[0]['count'] if records else 0
print(f"\n当前需要重置的记录数: {count}")

if count == 0:
    print("\n✅ 所有副本都已在第1层，无需重置")
else:
    print(f"\n准备重置 {count} 条记录...")
    
    # 执行重置
    try:
        result = execute_update("""
            UPDATE player_dungeon_progress
            SET current_floor = 1,
                floor_cleared = TRUE,
                floor_event_type = 'beast',
                resets_today = 0,
                last_reset_date = CURDATE(),
                loot_claimed = TRUE
            WHERE current_floor > 1
        """)
        
        print(f"\n✅ 重置完成！共重置了 {result} 条记录")
        print(f"   - 所有副本已重置到第1层")
        print(f"   - 重置日期已更新为今天: {date.today()}")
        
    except Exception as e:
        print(f"\n❌ 重置失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
