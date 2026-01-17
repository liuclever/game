#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复脚本：将所有联盟创建者的role字段设置为1（盟主）
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_update, execute_query

def fix_alliance_leader_roles():
    """修复所有联盟创建者的role字段"""
    
    print("开始修复联盟创建者的role字段...")
    print()
    
    # 执行修复SQL
    sql = """
        UPDATE alliance_members am
        INNER JOIN alliances a ON am.alliance_id = a.id
        SET am.role = 1
        WHERE am.user_id = a.leader_id
          AND am.role != 1
    """
    
    affected = execute_update(sql, ())
    print(f"修复了 {affected} 条记录")
    print()
    
    # 显示修复结果
    print("修复后的结果：")
    print("-" * 80)
    
    sql_check = """
        SELECT 
            a.id AS alliance_id,
            a.name AS alliance_name,
            a.leader_id,
            am.user_id,
            am.role,
            CASE 
                WHEN am.user_id = a.leader_id AND am.role = 1 THEN '[OK] 正确'
                WHEN am.user_id = a.leader_id AND am.role != 1 THEN '[ERROR] 错误'
                ELSE '成员'
            END AS status
        FROM alliances a
        LEFT JOIN alliance_members am ON a.id = am.alliance_id AND am.user_id = a.leader_id
        ORDER BY a.id
    """
    
    rows = execute_query(sql_check, ())
    
    if not rows:
        print("没有找到联盟数据")
    else:
        print(f"{'联盟ID':<10} {'联盟名称':<30} {'创建者ID':<10} {'角色':<5} {'状态'}")
        print("-" * 80)
        for row in rows:
            if row['user_id']:
                role_name = {1: "盟主", 2: "副盟主", 3: "长老", 0: "盟众"}.get(row['role'], f"未知({row['role']})")
                print(f"{row['alliance_id']:<10} {row['alliance_name']:<30} {row['leader_id']:<10} {role_name:<5} {row['status']}")
            else:
                print(f"{row['alliance_id']:<10} {row['alliance_name']:<30} {row['leader_id']:<10} {'-':<5} 创建者不在成员表中")
    
    print()
    print("修复完成！")

if __name__ == "__main__":
    try:
        fix_alliance_leader_roles()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
