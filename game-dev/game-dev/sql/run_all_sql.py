#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
游戏数据库初始化脚本
按顺序执行所有 SQL 文件
"""
import os
import pymysql
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'game_tower',
    'charset': 'utf8mb4',
}

def execute_sql_file(conn, file_path):
    """执行单个 SQL 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割多个 SQL 语句
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        with conn.cursor() as cursor:
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        # 忽略一些常见的错误（如表已存在、字段已存在等）
                        error_msg = str(e)
                        if any(keyword in error_msg.lower() for keyword in ['already exists', 'duplicate', 'exist']):
                            print(f"  [SKIP] 跳过（已存在）: {error_msg[:50]}")
                            continue
                        else:
                            print(f"  [ERROR] 错误: {error_msg[:100]}")
                            # 继续执行，不中断
            conn.commit()
        return True
    except Exception as e:
        print(f"  [ERROR] 执行失败: {str(e)[:100]}")
        return False

def main():
    print("=" * 50)
    print("   游戏数据库初始化脚本")
    print("=" * 50)
    print()
    
    # 连接数据库
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"[OK] 数据库连接成功: {DB_CONFIG['database']}")
        print()
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        return
    
    # 获取当前目录下的所有 SQL 文件
    sql_dir = Path(__file__).parent
    sql_files = sorted([f for f in sql_dir.glob("*.sql") if f.name != "run_all.sql"])
    
    print(f"找到 {len(sql_files)} 个 SQL 文件")
    print("开始执行SQL文件...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for sql_file in sql_files:
        print(f"正在执行: {sql_file.name}")
        if execute_sql_file(conn, sql_file):
            print(f"  [OK] 成功")
            success_count += 1
        else:
            print(f"  [FAIL] 失败（继续执行...）")
            fail_count += 1
        print()
    
    conn.close()
    
    print("=" * 50)
    print("   数据库初始化完成！")
    print("=" * 50)
    print()
    print(f"   成功: {success_count} 个文件")
    print(f"   失败: {fail_count} 个文件")
    print()
    print(f"   数据库名: {DB_CONFIG['database']}")
    print(f"   用户名: {DB_CONFIG['user']}")
    print(f"   密  码: {DB_CONFIG['password']}")
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()
