"""
添加修行系统所需的数据库字段
"""
import sys
import os
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'game_tower',
    'charset': 'utf8mb4'
}

def execute_query(sql, params=()):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def execute_update(sql, params=()):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()
    finally:
        conn.close()

def check_column_exists(table, column):
    """检查列是否存在"""
    sql = """
        SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'game_tower' AND TABLE_NAME = %s AND COLUMN_NAME = %s
    """
    result = execute_query(sql, (table, column))
    return result[0]['cnt'] > 0 if result else False

def add_column_if_not_exists(table, column, definition):
    """如果列不存在则添加"""
    if check_column_exists(table, column):
        print(f"列 {column} 已存在，跳过")
        return False
    
    sql = f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
    try:
        execute_update(sql, ())
        print(f"成功添加列 {column}")
        return True
    except Exception as e:
        print(f"添加列 {column} 失败: {e}")
        return False

def main():
    print("检查并添加修行系统字段...")
    
    add_column_if_not_exists('player', 'cultivation_start_time', 'DATETIME DEFAULT NULL')
    add_column_if_not_exists('player', 'cultivation_area', 'VARCHAR(50) DEFAULT NULL')
    add_column_if_not_exists('player', 'cultivation_dungeon', 'VARCHAR(50) DEFAULT NULL')
    
    print("完成!")

if __name__ == "__main__":
    main()
