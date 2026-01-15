"""
快速检查签到数据
"""
from infrastructure.db.connection import execute_query
from datetime import date

# 查询所有玩家的签到情况
print("=" * 80)
print("所有玩家本月签到情况")
print("=" * 80)

today = date.today()
first_day = date(today.year, today.month, 1)

# 查询所有有签到记录的玩家
players = execute_query("""
    SELECT 
        p.user_id,
        COUNT(DISTINCT psr.signin_date) as total_days,
        p.signin_rewards_claimed
    FROM player p
    LEFT JOIN player_signin_records psr 
        ON p.user_id = psr.user_id 
        AND psr.signin_date >= %s 
        AND psr.signin_date <= %s
    GROUP BY p.user_id
    HAVING total_days > 0
    ORDER BY total_days DESC
    LIMIT 20
""", (first_day, today))

if players:
    for player in players:
        user_id = player['user_id']
        total_days = player['total_days']
        claimed = player['signin_rewards_claimed'] or '无'
        
        status_7 = "✅" if total_days >= 7 else "❌"
        status_15 = "✅" if total_days >= 15 else "❌"
        status_30 = "✅" if total_days >= 30 else "❌"
        
        print(f"用户ID: {user_id:6d} | 本月签到: {total_days:2d}天 | "
              f"7天{status_7} 15天{status_15} 30天{status_30} | 已领取: {claimed}")
else:
    print("没有找到任何签到记录")

print()
print("=" * 80)
print("请找到你的用户ID，然后运行: python diagnose_signin_reward.py")
print("=" * 80)
