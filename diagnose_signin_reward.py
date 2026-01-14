"""
诊断签到奖励问题
"""
from infrastructure.db.connection import execute_query

# 获取你的用户信息
user_id_input = input("请输入你的user_id (例如: 4053): ").strip()

try:
    user_id = int(user_id_input)
except ValueError:
    print("❌ 请输入有效的数字ID")
    exit(1)

print(f"✅ 用户ID: {user_id}")
print()

# 查询签到信息
player = execute_query(
    """SELECT consecutive_signin_days, signin_rewards_claimed, last_signin_date 
       FROM player WHERE user_id = %s""",
    (user_id,)
)

if not player:
    print("❌ 找不到玩家数据")
    exit(1)

player_data = player[0]
consecutive_days = int(player_data['consecutive_signin_days'] or 0)
claimed_str = player_data['signin_rewards_claimed'] or ''
last_signin = player_data['last_signin_date']

# 计算本月累积签到天数
from datetime import date
today = date.today()
first_day = date(today.year, today.month, 1)

records = execute_query(
    """SELECT COUNT(*) as count FROM player_signin_records 
       WHERE user_id = %s AND signin_date >= %s AND signin_date <= %s""",
    (user_id, first_day, today)
)

total_signin_days = records[0]['count'] if records else 0

print("=" * 60)
print("签到信息")
print("=" * 60)
print(f"本月累积签到天数: {total_signin_days} 天")
print(f"连续签到天数: {consecutive_days} 天 (仅供参考)")
print(f"最后签到日期: {last_signin}")
print(f"已领取奖励: {claimed_str if claimed_str else '无'}")
print()

# 解析已领取的奖励
claimed_list = [int(x) for x in claimed_str.split(',') if x.strip()]

# 检查各个奖励状态
print("=" * 60)
print("奖励状态")
print("=" * 60)

for days in [7, 15, 30]:
    is_claimed = days in claimed_list
    can_claim = total_signin_days >= days and not is_claimed
    
    status = "✅ 已领取" if is_claimed else ("🎁 可领取" if can_claim else "❌ 未满足")
    print(f"{days}天礼包: {status} (需要{days}天，当前本月累积{total_signin_days}天)")

print()

# 查询签到记录
print("=" * 60)
print("本月签到记录")
print("=" * 60)

from datetime import date
today = date.today()
first_day = date(today.year, today.month, 1)

records = execute_query(
    """SELECT signin_date, is_makeup FROM player_signin_records 
       WHERE user_id = %s AND signin_date >= %s
       ORDER BY signin_date""",
    (user_id, first_day)
)

if records:
    print(f"本月已签到 {len(records)} 天:")
    for record in records:
        makeup_tag = " (补签)" if record['is_makeup'] else ""
        print(f"  - {record['signin_date']}{makeup_tag}")
else:
    print("本月还没有签到记录")

print()
print("=" * 60)
print("诊断建议")
print("=" * 60)

if total_signin_days >= 7 and 7 not in claimed_list:
    print("✅ 你可以领取7天礼包了！")
if total_signin_days >= 15 and 15 not in claimed_list:
    print("✅ 你可以领取15天礼包了！")
if total_signin_days >= 30 and 30 not in claimed_list:
    print("✅ 你可以领取30天礼包了！")

if total_signin_days < 7:
    print(f"⏳ 还需要签到 {7 - total_signin_days} 天才能领取7天礼包")
