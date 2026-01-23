"""修复副本相关问题"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from datetime import datetime

print("="*80)
print("修复副本相关问题")
print("="*80)

# 问题1：清除移动状态
print("\n1. 清除玩家移动状态...")
test_user_ids = [100006, 100007]

for user_id in test_user_ids:
    player = execute_query(
        "SELECT nickname, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not player:
        continue
    
    nickname = player[0]['nickname']
    moving_to = player[0].get('moving_to')
    
    if moving_to:
        print(f"  {nickname}: 正在移动到 {moving_to}，清除移动状态...")
        execute_update(
            "UPDATE player SET moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
            (user_id,)
        )
        print(f"  ✓ 已清除")
    else:
        print(f"  {nickname}: 没有移动状态")

# 问题2：修复副本名称
print("\n2. 修复副本名称...")

# 查找所有使用了错误副本名称的记录
wrong_dungeons = execute_query(
    """SELECT DISTINCT dungeon_name 
       FROM player_dungeon_progress 
       WHERE dungeon_name NOT IN (
           '森林入口', '宁静之森(4-6级)', '宁静之森(7-9级)',
           '呼啸平原', '天罚山',
           '石工矿场', '幻灵湖畔',
           '回音之谷', '死亡沼泽',
           '日落海峡', '聚灵孤岛',
           '龙骨墓地', '巨龙冰原',
           '圣龙城郊', '皇城迷宫',
           '梦幻海湾', '幻光公园'
       )"""
)

if wrong_dungeons:
    print(f"  发现 {len(wrong_dungeons)} 个错误的副本名称:")
    for d in wrong_dungeons:
        print(f"    - {d['dungeon_name']}")
    
    # 修复映射
    name_mapping = {
        '森林秘境': '宁静之森(7-9级)',
        '宁静之森': '宁静之森(4-6级)',
    }
    
    for old_name, new_name in name_mapping.items():
        count = execute_query(
            "SELECT COUNT(*) as cnt FROM player_dungeon_progress WHERE dungeon_name = %s",
            (old_name,)
        )
        
        if count and count[0]['cnt'] > 0:
            print(f"\n  修复: {old_name} -> {new_name}")
            execute_update(
                "UPDATE player_dungeon_progress SET dungeon_name = %s WHERE dungeon_name = %s",
                (new_name, old_name)
            )
            print(f"  ✓ 已修复 {count[0]['cnt']} 条记录")
else:
    print("  ✓ 没有发现错误的副本名称")

# 问题3：检查修复后的状态
print("\n3. 检查修复后的状态...")

for user_id in test_user_ids:
    player = execute_query(
        "SELECT nickname, moving_to FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not player:
        continue
    
    nickname = player[0]['nickname']
    moving_to = player[0].get('moving_to')
    
    print(f"\n  {nickname} (ID: {user_id})")
    print(f"    移动状态: {'移动中' if moving_to else '正常'}")
    
    # 查看副本进度
    progress = execute_query(
        "SELECT dungeon_name, current_floor FROM player_dungeon_progress WHERE user_id = %s",
        (user_id,)
    )
    
    if progress:
        print(f"    副本进度:")
        for p in progress:
            print(f"      - {p['dungeon_name']}: {p['current_floor']}层")
    else:
        print(f"    副本进度: 无")

print("\n" + "="*80)
print("修复完成！")
print("\n现在可以：")
print("1. 刷新浏览器页面")
print("2. 重新进入副本")
print("3. 副本应该可以正常显示了")
