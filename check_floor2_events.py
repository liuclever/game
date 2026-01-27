"""检查第2层的事件类型"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update

print("=" * 60)
print("检查第2层的事件类型")
print("=" * 60)

# 查询所有第2层的记录
records = execute_query("""
    SELECT 
        pdp.user_id,
        p.nickname,
        pdp.dungeon_name,
        pdp.current_floor,
        pdp.floor_event_type,
        pdp.floor_cleared
    FROM player_dungeon_progress pdp
    JOIN player p ON pdp.user_id = p.user_id
    WHERE pdp.current_floor = 2
    ORDER BY pdp.user_id, pdp.dungeon_name
""")

print(f"\n第2层的记录数: {len(records)}")

if records:
    print("\n详细信息:")
    problem_count = 0
    for r in records:
        nickname = r['nickname'] or f"玩家{r['user_id']}"
        event_type = r['floor_event_type']
        
        # 第2层应该是beast事件
        is_problem = event_type in ['climb', 'vitality_spring', 'rps', 'giant_chest', 'mystery_chest']
        
        if is_problem:
            problem_count += 1
            status = "❌ 错误"
        else:
            status = "✅ 正确"
        
        print(f"  {status} - {nickname} - {r['dungeon_name']}")
        print(f"      事件类型: {event_type}")
        print(f"      已通关: {'是' if r['floor_cleared'] else '否'}")
        print()
    
    if problem_count > 0:
        print(f"\n⚠️  发现 {problem_count} 条错误记录（第2层不应该是随机事件或宝箱事件）")
        print("\n是否修复这些记录？")
        choice = input("输入 yes 将这些记录的事件类型改为 beast: ")
        if choice.lower() == 'yes':
            result = execute_update("""
                UPDATE player_dungeon_progress
                SET floor_event_type = 'beast'
                WHERE current_floor = 2
                AND floor_event_type IN ('climb', 'vitality_spring', 'rps', 'giant_chest', 'mystery_chest')
            """)
            print(f"\n✅ 已修复 {result} 条记录")
    else:
        print(f"\n✅ 所有第2层记录都正确（事件类型为beast）")
else:
    print("\n没有玩家在第2层")

print("\n" + "=" * 60)
