import sys
import os

sys.path.append(os.getcwd())

from infrastructure.db.connection import execute_query

def verify():
    try:
        print("检查 player 表结构...")
        result = execute_query("DESCRIBE player;")
        columns = [row['Field'] for row in result]
        if 'dice' in columns:
            print("验证成功: 'dice' 字段已存在。")
        else:
            print("验证失败: 'dice' 字段不存在。")
            
        print("检查玩家骰子数据...")
        data = execute_query("SELECT user_id, dice FROM player LIMIT 5;")
        for row in data:
            print(f"User ID: {row['user_id']}, Dice: {row['dice']}")
            
    except Exception as e:
        print(f"验证过程中出错: {e}")

if __name__ == "__main__":
    verify()
