"""测试副本每日重置功能

测试场景：
1. 查看测试账号的副本进度
2. 手动触发副本重置任务
3. 验证副本是否重置到第1层
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from datetime import date


def test_dungeon_reset():
    """测试副本重置功能"""
    
    print("=" * 60)
    print("测试副本每日重置功能")
    print("=" * 60)
    
    # 测试账号
    test_user_id = 100006  # 测试50级A
    
    # 1. 查看当前副本进度
    print(f"\n【步骤1】查看测试账号 {test_user_id} 的副本进度")
    sql = """
        SELECT user_id, dungeon_name, current_floor, total_floors, 
               floor_cleared, resets_today, last_reset_date, loot_claimed
        FROM player_dungeon_progress
        WHERE user_id = %s
        ORDER BY dungeon_name
    """
    results = execute_query(sql, (test_user_id,))
    
    if not results:
        print(f"❌ 测试账号 {test_user_id} 没有副本进度记录")
        return
    
    print(f"\n当前副本进度（共 {len(results)} 个副本）:")
    for row in results:
        dungeon_name = row.get('dungeon_name', '')
        current_floor = row.get('current_floor', 0)
        total_floors = row.get('total_floors', 0)
        floor_cleared = row.get('floor_cleared', False)
        resets_today = row.get('resets_today', 0)
        last_reset_date = row.get('last_reset_date')
        loot_claimed = row.get('loot_claimed', False)
        
        print(f"  {dungeon_name}:")
        print(f"    当前层数: {current_floor}/{total_floors}")
        print(f"    本层已通关: {'是' if floor_cleared else '否'}")
        print(f"    今日重置次数: {resets_today}")
        print(f"    上次重置日期: {last_reset_date}")
        print(f"    战利品已领取: {'是' if loot_claimed else '否'}")
    
    # 2. 查看所有玩家的副本进度统计
    print(f"\n【步骤2】查看所有玩家的副本进度统计")
    sql = """
        SELECT 
            COUNT(DISTINCT user_id) as total_users,
            COUNT(*) as total_records,
            SUM(CASE WHEN current_floor > 1 THEN 1 ELSE 0 END) as need_reset_count,
            AVG(current_floor) as avg_floor
        FROM player_dungeon_progress
    """
    stats = execute_query(sql)
    if stats:
        stat = stats[0]
        print(f"  总玩家数: {stat.get('total_users', 0)}")
        print(f"  总副本记录数: {stat.get('total_records', 0)}")
        print(f"  需要重置的记录数: {stat.get('need_reset_count', 0)} (当前层数 > 1)")
        print(f"  平均层数: {stat.get('avg_floor', 0):.2f}")
    
    # 3. 模拟每日重置任务
    print(f"\n【步骤3】执行副本每日重置任务（模拟）")
    print("注意：这将重置所有玩家的所有副本到第1层")
    
    confirm = input("\n是否继续执行重置？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消重置")
        return
    
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
        print(f"✅ 副本重置成功，共重置 {result} 条记录")
    except Exception as e:
        print(f"❌ 副本重置失败: {e}")
        return
    
    # 4. 验证重置结果
    print(f"\n【步骤4】验证重置结果")
    results = execute_query(sql, (test_user_id,))
    
    print(f"\n重置后的副本进度:")
    all_reset = True
    for row in results:
        dungeon_name = row.get('dungeon_name', '')
        current_floor = row.get('current_floor', 0)
        total_floors = row.get('total_floors', 0)
        floor_cleared = row.get('floor_cleared', False)
        resets_today = row.get('resets_today', 0)
        last_reset_date = row.get('last_reset_date')
        
        print(f"  {dungeon_name}:")
        print(f"    当前层数: {current_floor}/{total_floors}")
        print(f"    本层已通关: {'是' if floor_cleared else '否'}")
        print(f"    今日重置次数: {resets_today}")
        print(f"    上次重置日期: {last_reset_date}")
        
        if current_floor != 1:
            all_reset = False
            print(f"    ❌ 未重置到第1层")
        else:
            print(f"    ✅ 已重置到第1层")
    
    print("\n" + "=" * 60)
    if all_reset:
        print("✅ 所有副本已成功重置到第1层")
    else:
        print("❌ 部分副本未成功重置")
    print("=" * 60)
    
    # 5. 查看重置后的统计
    print(f"\n【步骤5】重置后的统计")
    stats = execute_query("""
        SELECT 
            COUNT(DISTINCT user_id) as total_users,
            COUNT(*) as total_records,
            SUM(CASE WHEN current_floor > 1 THEN 1 ELSE 0 END) as need_reset_count,
            AVG(current_floor) as avg_floor
        FROM player_dungeon_progress
    """)
    if stats:
        stat = stats[0]
        print(f"  总玩家数: {stat.get('total_users', 0)}")
        print(f"  总副本记录数: {stat.get('total_records', 0)}")
        print(f"  需要重置的记录数: {stat.get('need_reset_count', 0)} (当前层数 > 1)")
        print(f"  平均层数: {stat.get('avg_floor', 0):.2f}")


def check_scheduler_status():
    """检查定时任务状态"""
    print("\n" + "=" * 60)
    print("检查定时任务状态")
    print("=" * 60)
    
    try:
        from infrastructure.scheduler import _scheduler
        
        if _scheduler is None:
            print("❌ 定时任务调度器未启动")
            print("提示：需要启动后端服务才能启动定时任务调度器")
            return
        
        print("✅ 定时任务调度器已启动")
        
        # 查看所有任务
        jobs = _scheduler.get_jobs()
        print(f"\n当前已配置的定时任务（共 {len(jobs)} 个）:")
        
        for job in jobs:
            print(f"\n  任务ID: {job.id}")
            print(f"  任务名称: {job.name}")
            print(f"  触发器: {job.trigger}")
            print(f"  下次执行时间: {job.next_run_time}")
        
        # 检查副本重置任务
        dungeon_reset_job = None
        for job in jobs:
            if job.id == "daily_dungeon_reset":
                dungeon_reset_job = job
                break
        
        if dungeon_reset_job:
            print(f"\n✅ 找到副本每日重置任务")
            print(f"  下次执行时间: {dungeon_reset_job.next_run_time}")
        else:
            print(f"\n❌ 未找到副本每日重置任务")
            print("提示：需要更新 infrastructure/scheduler.py 并重启后端服务")
    
    except Exception as e:
        print(f"❌ 检查定时任务状态失败: {e}")


if __name__ == "__main__":
    test_dungeon_reset()
    check_scheduler_status()
