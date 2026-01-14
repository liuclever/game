"""迁移现有签到数据到新的签到记录表"""
import sys
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query, execute_update

print("=" * 60)
print("迁移签到数据")
print("=" * 60)
print()

# 查询所有有签到记录的玩家
players = execute_query(
    "SELECT user_id, last_signin_date FROM player WHERE last_signin_date IS NOT NULL"
)

print(f"找到 {len(players)} 个有签到记录的玩家")
print()

migrated_count = 0
skipped_count = 0

for player in players:
    user_id = player['user_id']
    last_signin = player['last_signin_date']
    
    # 处理可能的 datetime 类型
    if hasattr(last_signin, 'date'):
        last_signin = last_signin.date()
    
    # 检查是否已经迁移
    existing = execute_query(
        "SELECT id FROM player_signin_records WHERE user_id = %s AND signin_date = %s",
        (user_id, last_signin)
    )
    
    if existing:
        skipped_count += 1
        continue
    
    # 插入签到记录
    try:
        execute_update(
            """INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
               VALUES (%s, %s, 0, 1000)""",
            (user_id, last_signin)
        )
        migrated_count += 1
        print(f"✓ 迁移玩家 {user_id} 的签到记录: {last_signin}")
    except Exception as e:
        print(f"✗ 迁移玩家 {user_id} 失败: {e}")

print()
print("=" * 60)
print(f"迁移完成")
print(f"  成功迁移: {migrated_count} 条")
print(f"  跳过（已存在）: {skipped_count} 条")
print("=" * 60)
