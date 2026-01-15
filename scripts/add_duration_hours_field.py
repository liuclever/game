#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加联盟修行时长字段的迁移脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_update, execute_query

def main():
    try:
        # 检查字段是否已存在
        rows = execute_query("SHOW COLUMNS FROM alliance_training_rooms LIKE 'duration_hours'")
        if rows:
            print("字段 duration_hours 已存在，跳过添加")
            return
        
        # 添加字段
        print("正在添加 duration_hours 字段...")
        execute_update("""
            ALTER TABLE alliance_training_rooms 
            ADD COLUMN duration_hours INT NOT NULL DEFAULT 2 COMMENT '修行时长（小时），默认2小时' 
            AFTER max_participants
        """)
        
        # 为现有数据设置默认值
        print("正在更新现有数据...")
        execute_update("UPDATE alliance_training_rooms SET duration_hours = 2 WHERE duration_hours IS NULL OR duration_hours = 0")
        
        print("字段添加成功！")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
