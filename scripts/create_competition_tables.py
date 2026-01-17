#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建联盟争霸赛数据库表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_update, execute_query

def create_tables():
    """创建争霸赛相关表"""
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', '040_alliance_competition_system.sql')
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割SQL语句
    statements = []
    current_statement = []
    in_comment = False
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 跳过注释
        if line.startswith('--'):
            continue
        if '/*' in line:
            in_comment = True
        if '*/' in line:
            in_comment = False
            continue
        if in_comment:
            continue
        
        current_statement.append(line)
        
        if line.endswith(';'):
            stmt = ' '.join(current_statement)
            if stmt.strip() and not stmt.strip().startswith('--'):
                statements.append(stmt)
            current_statement = []
    
    # 执行SQL语句
    for stmt in statements:
        try:
            execute_update(stmt)
            print(f"[OK] Executed: {stmt[:50]}...")
        except Exception as e:
            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                print(f"[SKIP] Already exists: {stmt[:50]}...")
            else:
                print(f"[ERROR] Error: {e}")
                print(f"  Statement: {stmt[:100]}...")
                raise

if __name__ == "__main__":
    print("Creating competition tables...")
    create_tables()
    print("Done!")
