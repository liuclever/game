"""测试补签功能"""
import sys
from pathlib import Path
from datetime import date, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query, execute_update

print("=" * 60)
print("测试补签功能")
print("=" * 60)
print()

# 测试玩家
test_user_id = 4053
today = date.today()
first_day = date(today.year, today.month, 1)

print(f"测试玩家ID: {test_user_id}")
print(f"当前日期: {today}")
print(f"本月第一天: {first_day}")
print()

# 1. 清空测试数据
print("【步骤1】清空测试数据")
print("-" * 60)
execute_update(
    "DELETE FROM player_signin_records WHERE user_id = %s AND signin_date >= %s",
    (test_user_id, first_day)
)
print("✅ 已清空本月签到记录")
print()

# 2. 模拟签到几天（跳过一些日期）
print("【步骤2】模拟签到（跳过一些日期）")
print("-" * 60)
signed_days = [1, 2, 3, 5, 7, 10]  # 跳过了4, 6, 8, 9号
for day in signed_days:
    if day < today.day:  # 只签到今天之前的日期
        signin_date = date(today.year, today.month, day)
        execute_update(
            """INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
               VALUES (%s, %s, 0, 1000)
               ON DUPLICATE KEY UPDATE signin_date = signin_date""",
            (test_user_id, signin_date)
        )
        print(f"  ✓ 已签到: {today.month}月{day}日")
print()

# 3. 查询已签到的日期
print("【步骤3】查询已签到的日期")
print("-" * 60)
records = execute_query(
    """SELECT DAY(signin_date) as day, is_makeup FROM player_signin_records 
       WHERE user_id = %s AND signin_date >= %s AND signin_date < %s
       ORDER BY signin_date""",
    (test_user_id, first_day, today)
)

signed_days_set = set(r['day'] for r in records)
print(f"已签到的日期: {sorted(list(signed_days_set))}")
print()

# 4. 计算未签到的日期
print("【步骤4】计算未签到的日期")
print("-" * 60)
missed_days = []
current_day = first_day
while current_day < today:
    if current_day.day not in signed_days_set:
        missed_days.append(current_day.day)
    current_day += timedelta(days=1)

print(f"未签到的日期: {missed_days}")
print(f"可补签天数: {len(missed_days)}")
print()

# 5. 模拟补签
print("【步骤5】模拟补签")
print("-" * 60)

# 先给玩家添加补签卡
execute_update(
    """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
       VALUES (%s, 6027, 10, 0)
       ON DUPLICATE KEY UPDATE quantity = 10""",
    (test_user_id,)
)
print("✅ 已添加10张补签卡")

# 补签第一个未签到的日期
if missed_days:
    makeup_day = missed_days[0]
    makeup_date = date(today.year, today.month, makeup_day)
    
    print(f"\n补签日期: {today.month}月{makeup_day}日")
    
    # 检查是否已签到
    existing = execute_query(
        "SELECT id FROM player_signin_records WHERE user_id = %s AND signin_date = %s",
        (test_user_id, makeup_date)
    )
    
    if existing:
        print("❌ 该日期已签到")
    else:
        # 扣除补签卡
        execute_update(
            "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = 6027",
            (test_user_id,)
        )
        
        # 记录补签
        execute_update(
            """INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
               VALUES (%s, %s, 1, 1000)""",
            (test_user_id, makeup_date)
        )
        
        print(f"✅ 补签成功！")
print()

# 6. 再次查询签到情况
print("【步骤6】补签后的签到情况")
print("-" * 60)
records = execute_query(
    """SELECT DAY(signin_date) as day, is_makeup FROM player_signin_records 
       WHERE user_id = %s AND signin_date >= %s AND signin_date < %s
       ORDER BY signin_date""",
    (test_user_id, first_day, today)
)

print("签到日历:")
for r in records:
    day = r['day']
    is_makeup = r['is_makeup']
    status = "补签" if is_makeup else "正常"
    print(f"  {today.month}月{day}日 - {status}")

signed_days_set = set(r['day'] for r in records)
missed_days = []
current_day = first_day
while current_day < today:
    if current_day.day not in signed_days_set:
        missed_days.append(current_day.day)
    current_day += timedelta(days=1)

print(f"\n剩余未签到的日期: {missed_days}")
print()

# 7. 检查补签卡数量
cards = execute_query(
    "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = 6027",
    (test_user_id,)
)
current_cards = cards[0]['quantity'] if cards else 0
print(f"剩余补签卡: {current_cards}张")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
