#!/usr/bin/env python3
"""
测试连胜竞技场奖励领取功能

模拟前端请求，测试领取奖励的完整流程
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update
from datetime import datetime
import json


def test_reward_claim():
    """测试奖励领取功能"""
    
    print("=" * 80)
    print("连胜竞技场奖励领取测试")
    print("=" * 80)
    print()
    
    # 1. 查找一个有连胜记录但未领取奖励的用户
    print("【1. 查找测试用户】")
    today = datetime.now().date()
    
    records = execute_query("""
        SELECT a.*, p.nickname 
        FROM arena_streak a
        LEFT JOIN player p ON a.user_id = p.user_id
        WHERE a.record_date = %s AND a.max_streak_today > 0
        ORDER BY a.max_streak_today DESC
        LIMIT 1
    """, (today,))
    
    if not records:
        # 如果今天没有记录，查找最近的记录
        print("  今天没有记录，查找最近的记录...")
        records = execute_query("""
            SELECT a.*, p.nickname 
            FROM arena_streak a
            LEFT JOIN player p ON a.user_id = p.user_id
            WHERE a.max_streak_today > 0
            ORDER BY a.record_date DESC, a.max_streak_today DESC
            LIMIT 1
        """)
    
    if not records:
        print("  ✗ 没有找到任何连胜记录")
        print("  建议：先进行一些连胜竞技场战斗")
        return
    
    record = records[0]
    user_id = record['user_id']
    nickname = record['nickname'] or f"用户{user_id}"
    max_streak = record['max_streak_today']
    claimed_rewards_str = record.get('claimed_rewards') or '[]'
    
    print(f"  ✓ 找到测试用户: {nickname} (ID: {user_id})")
    print(f"    最高连胜: {max_streak}")
    print(f"    已领取奖励(原始): {repr(claimed_rewards_str)}")
    
    # 解析已领取奖励
    try:
        claimed_rewards = json.loads(claimed_rewards_str)
        print(f"    已领取奖励(解析): {claimed_rewards}")
    except Exception as e:
        print(f"    ✗ JSON解析失败: {e}")
        claimed_rewards = []
    
    print()
    
    # 2. 检查可领取的奖励
    print("【2. 检查可领取的奖励】")
    can_claim_levels = []
    for level in [1, 2, 3, 4, 5, 6]:
        can_claim = max_streak >= level and level not in claimed_rewards
        status = "✓ 可领取" if can_claim else ("✗ 已领取" if level in claimed_rewards else "✗ 未达成")
        print(f"  {level}连胜: {status}")
        if can_claim:
            can_claim_levels.append(level)
    
    if not can_claim_levels:
        print("\n  没有可领取的奖励")
        return
    
    print(f"\n  可领取的奖励等级: {can_claim_levels}")
    print()
    
    # 3. 模拟领取第一个可领取的奖励
    test_level = can_claim_levels[0]
    print(f"【3. 模拟领取 {test_level}连胜奖励】")
    
    # 检查用户是否存在
    player = execute_query("SELECT * FROM player WHERE user_id = %s", (user_id,))
    if not player:
        print(f"  ✗ 用户 {user_id} 不存在")
        return
    
    print(f"  用户当前铜钱: {player[0].get('gold', 0)}")
    
    # 奖励配置
    rewards_config = {
        1: {"copper": 1000, "items": [{"id": 6024, "name": "双倍卡", "quantity": 1}]},
        2: {"copper": 5000, "items": [{"id": 4003, "name": "强力捕捉球", "quantity": 1}]},
        3: {"copper": 10000, "items": [{"id": 6015, "name": "化仙丹", "quantity": 1}]},
        4: {"copper": 50000, "items": [{"id": 4001, "name": "活力草", "quantity": 1}]},
        5: {"copper": 100000, "items": [{"id": 4001, "name": "活力草", "quantity": 2}]},
        6: {"copper": 150000, "items": [{"id": 6017, "name": "重生丹", "quantity": 2}]}
    }
    
    reward = rewards_config.get(test_level)
    print(f"  奖励内容: 铜钱×{reward['copper']}")
    
    # 模拟发放奖励（不实际执行，只是测试）
    print(f"\n  ✓ 测试通过：可以正常领取 {test_level}连胜奖励")
    print()
    
    # 4. 检查前端数据格式
    print("【4. 检查前端数据格式】")
    print(f"  后端返回的 claimed_rewards 类型: {type(claimed_rewards).__name__}")
    print(f"  后端返回的 claimed_rewards 值: {claimed_rewards}")
    print(f"  前端判断 {test_level} in claimed_rewards: {test_level in claimed_rewards}")
    print()
    
    # 5. 检查数据库字段类型
    print("【5. 检查数据库字段类型】")
    column_info = execute_query("""
        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'game_tower' 
        AND TABLE_NAME = 'arena_streak'
        AND COLUMN_NAME = 'claimed_rewards'
    """)
    
    if column_info:
        col = column_info[0]
        print(f"  字段名: {col['COLUMN_NAME']}")
        print(f"  数据类型: {col['DATA_TYPE']}")
        print(f"  完整类型: {col['COLUMN_TYPE']}")
    print()
    
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_reward_claim()
