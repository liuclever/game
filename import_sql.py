"""
导入SQL文件到MySQL数据库
"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4',
}

def import_sql_file(sql_file_path):
    """导入SQL文件"""
    # 先连接MySQL服务器（不指定数据库）
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # 创建数据库（如果不存在）
            print("创建数据库 game_tower...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS game_tower CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            cursor.execute("USE game_tower")
            
            # 读取SQL文件
            print(f"读取SQL文件: {sql_file_path}")
            with open(sql_file_path, 'r', encoding='utf8') as f:
                sql_content = f.read()
            
            # 分割SQL语句（按分号分割）
            sql_statements = sql_content.split(';')
            
            # 执行每条SQL语句
            total = len(sql_statements)
            for i, statement in enumerate(sql_statements, 1):
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        if i % 10 == 0:
                            print(f"进度: {i}/{total}")
                    except Exception as e:
                        print(f"执行SQL出错: {str(e)[:100]}")
                        print(f"SQL: {statement[:100]}...")
            
            conn.commit()
            print("✓ SQL文件导入成功！")
            
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    import_sql_file('game_tower_2026_1_11.sql')
