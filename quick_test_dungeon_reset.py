"""快速测试副本重置功能

不需要确认，直接查看当前状态
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query


def quick_test():
    """快速查看副本状态"""
    
    print("=" * 60)
    print("副本进度快速查看")
    print("=" * 60)
    
    # 测试账号
    test_user_id = 100006  # 测试50级A
    
    # 查看测试账号的副本进度
    print(f"\n测试账号 {test_user_id} 的副本进度:")
    sql = """
        SELECT dungeon_name, current_floor, total_floors, 
               floor_cleared, resets_today, last_reset_date
        FROM player_dungeon_progress
        WHERE user_id = %s
        ORDER BY dungeon_name
    """
    results = execute_query(sql, (test_user_id,))
    
    if not results:
        print(f"  ❌ 没有副本进度记录")
        return
    
    for row in results:
        dungeon_name = row.get('dungeon_name', '')
        current_floor = row.get('current_floor', 0)
        total_floors = row.get('total_floors', 0)
        floor_cleared = row.get('floor_cleared', False)
        resets_today = row.get('resets_today', 0)
        last_reset_date = row.get('last_reset_date')
        
        status = "✅" if current_floor == 1 else "❌"
        print(f"\n  {status} {dungeon_name}:")
        print(f"     当前层数: {current_floor}/{total_floors}")
        print(f"     本层已通关: {'是' if floor_cleared else '否'}")
        print(f"     今日重置次数: {resets_today}")
        print(f"     上次重置日期: {last_reset_date}")
    
    # 统计信息
    print(f"\n" + "=" * 60)
    sql = """
        SELECT 
            COUNT(DISTINCT user_id) as total_users,
            COUNT(*) as total_records,
            SUM(CASE WHEN current_floor > 1 THEN 1 ELSE 0 END) as need_reset_count,
            SUM(CASE WHEN current_floor = 1 THEN 1 ELSE 0 END) as already_reset_count
        FROM player_dungeon_progress
    """
    stats = execute_query(sql)
    if stats:
        stat = stats[0]
        print(f"全服统计:")
        print(f"  总玩家数: {stat.get('total_users', 0)}")
        print(f"  总副本记录数: {stat.get('total_records', 0)}")
        print(f"  需要重置的记录: {stat.get('need_reset_count', 0)} (层数 > 1)")
        print(f"  已在第1层的记录: {stat.get('already_reset_count', 0)}")
    
    print("=" * 60)


if __name__ == "__main__":
    quick_test()
