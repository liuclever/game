"""检查调度器状态"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("调度器状态检查")
print("=" * 60)

# 检查调度器模块
try:
    from infrastructure.scheduler import _scheduler
    
    if _scheduler is None:
        print("\n❌ 调度器未启动")
        print("   原因：_scheduler 变量为 None")
        print("\n解决方案：")
        print("   1. 确保后端服务正在运行")
        print("   2. 检查 interfaces/web_api/app.py 中是否调用了 start_scheduler()")
    else:
        print("\n✅ 调度器已启动")
        print(f"   调度器对象: {_scheduler}")
        print(f"   调度器状态: {'运行中' if _scheduler.running else '已停止'}")
        
        # 获取所有任务
        jobs = _scheduler.get_jobs()
        print(f"\n   已注册的定时任务数: {len(jobs)}")
        
        if jobs:
            print("\n   任务列表:")
            for job in jobs:
                print(f"     - {job.id}: {job.name}")
                print(f"       触发器: {job.trigger}")
                print(f"       下次执行: {job.next_run_time}")
                print()
        
        # 检查副本重置任务
        dungeon_reset_job = _scheduler.get_job('daily_dungeon_reset')
        if dungeon_reset_job:
            print("   ✅ 副本每日重置任务已注册")
            print(f"      任务ID: {dungeon_reset_job.id}")
            print(f"      下次执行时间: {dungeon_reset_job.next_run_time}")
        else:
            print("   ❌ 副本每日重置任务未注册")
            
except ImportError as e:
    print(f"\n❌ 无法导入调度器模块: {e}")
except Exception as e:
    print(f"\n❌ 检查调度器时出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

print("\n【重要说明】")
print("1. 定时任务只有在后端服务运行时才会执行")
print("2. 如果后端服务在00:00时没有运行，任务不会执行")
print("3. 如果后端服务在00:00之后启动，当天的00:00任务会被跳过")
print("4. 建议：保持后端服务24小时运行，或者使用系统服务管理工具")
