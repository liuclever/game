"""检查测试账号的副本进度"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

# 测试账号
test_user_ids = [100006, 100007]

print("检查副本进度...")
print("="*80)

for user_id in test_user_ids:
    # 获取玩家信息
    player = execute_query(
        "SELECT nickname FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not player:
        print(f"未找到 user_id: {user_id}")
        continue
    
    nickname = player[0]['nickname']
    print(f"\n{nickname} (ID: {user_id})")
    print("-"*80)
    
    # 获取副本进度
    progress = execute_query(
        """SELECT dungeon_name, current_floor, total_floors, floor_cleared, 
                  floor_event_type, resets_today, last_reset_date, loot_claimed
           FROM player_dungeon_progress 
           WHERE user_id = %s""",
        (user_id,)
    )
    
    if progress:
        print(f"副本进度记录数: {len(progress)}")
        for p in progress:
            print(f"\n  副本: {p['dungeon_name']}")
            print(f"  当前层: {p['current_floor']}/{p['total_floors']}")
            print(f"  本层已通关: {p.get('floor_cleared', False)}")
            print(f"  事件类型: {p.get('floor_event_type', 'N/A')}")
            print(f"  今日重置: {p.get('resets_today', 0)}次")
            print(f"  战利品已领取: {p.get('loot_claimed', True)}")
    else:
        print("  没有副本进度记录")

print("\n" + "="*80)
