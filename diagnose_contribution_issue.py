"""诊断贡献点问题"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update

def check_specific_user(user_id):
    """检查特定用户的贡献点数据"""
    print(f"\n检查用户 {user_id} 的贡献点数据:")
    print("-" * 60)
    
    sql = """
        SELECT 
            am.user_id,
            am.contribution as 现有贡献点,
            am.total_contribution as 历史总贡献点,
            COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
            a.name as alliance_name
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LEFT JOIN alliances a ON am.alliance_id = a.id
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    
    if not rows:
        print(f"用户 {user_id} 不存在或不是联盟成员")
        return
    
    row = rows[0]
    contribution = row['现有贡献点'] or 0
    total = row.get('历史总贡献点') or 0
    
    print(f"用户: {row['nickname']}")
    print(f"联盟: {row['alliance_name']}")
    print(f"现有贡献点: {contribution}")
    print(f"历史总贡献点: {total}")
    
    if total < contribution:
        print(f"[ERROR] 历史总贡献点小于现有贡献点！数据异常！")
    elif total == contribution:
        print(f"[WARN] 历史总贡献点等于现有贡献点")
        print(f"  这可能是因为:")
        print(f"  1. 用户从未消耗过贡献点（正常情况）")
        print(f"  2. 数据被错误初始化（迁移脚本将 total_contribution 设置为 contribution）")
        print(f"  3. 有其他地方在更新 total_contribution")
    else:
        print(f"[OK] 历史总贡献点大于现有贡献点，说明用户消耗过贡献点")

def check_all_problematic_users():
    """检查所有有问题的用户"""
    print("\n" + "=" * 80)
    print("检查所有有问题的用户（历史总贡献点 <= 现有贡献点）")
    print("=" * 80)
    
    sql = """
        SELECT 
            am.user_id,
            am.contribution as 现有贡献点,
            am.total_contribution as 历史总贡献点,
            COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
            a.name as alliance_name,
            CASE 
                WHEN am.total_contribution IS NULL THEN 'NULL值'
                WHEN am.total_contribution < am.contribution THEN '小于现有贡献点'
                WHEN am.total_contribution = am.contribution THEN '等于现有贡献点'
                ELSE '正常'
            END as 问题类型
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LEFT JOIN alliances a ON am.alliance_id = a.id
        WHERE am.total_contribution IS NULL 
           OR am.total_contribution <= am.contribution
        ORDER BY am.user_id
        LIMIT 50
    """
    
    rows = execute_query(sql)
    
    if not rows:
        print("没有找到有问题的用户")
        return
    
    print(f"{'用户ID':<8} {'昵称':<15} {'联盟':<15} {'现有贡献':<10} {'历史总贡献':<12} {'问题':<20}")
    print("-" * 90)
    
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        alliance = row['alliance_name'] or "未知"
        contribution = row['现有贡献点'] or 0
        total = row.get('历史总贡献点') or 0
        problem = row['问题类型']
        
        print(f"{user_id:<8} {nickname:<15} {alliance:<15} {contribution:<10} {total:<12} {problem:<20}")
    
    print(f"\n总计: {len(rows)} 个用户的历史总贡献点 <= 现有贡献点")
    print("\n说明:")
    print("  - 如果历史总贡献点 = 现有贡献点，可能是用户从未消耗过贡献点（正常）")
    print("  - 如果历史总贡献点 < 现有贡献点，说明数据异常，需要修复")
    print("  - 如果历史总贡献点为 NULL，说明数据未初始化，需要修复")

if __name__ == "__main__":
    # 检查所有有问题的用户
    check_all_problematic_users()
    
    # 可以指定用户ID检查
    # check_specific_user(4053)
