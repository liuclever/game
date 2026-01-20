"""测试贡献点问题：检查领取火能原石后两个数据是否都减少"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo

def get_member_data(user_id):
    """获取成员数据（直接从数据库）"""
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    if not rows:
        return None
    return rows[0]

def get_member_from_repo(user_id):
    """通过仓储获取成员数据"""
    repo = MySQLAllianceRepo()
    return repo.get_member(user_id)

def test_contribution_issue():
    """测试贡献点问题"""
    print("=" * 80)
    print("测试：领取火能原石后贡献点的变化")
    print("=" * 80)
    
    # 找一个有足够贡献点的用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 5
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到有足够贡献点的用户")
        return False
    
    user = rows[0]
    user_id = user['user_id']
    
    print(f"\n测试用户: {user['nickname']} (ID: {user_id})")
    
    # 确保 total_contribution 有值（如果为 NULL，设置为 contribution 的值）
    if user.get('total_contribution') is None:
        print("\n[警告] total_contribution 为 NULL，设置为 contribution 的值")
        sql_update = """
            UPDATE alliance_members 
            SET total_contribution = contribution
            WHERE user_id = %s AND total_contribution IS NULL
        """
        execute_update(sql_update, (user_id,))
        # 重新获取数据
        rows = execute_query(sql)
        user = rows[0]
    
    initial_contribution = user['contribution'] or 0
    initial_total = user.get('total_contribution') or 0
    
    print(f"\n[初始状态 - 数据库]")
    print(f"  现有贡献点: {initial_contribution}")
    print(f"  历史总贡献点: {initial_total}")
    
    # 通过仓储获取数据
    member_before = get_member_from_repo(user_id)
    if member_before:
        repo_contribution_before = member_before.contribution or 0
        repo_total_before = getattr(member_before, 'total_contribution', None) or 0
        print(f"\n[初始状态 - 仓储]")
        print(f"  现有贡献点: {repo_contribution_before}")
        print(f"  历史总贡献点: {repo_total_before}")
    
    # 清除今日领取记录
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    
    # 模拟消耗 5 点贡献
    print(f"\n[步骤1] 模拟消耗 5 点贡献（领取火能原石）")
    repo = MySQLAllianceRepo()
    repo.update_member_contribution(user_id, -5)
    
    # 检查数据库中的数据
    db_after = get_member_data(user_id)
    db_contribution_after = db_after['contribution'] or 0
    db_total_after = db_after.get('total_contribution')
    
    print(f"\n[更新后 - 数据库]")
    print(f"  现有贡献点: {db_contribution_after}")
    print(f"  历史总贡献点: {db_total_after} (类型: {type(db_total_after).__name__})")
    
    # 通过仓储获取数据
    member_after = get_member_from_repo(user_id)
    if member_after:
        repo_contribution_after = member_after.contribution or 0
        repo_total_after = getattr(member_after, 'total_contribution', None)
        print(f"\n[更新后 - 仓储]")
        print(f"  现有贡献点: {repo_contribution_after}")
        print(f"  历史总贡献点: {repo_total_after} (类型: {type(repo_total_after).__name__})")
    
    # 验证结果
    expected_contribution = max(0, initial_contribution - 5)
    expected_total = initial_total  # 不应该改变
    
    print(f"\n[验证结果]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    
    # 检查数据库数据
    if db_contribution_after != expected_contribution:
        print(f"  [ERROR] 数据库现有贡献点错误!")
        success = False
    else:
        print(f"  [OK] 数据库现有贡献点正确")
    
    if db_total_after is None:
        print(f"  [WARNING] 数据库历史总贡献点为 NULL!")
        print(f"  [WARNING] 这会导致前端显示时使用 contribution 的值")
        success = False
    elif db_total_after != expected_total:
        print(f"  [ERROR] 数据库历史总贡献点被错误减少!")
        print(f"  [ERROR] 从 {initial_total} 减少到 {db_total_after}")
        success = False
    else:
        print(f"  [OK] 数据库历史总贡献点保持不变")
    
    # 检查仓储数据
    if member_after:
        if repo_total_after is None:
            print(f"  [WARNING] 仓储返回的历史总贡献点为 None!")
            print(f"  [WARNING] 仓储会使用 contribution 作为默认值")
        elif repo_total_after != expected_total:
            print(f"  [ERROR] 仓储返回的历史总贡献点错误!")
            print(f"  [ERROR] 期望: {expected_total}, 实际: {repo_total_after}")
            success = False
    
    return success

if __name__ == "__main__":
    result = test_contribution_issue()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 测试通过！")
    else:
        print("[FAILED] 测试失败！")
        print("\n可能的问题:")
        print("1. total_contribution 字段为 NULL，导致读取时使用 contribution 的值")
        print("2. 数据库触发器没有正确保护 total_contribution")
        print("3. 有其他地方在更新 total_contribution")
    print("=" * 80)
