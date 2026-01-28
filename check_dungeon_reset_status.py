"""检查副本重置状态

检查：
1. 当前有多少副本进度大于第1层
2. 这些进度的最后重置日期
3. 调度器是否正常运行
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query
from datetime import datetime, date


def check_dungeon_status():
    """检查副本重置状态"""
    
    print("=" * 60)
    print("副本重置状态检查")
    print("=" * 60)
    
    # 获取当前日期
    today = date.today()
    print(f"\n【当前日期】: {today}")
    
    # 检查所有副本进度
    print(f"\n【所有副本进度】")
    all_progress = execute_query("""
        SELECT 
            pdp.user_id,
            p.nickname,
            pdp.dungeon_name,
            pdp.current_floor,
            pdp.last_reset_date,
            pdp.resets_today,
            pdp.floor_cleared,
            pdp.floor_event_type
        FROM player_dungeon_progress pdp
        JOIN player p ON pdp.user_id = p.user_id
        ORDER BY pdp.current_floor DESC, pdp.user_id, pdp.dungeon_name
    """)
    
    if not all_progress:
        print("  没有任何副本进度记录")
        return
    
    # 统计信息
    total_count = len(all_progress)
    need_reset_count = 0
    already_reset_count = 0
    
    print(f"\n  总记录数: {total_count}")
    print(f"\n  详细信息:")
    
    for record in all_progress:
        user_id = record['user_id']
        nickname = record['nickname'] or f"玩家{user_id}"
        dungeon_name = record['dungeon_name']
        current_floor = record['current_floor']
        last_reset_date = record['last_reset_date']
        resets_today = record['resets_today']
        
        # 判断是否需要重置
        needs_reset = current_floor > 1
        
        if needs_reset:
            need_reset_count += 1
            status = "❌ 需要重置"
        else:
            already_reset_count += 1
            status = "✅ 已在第1层"
        
        # 检查最后重置日期
        reset_date_str = str(last_reset_date) if last_reset_date else "从未重置"
        is_today = last_reset_date == today if last_reset_date else False
        date_status = "（今日已重置）" if is_today else f"（上次重置: {reset_date_str}）"
        
        print(f"    {status} - {nickname} - {dungeon_name}")
        print(f"      当前层数: {current_floor}层")
        print(f"      重置日期: {reset_date_str} {date_status}")
        print(f"      今日重置次数: {resets_today}")
        print()
    
    # 汇总统计
    print(f"\n【统计汇总】")
    print(f"  总记录数: {total_count}")
    print(f"  已在第1层: {already_reset_count}")
    print(f"  需要重置: {need_reset_count}")
    
    if need_reset_count > 0:
        print(f"\n  ⚠️  发现 {need_reset_count} 条记录需要重置到第1层")
        print(f"  这些记录应该在每天00:00被自动重置")
    else:
        print(f"\n  ✅ 所有副本进度都已正确重置到第1层")
    
    # 检查调度器任务
    print(f"\n【调度器检查】")
    print(f"  定时任务配置:")
    print(f"    - 任务名称: daily_dungeon_reset")
    print(f"    - 执行时间: 每天 00:00")
    print(f"    - 任务函数: _run_daily_dungeon_reset()")
    print(f"    - 注册位置: infrastructure/scheduler.py 第488-495行")
    print(f"    - 启动位置: interfaces/web_api/app.py 第507-508行")
    
    # 检查后端服务是否运行
    print(f"\n【后端服务检查】")
    print(f"  请确认:")
    print(f"    1. 后端服务是否正在运行？")
    print(f"    2. 后端服务是否在00:00之前就已经启动？")
    print(f"    3. 后端服务是否有重启过（重启会导致调度器重新初始化）？")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)


def manual_reset_all():
    """手动重置所有副本到第1层"""
    print("\n" + "=" * 60)
    print("手动重置所有副本")
    print("=" * 60)
    
    # 询问确认
    confirm = input("\n是否要手动重置所有副本到第1层？(输入 yes 确认): ")
    if confirm.lower() != 'yes':
        print("已取消")
        return
    
    try:
        from infrastructure.db.connection import execute_update
        
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
        
        print(f"\n✅ 手动重置完成，共重置 {result} 条记录")
        
        # 再次检查状态
        print("\n重置后的状态:")
        check_dungeon_status()
        
    except Exception as e:
        print(f"\n❌ 手动重置失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_dungeon_status()
    
    # 询问是否需要手动重置
    print("\n" + "=" * 60)
    choice = input("是否需要手动重置所有副本？(输入 yes 进行手动重置): ")
    if choice.lower() == 'yes':
        manual_reset_all()

