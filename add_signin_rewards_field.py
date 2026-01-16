"""
添加签到奖励已领取记录字段
"""
from infrastructure.db.connection import execute_update

print("正在添加 signin_rewards_claimed 字段...")

try:
    execute_update("""
        ALTER TABLE player 
        ADD COLUMN signin_rewards_claimed VARCHAR(50) DEFAULT '' 
        COMMENT '已领取的签到奖励，逗号分隔，例如: 7,15,30'
    """)
    print("✅ 字段添加成功！")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✅ 字段已存在，无需添加")
    else:
        print(f"❌ 添加失败: {e}")
