#!/usr/bin/env python3
"""
修复连胜竞技场奖励无法领取的问题

可能的问题：
1. claimed_rewards 字段为 NULL 而不是空数组
2. claimed_rewards 字段包含无效的 JSON
3. 前端的 claimedRewards 没有正确初始化为数组

解决方案：
1. 检查并修复所有 NULL 或无效的 claimed_rewards 字段
2. 确保所有记录的 claimed_rewards 都是有效的 JSON 数组
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update
import json


def fix_arena_reward_issue():
    """修复连胜竞技场奖励问题"""
    
    print("=" * 80)
    print("修复连胜竞技场奖励问题")
    print("=" * 80)
    print()
    
    # 1. 检查所有记录的 claimed_rewards 字段
    print("【1. 检查 claimed_rewards 字段】")
    records = execute_query("""
        SELECT id, user_id, record_date, claimed_rewards,
               claimed_rewards IS NULL as is_null,
               LENGTH(claimed_rewards) as len
        FROM arena_streak
        ORDER BY record_date DESC
        LIMIT 20
    """)
    
    if not records:
        print("  没有找到任何记录")
        return
    
    print(f"  检查最近 {len(records)} 条记录:")
    
    null_count = 0
    empty_count = 0
    invalid_count = 0
    valid_count = 0
    
    for r in records:
        claimed_rewards = r.get('claimed_rewards')
        is_null = r.get('is_null')
        
        if is_null or claimed_rewards is None:
            null_count += 1
            print(f"    ✗ 记录 {r['id']} (用户{r['user_id']}, {r['record_date']}): NULL")
        elif claimed_rewards == '':
            empty_count += 1
            print(f"    ✗ 记录 {r['id']} (用户{r['user_id']}, {r['record_date']}): 空字符串")
        else:
            # 尝试解析 JSON
            try:
                parsed = json.loads(claimed_rewards)
                if isinstance(parsed, list):
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"    ✗ 记录 {r['id']} (用户{r['user_id']}, {r['record_date']}): 不是数组 - {type(parsed).__name__}")
            except Exception as e:
                invalid_count += 1
                print(f"    ✗ 记录 {r['id']} (用户{r['user_id']}, {r['record_date']}): JSON解析失败 - {e}")
    
    print()
    print(f"  统计:")
    print(f"    有效记录: {valid_count}")
    print(f"    NULL记录: {null_count}")
    print(f"    空字符串记录: {empty_count}")
    print(f"    无效JSON记录: {invalid_count}")
    print()
    
    # 2. 修复所有无效的记录
    if null_count + empty_count + invalid_count > 0:
        print("【2. 修复无效记录】")
        
        # 修复 NULL 和空字符串
        result = execute_update("""
            UPDATE arena_streak 
            SET claimed_rewards = '[]'
            WHERE claimed_rewards IS NULL OR claimed_rewards = ''
        """)
        
        print(f"  ✓ 已修复 NULL 和空字符串记录")
        
        # 检查是否还有无效的 JSON
        invalid_records = execute_query("""
            SELECT id, user_id, record_date, claimed_rewards
            FROM arena_streak
            WHERE claimed_rewards IS NOT NULL AND claimed_rewards != ''
        """)
        
        fixed_count = 0
        for r in invalid_records:
            try:
                json.loads(r['claimed_rewards'])
            except:
                # 无效的 JSON，修复为空数组
                execute_update(
                    "UPDATE arena_streak SET claimed_rewards = '[]' WHERE id = %s",
                    (r['id'],)
                )
                fixed_count += 1
                print(f"  ✓ 修复记录 {r['id']} (用户{r['user_id']}, {r['record_date']})")
        
        if fixed_count > 0:
            print(f"  ✓ 共修复 {fixed_count} 条无效JSON记录")
        
        print()
    
    # 3. 验证修复结果
    print("【3. 验证修复结果】")
    records = execute_query("""
        SELECT id, user_id, record_date, claimed_rewards
        FROM arena_streak
        ORDER BY record_date DESC
        LIMIT 10
    """)
    
    all_valid = True
    for r in records:
        try:
            parsed = json.loads(r['claimed_rewards'] or '[]')
            if not isinstance(parsed, list):
                all_valid = False
                print(f"  ✗ 记录 {r['id']} 仍然无效")
        except Exception as e:
            all_valid = False
            print(f"  ✗ 记录 {r['id']} JSON解析失败: {e}")
    
    if all_valid:
        print(f"  ✓ 所有记录都已修复，claimed_rewards 字段格式正确")
    
    print()
    
    # 4. 检查前端可能的问题
    print("【4. 前端问题排查建议】")
    print("  如果修复后仍然无法领取奖励，请检查：")
    print()
    print("  1. 浏览器控制台是否有错误信息")
    print("     - 打开浏览器开发者工具 (F12)")
    print("     - 查看 Console 标签页")
    print()
    print("  2. 网络请求是否正常")
    print("     - 打开浏览器开发者工具 (F12)")
    print("     - 查看 Network 标签页")
    print("     - 检查 /api/arena-streak/info 请求的响应")
    print("     - 确认 claimed_rewards 字段是数组格式")
    print()
    print("  3. 前端数据是否正确加载")
    print("     - 在浏览器控制台输入: console.log(this.claimedRewards)")
    print("     - 确认输出是数组格式，如: []")
    print()
    print("  4. 清除浏览器缓存")
    print("     - 按 Ctrl+Shift+Delete")
    print("     - 清除缓存和Cookie")
    print("     - 重新登录")
    print()
    
    print("=" * 80)
    print("修复完成")
    print("=" * 80)


if __name__ == "__main__":
    fix_arena_reward_issue()
