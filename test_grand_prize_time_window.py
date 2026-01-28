"""测试连胜大奖时间窗口功能

测试场景：
1. 查看当前时间和昨日连胜王
2. 测试大奖领取逻辑
3. 验证时间窗口限制（00:00-08:00）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from datetime import datetime, timedelta, date


def test_grand_prize_logic():
    """测试连胜大奖逻辑"""
    
    print("=" * 60)
    print("连胜大奖时间窗口测试")
    print("=" * 60)
    
    # 获取当前时间
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    current_hour = now.hour
    
    print(f"\n【当前时间】")
    print(f"  日期: {today}")
    print(f"  时间: {now.strftime('%H:%M:%S')}")
    print(f"  小时: {current_hour}")
    print(f"  昨日: {yesterday}")
    
    # 检查是否在领取时间窗口内
    in_time_window = current_hour < 8
    print(f"\n【时间窗口检查】")
    print(f"  领取时间窗口: 00:00-08:00")
    print(f"  当前是否在窗口内: {'是' if in_time_window else '否'}")
    if not in_time_window:
        print(f"  ⚠️  当前时间 {current_hour}:00 已超过08:00，无法领取大奖")
    else:
        print(f"  ✅ 当前时间 {current_hour}:00 在窗口内，可以领取大奖")
    
    # 查看今日连胜王
    print(f"\n【今日连胜王】({today})")
    today_king = execute_query("""
        SELECT p.user_id, p.nickname, a.max_streak_today, a.claimed_grand_prize
        FROM arena_streak a
        JOIN player p ON a.user_id = p.user_id
        WHERE a.record_date = %s
        ORDER BY a.max_streak_today DESC
        LIMIT 1
    """, (today,))
    
    if today_king:
        king = today_king[0]
        print(f"  玩家: {king['nickname']} (ID: {king['user_id']})")
        print(f"  连胜次数: {king['max_streak_today']}")
        print(f"  已领取大奖: {'是' if king.get('claimed_grand_prize') else '否'}")
    else:
        print(f"  暂无连胜记录")
    
    # 查看昨日连胜王
    print(f"\n【昨日连胜王】({yesterday})")
    yesterday_king = execute_query("""
        SELECT p.user_id, p.nickname, a.max_streak_today, a.claimed_grand_prize
        FROM arena_streak a
        JOIN player p ON a.user_id = p.user_id
        WHERE a.record_date = %s
        ORDER BY a.max_streak_today DESC
        LIMIT 1
    """, (yesterday,))
    
    if yesterday_king:
        king = yesterday_king[0]
        print(f"  玩家: {king['nickname']} (ID: {king['user_id']})")
        print(f"  连胜次数: {king['max_streak_today']}")
        print(f"  已领取大奖: {'是' if king.get('claimed_grand_prize') else '否'}")
        
        # 判断是否可以领取
        can_claim = not king.get('claimed_grand_prize') and in_time_window
        print(f"\n  【大奖领取状态】")
        if can_claim:
            print(f"  ✅ 可以领取大奖")
            print(f"     - 昨日连胜王: 是")
            print(f"     - 未领取: 是")
            print(f"     - 在时间窗口内: 是")
        else:
            print(f"  ❌ 无法领取大奖")
            if king.get('claimed_grand_prize'):
                print(f"     - 原因: 已领取过")
            elif not in_time_window:
                print(f"     - 原因: 超过领取时间（08:00）")
    else:
        print(f"  暂无连胜记录")
    
    # 查看所有玩家的连胜记录
    print(f"\n【所有玩家连胜记录】")
    all_records = execute_query("""
        SELECT p.user_id, p.nickname, a.record_date, a.max_streak_today, a.claimed_grand_prize
        FROM arena_streak a
        JOIN player p ON a.user_id = p.user_id
        WHERE a.record_date >= %s
        ORDER BY a.record_date DESC, a.max_streak_today DESC
        LIMIT 10
    """, (yesterday,))
    
    if all_records:
        for record in all_records:
            record_date = record['record_date']
            is_today = record_date == today
            is_yesterday = record_date == yesterday
            date_label = "今日" if is_today else ("昨日" if is_yesterday else str(record_date))
            
            print(f"  {date_label} - {record['nickname']} (ID: {record['user_id']})")
            print(f"    连胜: {record['max_streak_today']}次")
            print(f"    已领取大奖: {'是' if record.get('claimed_grand_prize') else '否'}")
    else:
        print(f"  暂无记录")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n【使用说明】")
    print("1. 大奖领取时间：每天00:00-08:00")
    print("2. 领取资格：前一天的全服连胜王")
    print("3. 过期机制：超过08:00后无法领取")
    print("4. 例如：1月12日的连胜王，可以在1月13日00:00-08:00领取大奖")


def simulate_time_window():
    """模拟不同时间的领取状态"""
    print("\n" + "=" * 60)
    print("模拟不同时间的领取状态")
    print("=" * 60)
    
    test_hours = [0, 1, 5, 7, 8, 9, 12, 20, 23]
    
    for hour in test_hours:
        in_window = hour < 8
        status = "✅ 可领取" if in_window else "❌ 已过期"
        print(f"  {hour:02d}:00 - {status}")


if __name__ == "__main__":
    test_grand_prize_logic()
    simulate_time_window()
