"""测试副本事件生成逻辑"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 导入事件生成函数
from interfaces.routes.dungeon_routes import generate_floor_event_type

print("=" * 60)
print("测试副本事件生成逻辑")
print("=" * 60)

print("\n【测试第2层事件生成】")
print("运行100次，统计事件类型分布：")

event_counts = {}
for i in range(100):
    event_type = generate_floor_event_type(2)
    event_counts[event_type] = event_counts.get(event_type, 0) + 1

print(f"\n结果统计（共100次）：")
for event_type, count in event_counts.items():
    print(f"  {event_type}: {count}次 ({count}%)")

if 'giant_chest' in event_counts or 'mystery_chest' in event_counts:
    print(f"\n❌ 错误！第2层生成了宝箱事件")
    print(f"   这会导致前端显示问题")
elif event_counts.get('beast', 0) == 100:
    print(f"\n✅ 正确！第2层100%生成幻兽事件")
else:
    print(f"\n⚠️  警告！第2层生成了非幻兽事件")

print("\n" + "=" * 60)
print("测试所有楼层的事件生成")
print("=" * 60)

print("\n楼层事件类型：")
for floor in range(1, 36):
    event_type = generate_floor_event_type(floor)
    
    if floor in [5, 10, 15, 20, 25, 30]:
        expected = "随机事件（climb/vitality_spring/rps）"
    elif floor == 35:
        expected = "boss"
    else:
        expected = "beast"
    
    status = "✅" if (
        (floor in [5, 10, 15, 20, 25, 30] and event_type in ['climb', 'vitality_spring', 'rps']) or
        (floor == 35 and event_type == 'boss') or
        (floor not in [5, 10, 15, 20, 25, 30, 35] and event_type == 'beast')
    ) else "❌"
    
    print(f"  第{floor:2d}层: {event_type:20s} {status} (期望: {expected})")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

print("\n【结论】")
print("如果上面显示第2层100%生成幻兽事件，说明代码逻辑正确。")
print("如果用户仍然遇到问题，可能是：")
print("  1. 后端服务没有重启，还在运行旧代码")
print("  2. 前端缓存问题，需要强制刷新（Ctrl+F5）")
print("  3. 用户需要重新进入副本（从第1层重新开始）")
