#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加火能原石领取日期字段到 player 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query, execute_update

def add_fire_ore_claim_date_field():
    """添加 last_fire_ore_claim_date 字段到 player 表"""
    try:
        # 检查字段是否已存在
        rows = execute_query(
            "SELECT COUNT(*) as cnt FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME = 'player' "
            "AND COLUMN_NAME = 'last_fire_ore_claim_date'"
        )
        
        if rows and rows[0].get('cnt', 0) > 0:
            print("字段 last_fire_ore_claim_date 已存在，跳过添加")
            return
        
        # 添加字段
        sql = """
            ALTER TABLE player 
            ADD COLUMN last_fire_ore_claim_date DATE DEFAULT NULL 
            COMMENT '最后领取火能原石日期'
        """
        execute_update(sql)
        print("Successfully added field last_fire_ore_claim_date to player table")
        
    except Exception as e:
        error_msg = str(e)
        if 'Duplicate column' in error_msg or 'already exists' in error_msg.lower():
            print("Field already exists, skipping")
        else:
            print(f"Failed to add field: {error_msg}")
            raise

if __name__ == "__main__":
    add_fire_ore_claim_date_field()
