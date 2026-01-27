"""检查特定用户的副本状态"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

# 查询宁静之森和森林秘境的进度
dungeons = ['宁静之森', '森林秘境']

print("=" * 60)
print("检查宁静之森和森林秘境的副本状态")
print("=" * 60)

for dungeon_name in dungeons:
    print(f"\n【{dungeon_name}】")
    records = execute_query("""
        SELECT 
            pdp.user_id,
            p.nickname,
            pdp.current_floor,
            pdp.floor_event_type,
            pdp.floor_cleared,
            pdp.loot_claimed
        FROM player_dungeon_progress pdp
        JOIN player p ON pdp.user_id = p.user_id
        WHERE pdp.dungeon_name = %s
        ORDER BY pdp.user_id
    """, (dungeon_name,))
    
    if not records:
        print(f"  没有玩家挑战过此副本")
        continue
    
    for r in records:
        nickname = r['nickname'] or f"玩家{r['user_id']}"
        print(f"  {nickname} (ID: {r['user_id']})")
        print(f"    当前层数: {r['current_floor']}")
        print(f"    事件类型: {r['floor_event_type']}")
        print(f"    已通关: {'是' if r['floor_cleared'] else '否'}")
        print(f"    已领取战利品: {'是' if r['loot_claimed'] else '否'}")
        
        # 检查是否是问题状态
        if r['current_floor'] == 2 and r['floor_event_type'] in ['giant_chest', 'mystery_chest']:
            print(f"    ⚠️  发现宝箱事件！这会导致前端显示问题")
        elif r['current_floor'] == 2 and r['floor_event_type'] == 'beast' and not r['floor_cleared']:
            print(f"    ✅ 状态正常（第2层幻兽事件，未通关）")

print("\n" + "=" * 60)
