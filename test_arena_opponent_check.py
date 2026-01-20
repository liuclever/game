#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试连胜竞技场对手检查功能

验证：
1. 只匹配有出战幻兽的玩家
2. 不会匹配没有出战幻兽的玩家
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query


def test_opponent_matching():
    """测试对手匹配逻辑"""
    
    print("=" * 80)
    print("连胜竞技场对手匹配测试")
    print("=" * 80)
    print()
    
    # 1. 统计玩家情况
    print("【1. 玩家统计】")
    
    total_players = execute_query("SELECT COUNT(*) as count FROM player")[0]['count']
    print(f"  总玩家数: {total_players}")
    
    # 有出战幻兽的玩家
    players_with_team = execute_query("""
        SELECT COUNT(DISTINCT user_id) as count 
        FROM player_beast 
        WHERE is_in_team = 1
    """)[0]['count']
    print(f"  有出战幻兽的玩家: {players_with_team}")
    
    # 没有出战幻兽的玩家
    players_without_team = total_players - players_with_team
    print(f"  没有出战幻兽的玩家: {players_without_team}")
    print()
    
    # 2. 测试匹配逻辑（模拟不同等级的玩家）
    print("【2. 测试对手匹配】")
    
    test_levels = [10, 20, 30, 40, 50]
    
    for level in test_levels:
        tier_start = (level - 1) // 10 * 10 + 1
        tier_end = tier_start + 9
        
        # 旧的匹配逻辑（不检查出战幻兽）
        old_opponents = execute_query("""
            SELECT user_id, nickname, level 
            FROM player 
            WHERE level BETWEEN %s AND %s 
            ORDER BY RAND() 
            LIMIT 5
        """, (tier_start, tier_end))
        
        # 新的匹配逻辑（只匹配有出战幻兽的玩家）
        new_opponents = execute_query("""
            SELECT DISTINCT p.user_id, p.nickname, p.level 
            FROM player p
            INNER JOIN player_beast pb ON p.user_id = pb.user_id
            WHERE p.level BETWEEN %s AND %s 
            AND pb.is_in_team = 1
            ORDER BY RAND() 
            LIMIT 5
        """, (tier_start, tier_end))
        
        print(f"\n  等级段 {tier_start}-{tier_end} (测试等级{level}):")
        print(f"    旧逻辑匹配到: {len(old_opponents)} 个对手")
        print(f"    新逻辑匹配到: {len(new_opponents)} 个对手")
        
        # 检查旧逻辑匹配的对手中有多少没有出战幻兽
        no_team_count = 0
        for opp in old_opponents:
            has_team = execute_query("""
                SELECT COUNT(*) as count 
                FROM player_beast 
                WHERE user_id = %s AND is_in_team = 1
            """, (opp['user_id'],))[0]['count']
            
            if has_team == 0:
                no_team_count += 1
        
        if no_team_count > 0:
            print(f"    警告: 旧逻辑中有 {no_team_count} 个对手没有出战幻兽")
        else:
            print(f"    OK: 旧逻辑匹配的对手都有出战幻兽")
        
        # 验证新逻辑匹配的对手都有出战幻兽
        all_have_team = True
        for opp in new_opponents:
            has_team = execute_query("""
                SELECT COUNT(*) as count 
                FROM player_beast 
                WHERE user_id = %s AND is_in_team = 1
            """, (opp['user_id'],))[0]['count']
            
            if has_team == 0:
                all_have_team = False
                break
        
        if all_have_team:
            print(f"    OK: 新逻辑匹配的对手都有出战幻兽")
        else:
            print(f"    ERROR: 新逻辑匹配的对手中有人没有出战幻兽")
    
    print()
    
    # 3. 检查具体的玩家
    print("【3. 检查没有出战幻兽的玩家】")
    
    players_no_team = execute_query("""
        SELECT p.user_id, p.nickname, p.level
        FROM player p
        LEFT JOIN player_beast pb ON p.user_id = pb.user_id AND pb.is_in_team = 1
        WHERE pb.user_id IS NULL
        LIMIT 10
    """)
    
    if players_no_team:
        print(f"  找到 {len(players_no_team)} 个没有出战幻兽的玩家:")
        for p in players_no_team:
            print(f"    - 用户{p['user_id']} ({p['nickname'] or '未命名'}), 等级{p['level']}")
        
        # 验证这些玩家不会被新逻辑匹配
        print("\n  验证这些玩家不会被新逻辑匹配:")
        for p in players_no_team:
            level = p['level']
            tier_start = (level - 1) // 10 * 10 + 1
            tier_end = tier_start + 9
            
            matched = execute_query("""
                SELECT DISTINCT p.user_id
                FROM player p
                INNER JOIN player_beast pb ON p.user_id = pb.user_id
                WHERE p.user_id = %s
                AND p.level BETWEEN %s AND %s 
                AND pb.is_in_team = 1
            """, (p['user_id'], tier_start, tier_end))
            
            if matched:
                print(f"    ERROR: 用户{p['user_id']} 仍然被匹配（不应该发生）")
            else:
                print(f"    OK: 用户{p['user_id']} 不会被匹配")
    else:
        print("  OK: 所有玩家都有出战幻兽")
    
    print()
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_opponent_matching()
