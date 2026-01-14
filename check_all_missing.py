"""全面检查数据库缺失的表和字段"""
from infrastructure.db.connection import execute_query

print("=" * 60)
print("数据库结构检查报告")
print("=" * 60)

# 1. 检查 player 表缺失的字段
print("\n【1】player 表字段检查")
print("-" * 60)
player_cols = execute_query("DESCRIBE player")
player_fields = {c['Field'] for c in player_cols}

# 后端代码中使用的字段
expected_fields = [
    'signin_rewards_claimed',  # 签到累计奖励已领取记录
]

missing_fields = []
for field in expected_fields:
    if field not in player_fields:
        missing_fields.append(field)
        print(f"❌ 缺失字段: {field}")
    else:
        print(f"✅ 存在字段: {field}")

# 2. 检查缺失的表
print("\n【2】数据库表检查")
print("-" * 60)
all_tables = execute_query("SHOW TABLES")
table_names = {list(t.values())[0] for t in all_tables}

expected_tables = [
    'player_signin_records',  # 签到记录表
]

missing_tables = []
for table in expected_tables:
    if table not in table_names:
        missing_tables.append(table)
        print(f"❌ 缺失表: {table}")
    else:
        print(f"✅ 存在表: {table}")

# 3. 检查 arena 相关表
print("\n【3】擂台相关表检查")
print("-" * 60)
arena_tables = ['arena', 'arena_battle_log', 'arena_daily_challenge', 'arena_stats', 'arena_streak', 'arena_streak_history']
for table in arena_tables:
    if table in table_names:
        print(f"✅ 存在表: {table}")
    else:
        print(f"❌ 缺失表: {table}")

# 4. 总结
print("\n" + "=" * 60)
print("总结")
print("=" * 60)
if missing_fields:
    print(f"\n缺失的字段 ({len(missing_fields)}个):")
    for field in missing_fields:
        print(f"  - {field}")
else:
    print("\n✅ 所有字段都存在")

if missing_tables:
    print(f"\n缺失的表 ({len(missing_tables)}个):")
    for table in missing_tables:
        print(f"  - {table}")
else:
    print("\n✅ 所有表都存在")

if missing_fields or missing_tables:
    print("\n⚠️  发现数据库结构与后端代码不一致！")
else:
    print("\n✅ 数据库结构与后端代码一致")
