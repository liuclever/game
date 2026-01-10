import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.getcwd())

from infrastructure.db.connection import execute_update

def migrate():
    try:
        print("开始添加 dice 字段...")
        sql = "ALTER TABLE player ADD COLUMN dice INT NOT NULL DEFAULT 0 COMMENT '骰子数量' AFTER yuanbao;"
        execute_update(sql)
        print("dice 字段添加成功。")
        
        print("设置初始骰子数量...")
        sql_update = "UPDATE player SET dice = 10 WHERE dice = 0;"
        execute_update(sql_update)
        print("初始骰子设置成功。")
    except Exception as e:
        print(f"迁移失败: {e}")

if __name__ == "__main__":
    migrate()
