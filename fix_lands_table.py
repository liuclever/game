#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复lands表，确保所有land_id都存在
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_insert
from application.services.alliance_service import AllianceService

def fix_lands_table():
    """修复lands表，确保所有WAR_LANDS中的land_id都存在"""
    print("检查lands表...")
    
    # 获取当前lands表数据
    existing_lands = execute_query("SELECT id, name FROM lands WHERE id IN (1,2,3,4)")
    existing_ids = {r['id'] for r in existing_lands}
    
    print(f"当前lands表中有 {len(existing_ids)} 条记录: {existing_ids}")
    
    # 检查WAR_LANDS中定义的所有land_id
    for land_id, land_meta in AllianceService.WAR_LANDS.items():
        if land_id not in existing_ids:
            print(f"  缺失 land_id={land_id}: {land_meta['land_name']}")
            # 插入缺失的land记录
            try:
                execute_insert(
                    "INSERT INTO lands (id, name, land_type, daily_reward_copper) VALUES (%s, %s, %s, %s)",
                    (land_id, land_meta['land_name'], land_meta['land_type'], land_meta.get('daily_reward_copper', 0))
                )
                print(f"  [OK] 已创建 land_id={land_id}: {land_meta['land_name']}")
            except Exception as e:
                print(f"  [ERROR] 创建 land_id={land_id} 失败: {e}")
        else:
            # 检查名称是否匹配，如果不匹配则更新
            existing_land = next((r for r in existing_lands if r['id'] == land_id), None)
            if existing_land and existing_land['name'] != land_meta['land_name']:
                print(f"  更新 land_id={land_id} 的名称: {existing_land['name']} -> {land_meta['land_name']}")
                from infrastructure.db.connection import execute_update
                execute_update(
                    "UPDATE lands SET name = %s, land_type = %s, daily_reward_copper = %s WHERE id = %s",
                    (land_meta['land_name'], land_meta['land_type'], land_meta.get('daily_reward_copper', 0), land_id)
                )
                print(f"  [OK] 已更新 land_id={land_id}")
    
    # 再次检查
    final_lands = execute_query("SELECT id, name, land_type FROM lands WHERE id IN (1,2,3,4) ORDER BY id")
    print(f"\n修复后的lands表数据:")
    for land in final_lands:
        print(f"  id={land['id']}: {land['name']} ({land['land_type']})")
    
    print("\n[SUCCESS] lands表修复完成！")

if __name__ == "__main__":
    fix_lands_table()
