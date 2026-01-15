#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：检查联盟盟主角色是否正确设置
检查 test_war_20001 到 test_war_20005 这些账号的联盟角色
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo

def test_alliance_leader_roles():
    """检查测试账号的联盟角色"""
    
    test_user_ids = [20001, 20002, 20003, 20004, 20005]
    alliance_repo = MySQLAllianceRepo()
    
    print("=" * 60)
    print("检查测试账号的联盟角色")
    print("=" * 60)
    print()
    
    for user_id in test_user_ids:
        print(f"检查用户 ID: {user_id}")
        
        # 1. 检查用户是否在联盟成员表中
        member = alliance_repo.get_member(user_id)
        if not member:
            print(f"  [ERROR] 用户 {user_id} 不在任何联盟中")
            print()
            continue
        
        # 2. 检查联盟信息
        alliance = alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            print(f"  [ERROR] 用户 {user_id} 的联盟不存在 (alliance_id={member.alliance_id})")
            print()
            continue
        
        # 3. 检查角色
        role_name = {1: "盟主", 2: "副盟主", 3: "长老", 0: "盟众"}.get(member.role, f"未知({member.role})")
        
        print(f"  联盟ID: {alliance.id}")
        print(f"  联盟名称: {alliance.name}")
        print(f"  联盟创建者 (leader_id): {alliance.leader_id}")
        print(f"  用户ID: {user_id}")
        print(f"  当前角色 (role): {member.role} ({role_name})")
        
        # 4. 判断是否正确
        if alliance.leader_id == user_id:
            if member.role == 1:
                print(f"  [OK] 正确：用户是联盟创建者且role=1（盟主）")
            else:
                print(f"  [ERROR] 错误：用户是联盟创建者但role={member.role}，应该是1（盟主）")
        else:
            print(f"  [WARN] 用户不是联盟创建者（创建者是 {alliance.leader_id}）")
        
        print()
    
    # 5. 检查所有联盟的创建者角色
    print("=" * 60)
    print("检查所有联盟的创建者角色")
    print("=" * 60)
    print()
    
    sql = """
        SELECT 
            a.id AS alliance_id,
            a.name AS alliance_name,
            a.leader_id,
            am.user_id,
            am.role,
            CASE 
                WHEN am.user_id = a.leader_id AND am.role = 1 THEN '[OK] 正确'
                WHEN am.user_id = a.leader_id AND am.role != 1 THEN '[ERROR] 错误（应该是1）'
                ELSE '成员'
            END AS status
        FROM alliances a
        LEFT JOIN alliance_members am ON a.id = am.alliance_id AND am.user_id = a.leader_id
        ORDER BY a.id
    """
    
    rows = execute_query(sql, ())
    
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

if __name__ == "__main__":
    try:
        test_alliance_leader_roles()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
