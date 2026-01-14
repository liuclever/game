"""
直接测试API（不通过HTTP）
"""
from infrastructure.db.connection import execute_query
from datetime import date

user_id = 4053  # 修改为你的用户ID

print("=" * 60)
print(f"测试用户 {user_id} 的签到奖励状态")
print("=" * 60)

# 获取已领取记录
player = execute_query(
    "SELECT signin_rewards_claimed FROM player WHERE user_id = %s",
    (user_id,)
)

if not player:
    print("❌ 找不到玩家")
    exit(1)

claimed_str = player[0]['signin_rewards_claimed'] or ''
print(f"已领取记录: {claimed_str if claimed_str else '无'}")

# 计算本月累积签到天数
today = date.today()
first_day = date(today.year, today.month, 1)
records = execute_query(
    """SELECT COUNT(*) as count FROM player_signin_records 
       WHERE user_id = %s AND signin_date >= %s AND signin_date <= %s""",
    (user_id, first_day, today)
)

total_signin_days = records[0]['count'] if records else 0
print(f"本月累积签到: {total_signin_days} 天")
print()

# 解析已领取的奖励
claimed_list = [int(x) for x in claimed_str.split(',') if x.strip()]

# 检查各个奖励状态
for days in [7, 15, 30]:
    is_claimed = days in claimed_list
    can_claim = total_signin_days >= days and not is_claimed
    
    print(f"{days}天礼包:")
    print(f"  - 需要天数: {days}")
    print(f"  - 当前天数: {total_signin_days}")
    print(f"  - 已领取: {'是' if is_claimed else '否'}")
    print(f"  - 可领取: {'是' if can_claim else '否'}")
    print()

print("=" * 60)
if total_signin_days >= 7 and 7 not in claimed_list:
    print("✅ 你应该可以领取7天礼包了！")
    print("   如果前端还显示'未满足'，请确保：")
    print("   1. 后端服务已重启")
    print("   2. 浏览器已刷新（清除缓存）")
    print("   3. 检查浏览器控制台是否有错误")
else:
    print("⏳ 还不能领取7天礼包")
print("=" * 60)
