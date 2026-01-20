#!/usr/bin/env python3
"""检查连胜竞技场历史记录"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query
import json

# 查询最近的记录
records = execute_query("""
    SELECT a.*, p.nickname 
    FROM arena_streak a
    LEFT JOIN player p ON a.user_id = p.user_id
    ORDER BY a.record_date DESC, a.max_streak_today DESC 
    LIMIT 10
""")

if records:
    print(f"找到 {len(records)} 条最近的记录:\n")
    for r in records:
        claimed = json.loads(r.get('claimed_rewards') or '[]')
        print(f"用户: {r['nickname'] or r['user_id']}")
        print(f"  日期: {r['record_date']}")
        print(f"  当前连胜: {r['current_streak']}")
        print(f"  最高连胜: {r['max_streak_today']}")
        print(f"  已领取奖励: {claimed}")
        print(f"  已领取大奖: {'是' if r.get('claimed_grand_prize') else '否'}")
        print()
else:
    print("数据库中没有任何连胜记录")
