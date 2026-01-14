"""检查签到相关字段和表"""
from infrastructure.db.connection import execute_query

# 检查 player 表中是否有 signin_rewards_claimed 字段
print("=== 检查 player 表字段 ===")
cols = execute_query("DESCRIBE player")
signin_fields = [c for c in cols if 'signin' in c['Field'].lower()]
print(f"签到相关字段: {[c['Field'] for c in signin_fields]}")

# 检查是否有 signin_rewards_claimed 字段
has_rewards_field = any(c['Field'] == 'signin_rewards_claimed' for c in cols)
print(f"signin_rewards_claimed 字段存在: {has_rewards_field}")

# 检查 player_signin_records 表是否存在
print("\n=== 检查 player_signin_records 表 ===")
tables = execute_query("SHOW TABLES LIKE 'player_signin_records'")
if tables:
    print("player_signin_records 表存在")
    # 查看表结构
    structure = execute_query("DESCRIBE player_signin_records")
    for col in structure:
        print(f"  {col['Field']:30} {col['Type']:20} NULL:{col['Null']:3}")
else:
    print("player_signin_records 表不存在")
