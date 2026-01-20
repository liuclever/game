#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建联盟退出记录表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_update

def create_table():
    """创建 alliance_quit_records 表"""
    sql = """
    CREATE TABLE IF NOT EXISTS alliance_quit_records (
        user_id INT NOT NULL PRIMARY KEY,
        quit_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '退出联盟的时间',
        FOREIGN KEY (user_id) REFERENCES player(user_id) ON DELETE CASCADE,
        INDEX idx_quit_at (quit_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记录玩家退出联盟的时间，用于48小时加入限制';
    """
    
    try:
        execute_update(sql)
        print("[OK] Successfully created alliance_quit_records table")
    except Exception as e:
        error_str = str(e).lower()
        if 'already exists' in error_str or 'duplicate' in error_str or 'table' in error_str and 'exists' in error_str:
            print("[SKIP] alliance_quit_records table already exists")
        else:
            print(f"[ERROR] Failed to create table: {e}")
            raise

if __name__ == "__main__":
    print("Creating alliance_quit_records table...")
    create_table()
    print("Done!")
