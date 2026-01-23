"""诊断召唤之王正赛自己和自己打的问题"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query
from datetime import datetime, timedelta

def diagnose_self_match():
    """诊断自己和自己打的问题"""
    
    print("=" * 80)
    print("诊断召唤之王正赛自己和自己打的问题")
    print("=" * 80)
    print()
    
    # 1. 获取当前赛季
    print("【1. 获取当前赛季】")
    
    # 计算当前赛季（基于周数）
    now = datetime.now()
    week_number = now.isocalendar()[1]
    year = now.year
    season = f"{year}W{week_number:02d}"
    
    print(f"当前赛季：{season}")
    print()
    
    # 2. 检查正赛记录
    print("【2. 检查正赛记录】")
    
    stages = ['32', '16', '8', '4', '2', 'champion']
    
    for stage in stages:
        print(f"\n{stage}强赛：")
        
        # 查询该阶段的所有记录
        records = execute_query(
            """SELECT user_id, opponent_id, is_winner, is_bye, match_id, battle_time
               FROM king_final_stage
               WHERE season = %s AND stage = %s
               ORDER BY match_id, user_id""",
            (season, stage)
        )
        
        if not records:
            print(f"  - 没有记录")
            continue
        
        print(f"  - 共 {len(records)} 条记录")
        
        # 检查重复的user_id
        user_ids = [r['user_id'] for r in records]
        unique_user_ids = set(user_ids)
        
        if len(user_ids) != len(unique_user_ids):
            print(f"  ⚠️  发现重复的玩家ID！")
            from collections import Counter
            duplicates = [uid for uid, count in Counter(user_ids).items() if count > 1]
            for uid in duplicates:
                count = user_ids.count(uid)
                print(f"     - 玩家 {uid} 有 {count} 条记录")
        
        # 检查自己和自己打的情况
        self_matches = [r for r in records if r['opponent_id'] == r['user_id']]
        if self_matches:
            print(f"  ❌ 发现自己和自己打的情况：")
            for r in self_matches:
                print(f"     - 玩家 {r['user_id']} vs {r['opponent_id']} (match_id: {r['match_id']})")
        
        # 显示所有对战
        if records:
            print(f"\n  对战列表：")
            matches = {}
            for r in records:
                mid = r['match_id']
                if mid not in matches:
                    matches[mid] = []
                matches[mid].append(r)
            
            for mid, players in sorted(matches.items()):
                if len(players) == 1:
                    p = players[0]
                    if p['is_bye']:
                        print(f"    第{mid}场：玩家{p['user_id']} 轮空")
                    else:
                        print(f"    第{mid}场：玩家{p['user_id']} vs {p['opponent_id']} ⚠️")
                elif len(players) == 2:
                    p1, p2 = players
                    winner = "玩家" + str(p1['user_id'] if p1['is_winner'] else p2['user_id'])
                    print(f"    第{mid}场：玩家{p1['user_id']} vs 玩家{p2['user_id']} → {winner}获胜")
                else:
                    print(f"    第{mid}场：异常，有{len(players)}个玩家")
    
    print()
    print("=" * 80)
    print("诊断完成")
    print("=" * 80)
    print()
    
    # 3. 显示可能的原因
    print("【3. 可能的原因】")
    print()
    print("1. 重复记录：")
    print("   - 同一个玩家在同一阶段有多条记录")
    print("   - 导致配对时可能配到自己")
    print()
    print("2. 配对逻辑问题：")
    print("   - 代码中使用 random.shuffle() 打乱顺序")
    print("   - 然后两两配对：player_ids[i] vs player_ids[i+1]")
    print("   - 如果有重复ID，就可能配到自己")
    print()
    print("3. 数据异常：")
    print("   - 晋级时重复插入了记录")
    print("   - 或者手动修改数据库导致重复")
    print()
    
    # 4. 显示解决方案
    print("【4. 解决方案】")
    print()
    print("方案1：去重")
    print("  在配对前，对 player_ids 进行去重")
    print("  player_ids = list(set(player_ids))")
    print()
    print("方案2：检查重复")
    print("  在配对时，检查是否配到自己")
    print("  if player1_id == player2_id: continue")
    print()
    print("方案3：修复数据")
    print("  删除重复的记录")
    print("  DELETE FROM king_final_stage WHERE ...")
    print()
    print("=" * 80)


if __name__ == "__main__":
    diagnose_self_match()
