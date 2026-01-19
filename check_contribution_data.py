"""检查贡献点数据，找出问题"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query

def check_all_members():
    """检查所有成员的贡献点数据"""
    print("=" * 80)
    print("检查所有联盟成员的贡献点数据")
    print("=" * 80)
    
    sql = """
        SELECT 
            am.user_id,
            COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
            a.name as alliance_name,
            am.contribution as 现有贡献点,
            am.total_contribution as 历史总贡献点,
            CASE 
                WHEN am.total_contribution IS NULL THEN '[ERROR] 历史总贡献点为NULL'
                WHEN am.total_contribution < am.contribution THEN '[ERROR] 历史总贡献点小于现有贡献点'
                WHEN am.total_contribution = am.contribution THEN '[WARN] 历史总贡献点等于现有贡献点（可能从未消耗过）'
                ELSE '[OK] 正常'
            END as 状态
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LEFT JOIN alliances a ON am.alliance_id = a.id
        ORDER BY am.alliance_id, am.user_id
        LIMIT 30
    """
    
    rows = execute_query(sql)
    
    if not rows:
        print("没有找到联盟成员")
        return
    
    print(f"{'用户ID':<8} {'昵称':<15} {'联盟':<15} {'现有贡献':<10} {'历史总贡献':<12} {'状态':<50}")
    print("-" * 110)
    
    error_count = 0
    warn_count = 0
    
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        alliance = row['alliance_name'] or "未知"
        contribution = row['现有贡献点'] or 0
        total = row['历史总贡献点']
        status = row['状态']
        
        if '[ERROR]' in status:
            error_count += 1
        elif '[WARN]' in status:
            warn_count += 1
        
        print(f"{user_id:<8} {nickname:<15} {alliance:<15} {contribution:<10} {total:<12} {status:<50}")
    
    print("-" * 110)
    print(f"总计: {len(rows)} 个成员")
    print(f"  正常: {len(rows) - error_count - warn_count} 个")
    print(f"  警告: {warn_count} 个（历史总贡献点等于现有贡献点）")
    print(f"  错误: {error_count} 个（历史总贡献点小于现有贡献点或为NULL）")
    
    if error_count > 0:
        print("\n[ERROR] 发现数据异常，需要修复！")
        print("请执行修复脚本: python run_migration.py sql/043_fix_total_contribution.sql")

if __name__ == "__main__":
    check_all_members()
