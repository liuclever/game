"""测试数据库触发器是否正确保护历史总贡献点"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update, get_connection

def test_trigger_protection():
    """测试触发器保护"""
    print("=" * 80)
    print("测试数据库触发器是否正确保护历史总贡献点")
    print("=" * 80)
    
    # 找一个测试用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 10 AND am.total_contribution > am.contribution
        LIMIT 1
    """
    rows = execute_query(sql)
    
    if not rows:
        print("[ERROR] 未找到合适的测试用户（需要 total_contribution > contribution）")
        return False
    
    user = rows[0]
    user_id = user['user_id']
    nickname = user['nickname'] or f"玩家{user_id}"
    before_contribution = user['contribution'] or 0
    before_total = user.get('total_contribution') or 0
    
    print(f"\n测试用户: {nickname} (ID: {user_id})")
    print(f"初始状态:")
    print(f"  现有贡献点: {before_contribution}")
    print(f"  历史总贡献点: {before_total}")
    
    # 测试1：尝试直接更新 total_contribution（应该被触发器阻止）
    print(f"\n[测试1] 尝试直接减少 total_contribution（应该被触发器阻止）")
    try:
        sql_test = """
            UPDATE alliance_members 
            SET total_contribution = total_contribution - 5
            WHERE user_id = %s
        """
        execute_update(sql_test, (user_id,))
        
        # 检查结果
        after_data = execute_query("SELECT contribution, total_contribution FROM alliance_members WHERE user_id = %s", (user_id,))[0]
        after_total = after_data.get('total_contribution')
        
        if after_total == before_total:
            print(f"  [OK] 触发器保护成功！total_contribution 没有被减少")
        else:
            print(f"  [ERROR] 触发器保护失败！total_contribution 从 {before_total} 变成了 {after_total}")
            # 恢复数据
            execute_update("UPDATE alliance_members SET total_contribution = %s WHERE user_id = %s", (before_total, user_id))
            return False
    except Exception as e:
        print(f"  [ERROR] 执行 SQL 时出错: {e}")
        return False
    
    # 测试2：使用 update_member_contribution 方法（减少贡献点）
    print(f"\n[测试2] 使用 update_member_contribution 方法减少贡献点")
    from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
    repo = MySQLAllianceRepo()
    
    # 记录更新前的数据
    before_data = execute_query("SELECT contribution, total_contribution FROM alliance_members WHERE user_id = %s", (user_id,))[0]
    before_contribution = before_data['contribution'] or 0
    before_total = before_data.get('total_contribution') or 0
    
    print(f"  更新前: 现有贡献点={before_contribution}, 历史总贡献点={before_total}")
    
    # 执行更新
    repo.update_member_contribution(user_id, -5)
    
    # 检查结果
    after_data = execute_query("SELECT contribution, total_contribution FROM alliance_members WHERE user_id = %s", (user_id,))[0]
    after_contribution = after_data['contribution'] or 0
    after_total = after_data.get('total_contribution') or 0
    
    print(f"  更新后: 现有贡献点={after_contribution}, 历史总贡献点={after_total}")
    
    expected_contribution = max(0, before_contribution - 5)
    expected_total = before_total
    
    if after_contribution != expected_contribution:
        print(f"  [ERROR] 现有贡献点错误: 期望 {expected_contribution}, 实际 {after_contribution}")
        return False
    else:
        print(f"  [OK] 现有贡献点正确")
    
    if after_total != expected_total:
        print(f"  [ERROR] 历史总贡献点被错误减少!")
        print(f"  [ERROR] 从 {before_total} 减少到 {after_total}")
        # 恢复数据
        repo.update_member_contribution(user_id, 5)
        return False
    else:
        print(f"  [OK] 历史总贡献点保持不变")
    
    # 恢复数据
    repo.update_member_contribution(user_id, 5)
    print(f"\n[恢复数据] 已恢复测试用户的贡献点")
    
    return True

if __name__ == "__main__":
    result = test_trigger_protection()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 测试通过！触发器正确保护了历史总贡献点")
    else:
        print("[FAILED] 测试失败！触发器没有正确保护历史总贡献点")
        print("\n建议:")
        print("1. 检查触发器是否正确创建")
        print("2. 运行 sql/044_protect_total_contribution.sql 重新创建触发器")
    print("=" * 80)
