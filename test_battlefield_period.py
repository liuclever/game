"""测试战场期数计算"""
from datetime import date

# 期数计算逻辑
reference_date = date(2024, 1, 1)
today = date.today()
period = (today - reference_date).days + 1

print(f"参考日期: {reference_date}")
print(f"今天日期: {today}")
print(f"当前期数: {period}")
print()

# 测试几个特定日期
test_dates = [
    date(2024, 1, 1),   # 第1期
    date(2024, 1, 24),  # 第24期
    date(2024, 1, 25),  # 第25期
    date(2026, 2, 1),   # 今天
]

print("日期期数对照表:")
print("-" * 40)
for test_date in test_dates:
    test_period = (test_date - reference_date).days + 1
    print(f"{test_date} => 第{test_period}期")
