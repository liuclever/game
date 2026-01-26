"""修复副本宝箱事件数据

问题：部分玩家的副本进度中，floor_event_type 被设置为 'giant_chest' 或 'mystery_chest'，
导致前端显示异常（空白页面，无法挑战幻兽，无法前进）。

解决方案：将所有宝箱事件改为幻兽事件（'beast'）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update


def fix_chest_events():
    """修复宝箱事件数据"""
    
    print("=" * 60)
    print("修复副本宝箱事件数据")
    print("=" * 60)
    
    # 1. 查看当前有多少宝箱事件
    print("\n【步骤1】查看当前宝箱事件数量")
    sql = """
        SELECT 
            COUNT(*) as total_count,
            SUM(CASE WHEN floor_event_type = 'giant_chest' THEN 1 ELSE 0 END) as giant_chest_count,
            SUM(CASE WHEN floor_event_type = 'mystery_chest' THEN 1 ELSE 0 END) as mystery_chest_count
        FROM player_dungeon_progress
        WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
    """
    results = execute_query(sql)
    
    if results:
        stat = results[0]
        total_count = stat.get('total_count', 0)
        giant_chest_count = stat.get('giant_chest_count', 0)
        mystery_chest_count = stat.get('mystery_chest_count', 0)
        
        print(f"  需要修复的记录数: {total_count}")
        print(f"    巨型宝箱: {giant_chest_count}")
        print(f"    神秘宝箱: {mystery_chest_count}")
        
        if total_count == 0:
            print("\n✅ 没有需要修复的记录")
            return
    else:
        print("  ❌ 查询失败")
        return
    
    # 2. 显示受影响的玩家和副本
    print("\n【步骤2】显示受影响的玩家和副本")
    sql = """
        SELECT user_id, dungeon_name, current_floor, floor_event_type, floor_cleared
        FROM player_dungeon_progress
        WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
        ORDER BY user_id, dungeon_name
    """
    results = execute_query(sql)
    
    if results:
        print(f"\n受影响的记录（共 {len(results)} 条）:")
        for row in results:
            user_id = row.get('user_id')
            dungeon_name = row.get('dungeon_name', '')
            current_floor = row.get('current_floor', 0)
            floor_event_type = row.get('floor_event_type', '')
            floor_cleared = row.get('floor_cleared', False)
            
            status = "已通关" if floor_cleared else "未通关"
            print(f"  玩家 {user_id} - {dungeon_name} 第{current_floor}层 - {floor_event_type} ({status})")
    
    # 3. 执行修复
    print("\n【步骤3】执行修复")
    confirm = input("\n是否将所有宝箱事件改为幻兽事件？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消修复")
        return
    
    try:
        result = execute_update("""
            UPDATE player_dungeon_progress
            SET floor_event_type = 'beast'
            WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
        """)
        print(f"✅ 修复成功，共修复 {result} 条记录")
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return
    
    # 4. 验证修复结果
    print("\n【步骤4】验证修复结果")
    sql = """
        SELECT COUNT(*) as remaining_count
        FROM player_dungeon_progress
        WHERE floor_event_type IN ('giant_chest', 'mystery_chest')
    """
    results = execute_query(sql)
    
    if results:
        remaining_count = results[0].get('remaining_count', 0)
        if remaining_count == 0:
            print("✅ 所有宝箱事件已成功修复为幻兽事件")
        else:
            print(f"❌ 仍有 {remaining_count} 条记录未修复")
    
    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)
    
    print("\n【注意事项】")
    print("1. 修复后，玩家需要刷新页面才能看到更新")
    print("2. 如果玩家当前正在副本中，建议让他们返回首页后重新进入")
    print("3. 后端服务需要重启以应用新的事件生成逻辑")


def check_event_distribution():
    """检查副本事件类型分布"""
    print("\n" + "=" * 60)
    print("副本事件类型分布统计")
    print("=" * 60)
    
    sql = """
        SELECT 
            floor_event_type,
            COUNT(*) as count,
            COUNT(DISTINCT user_id) as user_count
        FROM player_dungeon_progress
        GROUP BY floor_event_type
        ORDER BY count DESC
    """
    results = execute_query(sql)
    
    if results:
        print("\n事件类型分布:")
        total = sum(row.get('count', 0) for row in results)
        for row in results:
            event_type = row.get('floor_event_type', 'NULL')
            count = row.get('count', 0)
            user_count = row.get('user_count', 0)
            percentage = (count / total * 100) if total > 0 else 0
            
            print(f"  {event_type or '(空)'}: {count} 条记录 ({percentage:.1f}%), {user_count} 个玩家")


if __name__ == "__main__":
    fix_chest_events()
    check_event_distribution()
