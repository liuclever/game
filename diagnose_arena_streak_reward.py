#!/usr/bin/env python3
"""
诊断连胜竞技场奖励无法领取的问题

检查：
1. 数据库表结构是否正确
2. 用户的连胜记录
3. 已领取的奖励记录
4. 领取条件是否满足
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query
import json


def diagnose_arena_streak_reward(user_id=None):
    """诊断连胜竞技场奖励问题"""
    
    print("=" * 80)
    print("连胜竞技场奖励诊断")
    print("=" * 80)
    print()
    
    # 1. 检查表结构
    print("【1. 检查数据库表结构】")
    try:
        # 检查 arena_streak 表
        columns = execute_query("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'game_tower' AND TABLE_NAME = 'arena_streak'
            ORDER BY ORDINAL_POSITION
        """)
        
        print(f"✓ arena_streak 表存在，共 {len(columns)} 个字段:")
        for col in columns:
            print(f"  - {col['COLUMN_NAME']}: {col['COLUMN_TYPE']}")
        print()
        
    except Exception as e:
        print(f"✗ 检查表结构失败: {e}")
        print()
        return
    
    # 2. 查看所有用户的连胜记录
    print("【2. 查看今日连胜记录】")
    try:
        from datetime import datetime
        today = datetime.now().date()
        
        records = execute_query("""
            SELECT a.user_id, p.nickname, a.current_streak, a.max_streak_today, 
                   a.claimed_rewards, a.claimed_grand_prize, a.record_date
            FROM arena_streak a
            LEFT JOIN player p ON a.user_id = p.user_id
            WHERE a.record_date = %s
            ORDER BY a.max_streak_today DESC
        """, (today,))
        
        if records:
            print(f"✓ 找到 {len(records)} 条今日记录:")
            for r in records:
                claimed = json.loads(r.get('claimed_rewards') or '[]')
                print(f"\n  用户ID: {r['user_id']} ({r['nickname'] or '未命名'})")
                print(f"    当前连胜: {r['current_streak']}")
                print(f"    今日最高: {r['max_streak_today']}")
                print(f"    已领取奖励: {claimed}")
                print(f"    已领取大奖: {'是' if r.get('claimed_grand_prize') else '否'}")
                
                # 检查可领取的奖励
                can_claim = []
                for level in [1, 2, 3, 4, 5, 6]:
                    if r['max_streak_today'] >= level and level not in claimed:
                        can_claim.append(level)
                
                if can_claim:
                    print(f"    可领取奖励: {can_claim}")
                else:
                    print(f"    可领取奖励: 无")
        else:
            print("✗ 今日暂无连胜记录")
        print()
        
    except Exception as e:
        print(f"✗ 查询连胜记录失败: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    # 3. 如果指定了用户ID，详细检查该用户
    if user_id:
        print(f"【3. 详细检查用户 {user_id}】")
        try:
            from datetime import datetime
            today = datetime.now().date()
            
            record = execute_query("""
                SELECT * FROM arena_streak 
                WHERE user_id = %s AND record_date = %s
            """, (user_id, today))
            
            if record:
                r = record[0]
                claimed = json.loads(r.get('claimed_rewards') or '[]')
                
                print(f"✓ 找到用户记录:")
                print(f"  当前连胜: {r['current_streak']}")
                print(f"  今日最高: {r['max_streak_today']}")
                print(f"  今日战斗次数: {r.get('total_battles_today', 0)}")
                print(f"  已领取奖励: {claimed}")
                print(f"  已领取大奖: {'是' if r.get('claimed_grand_prize') else '否'}")
                print()
                
                # 检查每个奖励等级
                print("  奖励领取状态:")
                for level in [1, 2, 3, 4, 5, 6]:
                    can_claim = r['max_streak_today'] >= level
                    is_claimed = level in claimed
                    
                    status = "✓ 已领取" if is_claimed else ("✓ 可领取" if can_claim else "✗ 未达成")
                    print(f"    {level}连胜: {status} (需要{level}连胜，当前最高{r['max_streak_today']}连胜)")
                print()
                
                # 检查大奖领取条件
                print("  连胜大奖领取条件:")
                
                # 获取今日连胜王
                streak_king = execute_query("""
                    SELECT user_id, max_streak_today 
                    FROM arena_streak 
                    WHERE record_date = %s 
                    ORDER BY max_streak_today DESC LIMIT 1
                """, (today,))
                
                if streak_king:
                    king_id = streak_king[0]['user_id']
                    king_streak = streak_king[0]['max_streak_today']
                    
                    is_king = king_id == user_id
                    is_claimed = r.get('claimed_grand_prize', 0)
                    
                    print(f"    今日连胜王: 用户{king_id} ({king_streak}连胜)")
                    print(f"    当前用户是连胜王: {'是' if is_king else '否'}")
                    print(f"    已领取大奖: {'是' if is_claimed else '否'}")
                    
                    if is_king and not is_claimed:
                        print(f"    ✓ 可以领取连胜大奖")
                    elif is_king and is_claimed:
                        print(f"    ✗ 已经领取过连胜大奖")
                    else:
                        print(f"    ✗ 不是连胜王，无法领取大奖")
                else:
                    print(f"    ✗ 今日暂无连胜王")
                print()
                
            else:
                print(f"✗ 未找到用户 {user_id} 的今日记录")
                print()
                
        except Exception as e:
            print(f"✗ 检查用户记录失败: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    # 4. 检查 claimed_rewards 字段的数据类型
    print("【4. 检查 claimed_rewards 字段数据】")
    try:
        from datetime import datetime
        today = datetime.now().date()
        
        records = execute_query("""
            SELECT user_id, claimed_rewards, 
                   LENGTH(claimed_rewards) as len,
                   claimed_rewards IS NULL as is_null
            FROM arena_streak 
            WHERE record_date = %s
            LIMIT 5
        """, (today,))
        
        if records:
            print(f"✓ 检查前5条记录的 claimed_rewards 字段:")
            for r in records:
                print(f"  用户{r['user_id']}: ")
                print(f"    原始值: {repr(r['claimed_rewards'])}")
                print(f"    长度: {r['len']}")
                print(f"    是否NULL: {r['is_null']}")
                
                # 尝试解析JSON
                try:
                    if r['claimed_rewards']:
                        parsed = json.loads(r['claimed_rewards'])
                        print(f"    解析后: {parsed} (类型: {type(parsed).__name__})")
                    else:
                        print(f"    解析后: [] (空值)")
                except Exception as e:
                    print(f"    ✗ JSON解析失败: {e}")
                print()
        else:
            print("✗ 今日暂无记录")
        print()
        
    except Exception as e:
        print(f"✗ 检查字段数据失败: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    print("=" * 80)
    print("诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    # 如果提供了用户ID参数，则详细检查该用户
    user_id = None
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print(f"错误：用户ID必须是数字")
            sys.exit(1)
    
    diagnose_arena_streak_reward(user_id)
