#!/usr/bin/env python3
"""
测试连胜竞技场 API 响应格式

直接调用后端函数，检查返回的数据格式
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query
from datetime import datetime
import json


def test_api_response():
    """测试 API 响应格式"""
    
    print("=" * 80)
    print("连胜竞技场 API 响应格式测试")
    print("=" * 80)
    print()
    
    # 查找一个有记录的用户
    today = datetime.now().date()
    records = execute_query("""
        SELECT * FROM arena_streak 
        WHERE max_streak_today > 0
        ORDER BY record_date DESC
        LIMIT 1
    """)
    
    if not records:
        print("没有找到任何连胜记录")
        return
    
    record = records[0]
    user_id = record['user_id']
    
    print(f"测试用户ID: {user_id}")
    print(f"记录日期: {record['record_date']}")
    print()
    
    # 1. 检查数据库中的原始数据
    print("【1. 数据库原始数据】")
    print(f"  claimed_rewards (原始): {repr(record.get('claimed_rewards'))}")
    print(f"  claimed_rewards (类型): {type(record.get('claimed_rewards')).__name__}")
    print()
    
    # 2. 模拟 get_today_record 函数的处理
    print("【2. get_today_record 函数处理后】")
    claimed_rewards_str = record.get('claimed_rewards') or '[]'
    claimed_rewards = json.loads(claimed_rewards_str)
    print(f"  claimed_rewards (解析后): {claimed_rewards}")
    print(f"  claimed_rewards (类型): {type(claimed_rewards).__name__}")
    print()
    
    # 3. 模拟 jsonify 的序列化
    print("【3. jsonify 序列化后】")
    response_data = {
        "ok": True,
        "current_streak": record['current_streak'],
        "max_streak_today": record['max_streak_today'],
        "claimed_rewards": claimed_rewards,
        "claimed_grand_prize": record.get('claimed_grand_prize', 0)
    }
    
    # 模拟 JSON 序列化
    json_str = json.dumps(response_data)
    print(f"  JSON 字符串: {json_str}")
    print()
    
    # 4. 模拟前端接收并解析
    print("【4. 前端解析后】")
    parsed_data = json.loads(json_str)
    print(f"  claimed_rewards: {parsed_data['claimed_rewards']}")
    print(f"  claimed_rewards (类型): {type(parsed_data['claimed_rewards']).__name__}")
    print()
    
    # 5. 测试前端的判断逻辑
    print("【5. 前端判断逻辑测试】")
    claimed_rewards_frontend = parsed_data['claimed_rewards']
    max_streak = parsed_data['max_streak_today']
    
    for level in [1, 2, 3, 4, 5, 6]:
        can_claim = max_streak >= level
        is_claimed = level in claimed_rewards_frontend
        
        # 模拟前端的条件判断
        # v-if="canClaim(level) && !claimedRewards.includes(level)"
        show_claim_button = can_claim and not is_claimed
        
        status = "显示[领取]按钮" if show_claim_button else (
            "显示[已领取]" if is_claimed else "显示[未达成]"
        )
        
        print(f"  {level}连胜: {status}")
        print(f"    - canClaim({level}): {can_claim} (max_streak={max_streak})")
        print(f"    - {level} in claimedRewards: {is_claimed}")
        print(f"    - 显示领取按钮: {show_claim_button}")
    
    print()
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_api_response()
