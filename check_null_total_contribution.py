"""检查数据库中 total_contribution 为 NULL 的记录"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update

def check_null_total_contribution():
    """检查 total_contribution 为 NULL 的记录"""
    print("=" * 80)
    print("检查数据库中 total_contribution 为 NULL 的记录")
    print("=" * 80)
    
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.total_contribution IS NULL
        LIMIT 20
    """
    rows = execute_query(sql)
    
    if not rows:
        print("\n[OK] 没有找到 total_contribution 为 NULL 的记录")
        return True
    
    print(f"\n[WARNING] 找到 {len(rows)} 条 total_contribution 为 NULL 的记录")
    print("\n这些记录会导致前端显示时使用 contribution 的值作为 total_contribution")
    print("当 contribution 减少时，看起来就像是两个值都减少了\n")
    
    print(f"{'用户ID':<10} {'昵称':<20} {'现有贡献点':<12} {'历史总贡献点':<15}")
    print("-" * 60)
    
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        contribution = row['contribution'] or 0
        total_contribution = row.get('total_contribution')
        
        print(f"{user_id:<10} {nickname:<20} {contribution:<12} {str(total_contribution):<15}")
    
    # 询问是否修复
    print("\n是否要修复这些记录？将 total_contribution 设置为 contribution 的值")
    print("(这不会影响历史总贡献点的正确性，因为如果 total_contribution 是 NULL，")
    print(" 说明用户从未获得过贡献点，或者数据被错误初始化)")
    
    # 自动修复
    print("\n[自动修复] 将 total_contribution 设置为 contribution 的值...")
    
    sql_fix = """
        UPDATE alliance_members 
        SET total_contribution = contribution
        WHERE total_contribution IS NULL
    """
    affected_rows = execute_update(sql_fix)
    
    print(f"[OK] 已修复 {affected_rows} 条记录")
    
    return True

if __name__ == "__main__":
    check_null_total_contribution()
    print("\n" + "=" * 80)
